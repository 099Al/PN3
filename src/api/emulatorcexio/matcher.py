from decimal import Decimal
from typing import Optional

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.emulatorcexio.match_requests import Fill, EmulatorMatchRepo
from src.database.connect import DataBase
from src.database.models import ActiveOrder, Balance, Balance_Algo, Im_ActiveOrder, LogDoneTransactions
from src.database.trade_queries.log_helpers import log_order_event, save_balance_algo_snapshot, save_balance_snapshot
from src.trade_utils.date_unix import dt_from_unix_ms, utcnow_dt
from src.trade_utils.util_decimal import D0, D100


def _as_dec(x) -> Decimal:
    return x if isinstance(x, Decimal) else Decimal(str(x))


async def _ensure_balance_row(session: AsyncSession, curr: str) -> None:
    res = await session.execute(select(Balance.curr).where(Balance.curr == curr))
    if res.scalar_one_or_none() is None:
        session.add(
            Balance(
                curr=curr,
                amount=Decimal("0"),
                reserved=Decimal("0"),
                calc_amount=Decimal("0"),
                calc_reserved=Decimal("0"),
            )
        )
        await session.flush()


async def _ensure_balance_algo_row(session: AsyncSession, *, algo: str, curr: str) -> None:
    res = await session.execute(
        select(Balance_Algo.algo).where(Balance_Algo.algo == algo, Balance_Algo.curr == curr)
    )
    if res.scalar_one_or_none() is None:
        session.add(
            Balance_Algo(
                algo=algo,
                curr=curr,
                allocation_limit=Decimal("0"),
                amount=Decimal("0"),
                reserved=Decimal("0"),
            )
        )
        await session.flush()


async def _balance_apply(
    session: AsyncSession,
    *,
    curr: str,
    delta_amount: Decimal = Decimal("0"),
    delta_reserved: Decimal = Decimal("0"),
    delta_calc_amount: Optional[Decimal] = None,
    delta_calc_reserved: Optional[Decimal] = None,
) -> None:
    await _ensure_balance_row(session, curr)

    if delta_calc_amount is None:
        delta_calc_amount = delta_amount
    if delta_calc_reserved is None:
        delta_calc_reserved = delta_reserved

    stmt = (
        update(Balance)
        .where(Balance.curr == curr)
        .values(
            {
                Balance.amount: Balance.amount + delta_amount,
                Balance.reserved: func.coalesce(Balance.reserved, 0) + delta_reserved,
                Balance.calc_amount: func.coalesce(Balance.calc_amount, 0) + delta_calc_amount,
                Balance.calc_reserved: func.coalesce(Balance.calc_reserved, 0) + delta_calc_reserved,
            }
        )
    )
    await session.execute(stmt)


async def _balance_algo_apply(
    session: AsyncSession,
    *,
    algo: str,
    curr: str,
    delta_amount: Decimal = Decimal("0"),
    delta_reserved: Decimal = Decimal("0"),
) -> None:
    if not algo:
        return

    await _ensure_balance_algo_row(session, algo=algo, curr=curr)

    stmt = (
        update(Balance_Algo)
        .where(Balance_Algo.algo == algo, Balance_Algo.curr == curr)
        .values(
            {
                Balance_Algo.amount: Balance_Algo.amount + delta_amount,
                Balance_Algo.reserved: func.coalesce(Balance_Algo.reserved, 0) + delta_reserved,
            }
        )
    )
    await session.execute(stmt)


async def _get_public_order(session: AsyncSession, order_id: int) -> ActiveOrder | None:
    return (
        await session.execute(select(ActiveOrder).where(ActiveOrder.orderId == order_id))
    ).scalars().first()


