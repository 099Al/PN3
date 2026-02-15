from decimal import Decimal
from typing import Optional

from src.api.emulatorcexio.match_requests import Fill, EmulatorMatchRepo
from src.database.connect import DataBase
from src.database.models import Im_ActiveOrder
from src.trade_utils.util_decimal import D0, D100


def _as_dec(x) -> Decimal:
    return x if isinstance(x, Decimal) else Decimal(str(x))

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
        return (gross * self.fee_percent / D100)

    async def process_until(self, until_unix_ms: int) -> int:
        """
        Возвращает кол-во исполненных ордеров.
        """
        filled_count = 0

        # Чтобы autoflush не сработал "раньше времени" во время SELECT:
        async with self.repo.session.no_autoflush:
            orders = await self.repo.list_active_orders()

        for order in orders:
            fill = await self.repo.find_fill_for_order(order, until_unix_ms)
            if not fill:
                continue

            await self._fill_order(order, fill)
            filled_count += 1

        return filled_count

    async def _fill_order(self, order: Im_ActiveOrder, fill: Fill) -> None:
        """
        Полное исполнение.
        Движение баланса + записи транзакций.
        """
        side = str(order.side).upper()
        base = order.base
        quote = order.quote
        amount_base = _as_dec(order.amount)

        # В примере ты хочешь "если цена удовлетворила условию" — будем исполнять по цене ордера (limit price)
        # Можно исполнить по fill.price, если хочешь "по рынку".
        exec_price = _as_dec(order.price)

        gross_quote = amount_base * exec_price

        if side == "SELL":
            fee = self._fee(gross_quote)
            net_quote = gross_quote - fee

            # 1) снять ордер
            await self.repo.delete_active_order(order.id)

            # 2) баланс:
            # В момент выставления SELL ты резервировал base: amount -> reserved
            # Теперь: reserved(base) -= amount; amount(quote) += net_quote
            await self.repo.apply_balance_delta(curr=base, amount_delta=D0, reserved_delta=-amount_base)
            await self.repo.apply_balance_delta(curr=quote, amount_delta=net_quote, reserved_delta=D0)

            # 3) транзакции (как в примере, но для SELL будет -BTC, +USD, -USD fee)
            order_id = order.id
            details_trade = f"Finalization Trade orderId='{order_id}' for {self.repo.session.info.get('user', 'EMULATOR')}"
            details_fee = f"Commission for orderId='{order_id}' for {self.repo.session.info.get('user', 'EMULATOR')}"

            await self.repo.add_transaction(
                transaction_id=f"trade_{order_id}_finalization_{base}",
                order_id=order_id,
                unix_ms=fill.unix_ms,
                type="trade",
                currency=base,
                amount=-amount_base,
                details=details_trade,
            )
            await self.repo.add_transaction(
                transaction_id=f"trade_{order_id}_finalization_{quote}",
                order_id=order_id,
                unix_ms=fill.unix_ms,
                type="trade",
                currency=quote,
                amount=gross_quote,  # приход "грязными"
                details=details_trade,
            )
            if fee != D0:
                await self.repo.add_transaction(
                    transaction_id=f"commission_trade_{order_id}",
                    order_id=order_id,
                    unix_ms=fill.unix_ms + 12,  # чуть позже, как в реальных логах
                    type="commission",
                    currency=quote,
                    amount=-fee,
                    details=details_fee,
                )

        elif side == "BUY":
            fee = self._fee(gross_quote)
            total_quote = gross_quote + fee

            # 1) снять ордер
            await self.repo.delete_active_order(order.id)

            # 2) баланс:
            # В момент выставления BUY резервировал quote: reserved(quote) += reserved, amount(quote) -= reserved
            # Сейчас считаем фактическую трату total_quote и делаем:
            # reserved(quote) -= total_quote; amount(base) += amount_base
            # Если в order.reserved было "с запасом" — можно вернуть остаток в amount(quote)
            reserved_quote = _as_dec(order.reserved or D0)
            refund = reserved_quote - total_quote
            if refund < D0:
                # на всякий случай: если логика резервирования была другой
                refund = D0

            await self.repo.apply_balance_delta(account_id=order.accountId, curr=quote, amount_delta=refund, reserved_delta=-reserved_quote)  # снимаем весь резерв
            # затем "платим" фактическую сумму из amount (так проще понять):
            # но поскольку мы уже сняли reserved целиком, корректнее прямо отразить итог:
            # amount уже уменьшили при постановке ордера. Здесь надо только вернуть refund (если есть).
            # И добавить base:
            await self.repo.apply_balance_delta(account_id=order.accountId, curr=base, amount_delta=amount_base, reserved_delta=D0)

            # 3) транзакции (как в примере: +BTC, -USD, -USD fee)
            order_id = order.id
            details_trade = f"Finalization Trade orderId='{order_id}' for {self.repo.session.info.get('user', 'EMULATOR')}"
            details_fee = f"Commission for orderId='{order_id}' for {self.repo.session.info.get('user', 'EMULATOR')}"

            await self.repo.add_transaction(
                transaction_id=f"trade_{order_id}_finalization_{base}",
                order_id=order_id,
                unix_ms=fill.unix_ms,
                type="trade",
                currency=base,
                amount=amount_base,
                details=details_trade,
            )
            await self.repo.add_transaction(
                transaction_id=f"trade_{order_id}_finalization_{quote}",
                order_id=order_id,
                unix_ms=fill.unix_ms,
                type="trade",
                currency=quote,
                amount=-gross_quote,
                details=details_trade,
            )
            if fee != D0:
                await self.repo.add_transaction(
                    transaction_id=f"commission_trade_{order_id}",
                    order_id=order_id,
                    unix_ms=fill.unix_ms + 12,
                    type="commission",
                    currency=quote,
                    amount=-fee,
                    details=details_fee,
                )

        else:
            raise ValueError(f"Unknown order side: {order.side}")



async def emulation_check_orders(unix_ms: int) -> None:
    db = DataBase()
    async with db.get_session_maker()() as session:
        repo = EmulatorMatchRepo(session)
        matcher = OrderMatcher(repo, fee_percent=Decimal("0.0"))  # или твоя комиссия

        filled = await matcher.process_until(unix_ms)
        await session.commit()