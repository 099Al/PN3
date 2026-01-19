from sqlalchemy import (
    String, Integer, Text, DateTime, Boolean, Numeric,
    ForeignKey, Column,
    UniqueConstraint, BigInteger, PrimaryKeyConstraint
)

from decimal import Decimal
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
import enum
from sqlalchemy import Enum as SqlEnum

from src.database.models.models_types import OrderTypeEnum, ActivityTypeEnum, SideTypeEnum, OrderStatusTypeEnum
from src.database.models.base import Base


class ActiveOrder(Base):
    __tablename__ = 'active_orders'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    date: Mapped[DateTime] = mapped_column(DateTime)
    unix_date: Mapped[BigInteger] = mapped_column(BigInteger, nullable=False)
    base: Mapped[str] = mapped_column(String(5), nullable=True)
    quote: Mapped[str] = mapped_column(String(5), nullable=True)
    side: Mapped[str] = mapped_column(SideTypeEnum, nullable=True,)
    amount: Mapped[Decimal] = mapped_column(Numeric(20, 8))
    price: Mapped[Decimal] = mapped_column(Numeric(20, 4))
    reserved: Mapped[Decimal] = mapped_column(Numeric(20, 4))
    order_type: Mapped[str] = mapped_column(OrderTypeEnum, nullable=True)
    full_traid: Mapped[str]
    algo: Mapped[str]
    sys_date: Mapped[DateTime] = mapped_column(DateTime)

    def __repr__(self):
        return f"<ActiveOrder {self.id}> date: {self.date} side: {self.side} amount: {self.amount} price: {self.price}"

class Balance(Base):
    __tablename__ = "balance"

    curr: Mapped[str] = mapped_column(String(5), primary_key=True,)
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 8), nullable=False, default=Decimal("0"),)
    reserved: Mapped[Decimal] = mapped_column(Numeric(15, 8), nullable=True)

class Balance_Algo(Base):
    __tablename__ = "balance_algo"

    algo: Mapped[str] = mapped_column(String(20), primary_key=True,)
    curr: Mapped[str] = mapped_column(String(5), primary_key=True, )
    amount_limit: Mapped[Decimal] = mapped_column(Numeric(15, 8), nullable=False, default=Decimal("0"), )
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 8), nullable=False, default=Decimal("0"), )
    reserved: Mapped[Decimal] = mapped_column(Numeric(15, 8), nullable=True)

    def __repr__(self):
        return f"<Balance Algo{self.curr}> amount: {self.amount} reserved: {self.reserved}"

class Exchange(Base):
    __tablename__ = "exchange"

    id:    Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dt:    Mapped[DateTime] = mapped_column(DateTime)
    base:  Mapped[str] = mapped_column(String(5))
    quote: Mapped[str] = mapped_column(String(5))
    bye:   Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=True)
    sell:  Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=True)
    bank:  Mapped[str] = mapped_column(String(30))
    descr: Mapped[str] = mapped_column(String(200), nullable=True)

    def __repr__(self):
        return f"<Exchange {self.id}> dt: {self.dt} base: {self.base} quote: {self.quote} bye: {self.bye} sell: {self.sell}"

class CexHistoryTik(Base):
    __tablename__ = "cex_history_tik"

    tid:        Mapped[str] = mapped_column(String(100), primary_key=True)
    type:       Mapped[str] = mapped_column(String(6))
    unixdate:   Mapped[int] = mapped_column(BigInteger)
    date:       Mapped[DateTime] = mapped_column(DateTime)
    amount:     Mapped[Decimal] = mapped_column(Numeric(11, 8))
    price:      Mapped[Decimal] = mapped_column(Numeric(9, 2))
    sys_insert: Mapped[DateTime] = mapped_column(DateTime)