class OrderMatcher:
    """
    Исполняет лимит-ордера по историческим тикам.
    """

    def __init__(self, repo: EmulatorMatchRepo, *, fee_percent: Decimal = Decimal("0")):
        self.repo = repo
        self.fee_percent = _as_dec(fee_percent)

    def _fee(self, gross: Decimal) -> Decimal:
        if self.fee_percent <= 0:
            return D0
        return gross * self.fee_percent / D100

    async def process_until(self, until_unix_ms: int) -> int:
        filled_count = 0

        with self.repo.session.no_autoflush:
            orders = await self.repo.list_active_orders()

        for order in orders:
            fill = await self.repo.find_fill_for_order(order, until_unix_ms)
            if not fill:
                continue

            await self._fill_order(order, fill)
            filled_count += 1

        return filled_count

    async def _apply_public_fill(
        self,
        *,
        order: Im_ActiveOrder,
        fill: Fill,
        side: str,
        amount_base: Decimal,
        gross_quote: Decimal,
        fee: Decimal,
    ) -> None:
        public_order = await _get_public_order(self.repo.session, order.id)
        algo = public_order.algo if public_order is not None else ""
        public_side = public_order.side if public_order is not None else side.lower()
        public_order_type = public_order.order_type if public_order is not None else "limit"
        public_full_trade = public_order.full_traid if public_order is not None else "{}"
        reserved_public = _as_dec(public_order.reserved) if public_order is not None else _as_dec(order.reserved)

        if side == "SELL":
            await _balance_apply(
                self.repo.session,
                curr=order.base,
                delta_amount=D0,
                delta_reserved=-amount_base,
            )
            await _balance_apply(
                self.repo.session,
                curr=order.quote,
                delta_amount=gross_quote - fee,
                delta_reserved=D0,
            )
            await _balance_algo_apply(
                self.repo.session,
                algo=algo,
                curr=order.base,
                delta_amount=D0,
                delta_reserved=-amount_base,
            )
            await _balance_algo_apply(
                self.repo.session,
                algo=algo,
                curr=order.quote,
                delta_amount=gross_quote - fee,
                delta_reserved=D0,
            )
        else:
            reserved_quote = _as_dec(order.reserved or D0)
            total_quote = gross_quote + fee
            refund = reserved_quote - total_quote
            if refund < D0:
                refund = D0

            await _balance_apply(
                self.repo.session,
                curr=order.quote,
                delta_amount=refund,
                delta_reserved=-reserved_quote,
            )
            await _balance_apply(
                self.repo.session,
                curr=order.base,
                delta_amount=amount_base,
                delta_reserved=D0,
            )
            await _balance_algo_apply(
                self.repo.session,
                algo=algo,
                curr=order.quote,
                delta_amount=refund,
                delta_reserved=-reserved_quote,
            )
            await _balance_algo_apply(
                self.repo.session,
                algo=algo,
                curr=order.base,
                delta_amount=amount_base,
                delta_reserved=D0,
            )

        if public_order is not None:
            await self.repo.session.execute(delete(ActiveOrder).where(ActiveOrder.orderId == public_order.orderId))

        event_date = dt_from_unix_ms(fill.unix_ms)
        await log_order_event(
            self.repo.session,
            status="DONE",
            order_id=order.id,
            side=public_side,
            date=event_date,
            unix_ms=fill.unix_ms,
            base=order.base,
            quote=order.quote,
            amount=_as_dec(order.amount),
            price=_as_dec(order.price),
            reserved=reserved_public,
            fee=fee,
            order_type=public_order_type,
            full_trade=public_full_trade,
            algo=algo,
            flag_reason="EMULATION_DONE",
            event_id=f"{order.id}:DONE",
        )
        await save_balance_snapshot(self.repo.session, order_id=order.id)
        await save_balance_algo_snapshot(self.repo.session, algo_name=algo, order_id=order.id)

    async def _log_done_transactions(
        self,
        *,
        order: Im_ActiveOrder,
        fill: Fill,
        side: str,
        amount_base: Decimal,
        gross_quote: Decimal,
        fee: Decimal,
    ) -> None:
        public_order = await _get_public_order(self.repo.session, order.id)
        algo = public_order.algo if public_order is not None else ""
        log_side = (public_order.side if public_order is not None else side.lower()).lower()
        event_date = dt_from_unix_ms(fill.unix_ms)
        event_unix_s = int(fill.unix_ms // 1000)
        commission_abs = abs(fee)

        trade_rows: list[tuple[str, Decimal, str]] = []
        if side == "SELL":
            trade_rows.append((order.base, -amount_base, f"trade_{order.id}_finalization_{order.base}"))
            trade_rows.append((order.quote, gross_quote, f"trade_{order.id}_finalization_{order.quote}"))
        else:
            trade_rows.append((order.base, amount_base, f"trade_{order.id}_finalization_{order.base}"))
            trade_rows.append((order.quote, -gross_quote, f"trade_{order.id}_finalization_{order.quote}"))

        for curr, amount, tid in trade_rows:
            self.repo.session.add(
                LogDoneTransactions(
                    date=event_date,
                    unix_date=event_unix_s,
                    curr=curr,
                    amount=amount,
                    commission=commission_abs,
                    price=_as_dec(order.price),
                    algo_name=algo,
                    tid=tid,
                    order_side=log_side,
                    sys_date=utcnow_dt(),
                )
            )

    async def _fill_order(self, order: Im_ActiveOrder, fill: Fill) -> None:
        side = str(order.side).upper()
        amount_base = _as_dec(order.amount)
        exec_price = _as_dec(order.price)
        gross_quote = amount_base * exec_price

        if side == "SELL":
            fee = self._fee(gross_quote)
            net_quote = gross_quote - fee

            await self.repo.delete_active_order(order.id)
            await self.repo.apply_balance_delta(account_id=order.accountId, curr=order.base, amount_delta=D0, reserved_delta=-amount_base)
            await self.repo.apply_balance_delta(account_id=order.accountId, curr=order.quote, amount_delta=net_quote, reserved_delta=D0)

            order_id = order.id
            details_trade = f"Finalization Trade orderId='{order_id}' for {self.repo.session.info.get('user', 'EMULATOR')}"
            details_fee = f"Commission for orderId='{order_id}' for {self.repo.session.info.get('user', 'EMULATOR')}"

            await self.repo.add_transaction(
                transaction_id=f"trade_{order_id}_finalization_{order.base}",
                order_id=order_id,
                unix_ms=fill.unix_ms,
                type="trade",
                currency=order.base,
                amount=-amount_base,
                details=details_trade,
            )
            await self.repo.add_transaction(
                transaction_id=f"trade_{order_id}_finalization_{order.quote}",
                order_id=order_id,
                unix_ms=fill.unix_ms,
                type="trade",
                currency=order.quote,
                amount=gross_quote,
                details=details_trade,
            )
            if fee != D0:
                await self.repo.add_transaction(
                    transaction_id=f"commission_trade_{order_id}",
                    order_id=order_id,
                    unix_ms=fill.unix_ms + 12,
                    type="commission",
                    currency=order.quote,
                    amount=-fee,
                    details=details_fee,
                )

        elif side == "BUY":
            fee = self._fee(gross_quote)
            total_quote = gross_quote + fee

            await self.repo.delete_active_order(order.id)

            reserved_quote = _as_dec(order.reserved or D0)
            refund = reserved_quote - total_quote
            if refund < D0:
                refund = D0

            await self.repo.apply_balance_delta(account_id=order.accountId, curr=order.quote, amount_delta=refund, reserved_delta=-reserved_quote)
            await self.repo.apply_balance_delta(account_id=order.accountId, curr=order.base, amount_delta=amount_base, reserved_delta=D0)

            order_id = order.id
            details_trade = f"Finalization Trade orderId='{order_id}' for {self.repo.session.info.get('user', 'EMULATOR')}"
            details_fee = f"Commission for orderId='{order_id}' for {self.repo.session.info.get('user', 'EMULATOR')}"

            await self.repo.add_transaction(
                transaction_id=f"trade_{order_id}_finalization_{order.base}",
                order_id=order_id,
                unix_ms=fill.unix_ms,
                type="trade",
                currency=order.base,
                amount=amount_base,
                details=details_trade,
            )
            await self.repo.add_transaction(
                transaction_id=f"trade_{order_id}_finalization_{order.quote}",
                order_id=order_id,
                unix_ms=fill.unix_ms,
                type="trade",
                currency=order.quote,
                amount=-gross_quote,
                details=details_trade,
            )
            if fee != D0:
                await self.repo.add_transaction(
                    transaction_id=f"commission_trade_{order_id}",
                    order_id=order_id,
                    unix_ms=fill.unix_ms + 12,
                    type="commission",
                    currency=order.quote,
                    amount=-fee,
                    details=details_fee,
                )
        else:
            raise ValueError(f"Unknown order side: {order.side}")

        await self._log_done_transactions(
            order=order,
            fill=fill,
            side=side,
            amount_base=amount_base,
            gross_quote=gross_quote,
            fee=fee,
        )
        await self._apply_public_fill(
            order=order,
            fill=fill,
            side=side,
            amount_base=amount_base,
            gross_quote=gross_quote,
            fee=fee,
        )


async def emulation_check_orders(unix_ms: int) -> None:
    db = DataBase()
    async with db.get_session_maker()() as session:
        repo = EmulatorMatchRepo(session)
        matcher = OrderMatcher(repo, fee_percent=Decimal("0.0"))
        await matcher.process_until(unix_ms)
        await session.commit()
