import argparse
import asyncio
import json
from datetime import datetime, timezone
from typing import Optional, Any

from src.config import prj_configs
from src.api.cexio.cexioNewApi import Api

def pretty(data: Any) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False))


class ApiCli:
    def __init__(self, account_id: str) -> None:
        self.api = Api(
            prj_configs.API_USER,
            prj_configs.API_KEY,
            prj_configs.API_SECRET,
            account_id=account_id,
        )

    # ===== ACCOUNT =====
    async def account_status(self) -> None:
        pretty(await self.api.account_status())

    # ===== MARKET =====
    async def current_prices(self, pair: str) -> None:
        pretty(await self.api.current_prices(pair))

    async def ticker(self, pair: str) -> None:
        res = await self.api.ticker()
        pretty(res.get("data", {}).get(pair, res))

    async def trade_history(self, pair: str) -> None:
        pretty(await self.api.trade_history(pair))

    async def candles(
        self,
        pair: str,
        resolution: str,
        data_type: Optional[str],
        from_iso: Optional[str],
        to_iso: Optional[str],
    ) -> None:
        pretty(

                await self.api.candles(
                    dataType=data_type,
                    pair=pair,
                    resolution=resolution,
                    fromDT=from_iso,
                    toDT=to_iso,
                )
            )

    # ===== ORDERS =====
    async def open_orders(self) -> None:
        pretty(await self.api.open_orders())

    async def get_order(self, order_id: str) -> None:
        pretty(await self.api.get_order(order_id))

    async def cancel_all(self) -> None:
        pretty(await self.api.cancel_all_order())

    # ===== UTILS =====
    def unix_time_ms(self) -> None:
        print(int(datetime.now(timezone.utc).timestamp() * 1000))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser("cex-cli")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("account-status")

    p_prices = sub.add_parser("current-prices")
    p_prices.add_argument("--pair", default="BTC/USD")

    p_ticker = sub.add_parser("ticker")
    p_ticker.add_argument("--pair", default="BTC-USD")

    p_th = sub.add_parser("trade-history")
    p_th.add_argument("--pair", default="BTC-USD")

    p_candles = sub.add_parser("candles")
    p_candles.add_argument("--pair", default="BTC-USD")
    p_candles.add_argument("--resolution", default="1h")
    p_candles.add_argument("--data-type", default=None)
    p_candles.add_argument("--from-iso", default=None)
    p_candles.add_argument("--to-iso", default=None)

    sub.add_parser("open-orders")

    p_go = sub.add_parser("get-order")
    p_go.add_argument("--id", required=True)

    sub.add_parser("cancel-all")
    sub.add_parser("unix-time-ms")

    return parser

async def main(account_id: str, argv: Optional[list[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    cli = ApiCli(account_id=account_id)

    match args.cmd:
        case "account-status":
            await cli.account_status()
        case "current-prices":
            await cli.current_prices(args.pair)
        case "ticker":
            await cli.ticker(args.pair)
        case "trade-history":
            await cli.trade_history(args.pair)
        case "candles":
            await cli.candles(
                pair=args.pair,
                resolution=args.resolution,
                data_type=args.data_type,
                from_iso=args.from_iso,
                to_iso=args.to_iso,
            )
        case "open-orders":
            await cli.open_orders()
        case "get-order":
            await cli.get_order(args.id)
        case "cancel-all":
            await cli.cancel_all()
        case "unix-time-ms":
            cli.unix_time_ms()


if __name__ == "__main__":
    asyncio.run(main(account_id='trade_test'))



# python -m src.manualTrading.traiding_cli account-status
# python -m src.manualTrading.traiding_cli current-prices --pair BTC/USD
# python -m src.manualTrading.traiding_cli ticker --pair BTC-USD
# python -m src.manualTrading.traiding_cli trade-history --pair BTC-USD
# python -m src.manualTrading.traiding_cli candles --pair BTC-USD --resolution 1h --data-type bestAsk
# python -m src.manualTrading.traiding_cli open-orders
# python -m src.manualTrading.traiding_cli get-order --id 189237
# python -m src.manualTrading.traiding_cli cancel-all
# python -m src.manualTrading.traiding_cli unix-time-ms