class Stg_CexHistoryTik(Base):
    __tablename__ = "stg_cex_history_tik"

    tid:        Mapped[str] = mapped_column(String(100), primary_key=True)
    type:       Mapped[str] = mapped_column(String(6))
    unixdate:   Mapped[int] = mapped_column(BigInteger)
    date:       Mapped[DateTime] = mapped_column(DateTime)
    amount:     Mapped[Decimal] = mapped_column(Numeric(11, 8))
    price:      Mapped[Decimal] = mapped_column(Numeric(9, 2))
    sys_insert: Mapped[DateTime] = mapped_column(DateTime)

class DayHLV(Base):
    __tablename__ = "dayHLV"
    __table_args__ = (PrimaryKeyConstraint("date_d", "pair_id", name="pk_dayhlv"),)

    date_d:  Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    pair_id: Mapped[int] = mapped_column(Integer, ForeignKey("pairs.pair_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    high:    Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)
    low:     Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)
    vol:     Mapped[Decimal] = mapped_column(Numeric(13, 3), nullable=False)
    capital: Mapped[Decimal] = mapped_column(Numeric(15, 3))

class DepositFee(Base):
    __tablename__ = "deposit_fee"

    id:             Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    curr:           Mapped[str] = mapped_column(String(5))
    method:         Mapped[str] = mapped_column(String(15))
    deposit:        Mapped[Decimal] = mapped_column(Numeric)
    deposit_fix:    Mapped[Decimal] = mapped_column(Numeric)
    withdrawal:     Mapped[Decimal] = mapped_column(Numeric)
    withdrawal_fix: Mapped[Decimal] = mapped_column(Numeric)
    descr:          Mapped[str] = mapped_column(String, nullable=True)




class LogBalance(Base):
    __tablename__ = "log_balance"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[DateTime] = mapped_column(DateTime)
    unix_date: Mapped[int] = mapped_column(Integer)
    curr: Mapped[str] = mapped_column(String(5))
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 8))
    algo_name: Mapped[str] = mapped_column(String(20))
    tid: Mapped[str] = mapped_column(String(30))
    activity: Mapped[str] = mapped_column(ActivityTypeEnum)
    sys_date: Mapped[DateTime] = mapped_column(DateTime)


class LogOrders(Base):
    __tablename__ = "log_orders"

    status: Mapped[str] = mapped_column(OrderStatusTypeEnum)
    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    side: Mapped[str] = mapped_column(SideTypeEnum)
    date: Mapped[DateTime] = mapped_column(DateTime)
    unixdate: Mapped[int] = mapped_column(Integer)
    base: Mapped[str] = mapped_column(String(5))
    quote: Mapped[str] = mapped_column(String(5))
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 8))
    price: Mapped[Decimal] = mapped_column(Numeric(15, 8))
    reserved: Mapped[Decimal] = mapped_column(Numeric(15, 8))
    fee: Mapped[Decimal] = mapped_column(Numeric(15, 2))
    reject_reason: Mapped[str] = mapped_column(Text, nullable=True)
    order_type: Mapped[str] = mapped_column(OrderTypeEnum, nullable=False)
    expire: Mapped[int] = mapped_column(Integer, nullable=False)
    full_traid: Mapped[str] = mapped_column(Text, nullable=False)
    algo: Mapped[str] = mapped_column(String(20), nullable=False)
    flag_reason: Mapped[str] = mapped_column(Text, nullable=True)

class MakerTaker(Base):
    __tablename__ = "maker_taker"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    vol30d: Mapped[int] = mapped_column(Integer, nullable=False)
    maker: Mapped[Decimal] = mapped_column(Numeric)
    taker: Mapped[Decimal] = mapped_column(Numeric)
    descr: Mapped[str] = mapped_column(String, nullable=True)

class Pairs(Base):
    __tablename__ = "pairs"

    pair_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    pair: Mapped[str] = mapped_column(String(30), nullable=False)


class Trade_Parameters(Base):
    __tablename__ = "trade_parameters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(30), nullable=False)
    value: Mapped[str] = mapped_column(String(30), nullable=False)
    category: Mapped[str] = mapped_column(String(30), nullable=True)
    v_type: Mapped[str] = mapped_column(String(30), nullable=True)
    descr: Mapped[str] = mapped_column(String, nullable=True)