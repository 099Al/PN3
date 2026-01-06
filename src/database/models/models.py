from sqlalchemy import (
    String, Integer, Text, DateTime, Boolean, Numeric,
    ForeignKey, Column,
    UniqueConstraint
)

from decimal import Decimal
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
import enum
from sqlalchemy import Enum as SqlEnum

from src.database.models.base import Base
from src.database.models.models_types import SideType, OrderType


class ActiveOrder(Base):
    __tablename__ = 'active_orders'
    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[DateTime] = mapped_column(DateTime)
    unix_date: Mapped[int]
    base: Mapped[str] = mapped_column(String(5), nullable=True)
    quote: Mapped[str] = mapped_column(String(5), nullable=True)
    side: Mapped[SideType] = mapped_column(SqlEnum(SideType), nullable=True,)
    amount: Mapped[Decimal] = mapped_column(Numeric(20, 8))
    price: Mapped[Decimal] = mapped_column(Numeric(20, 4))
    reserved: Mapped[Decimal] = mapped_column(Numeric(20, 4))
    order_type: Mapped[OrderType] = mapped_column(SqlEnum(OrderType), nullable=True)
    full_traid: Mapped[str]
    algo: Mapped[str]
    sys_date: Mapped[DateTime] = mapped_column(DateTime)

    def __repr__(self):
        return f"<ActiveOrder {self.id}> date: {self.date} side: {self.side} amount: {self.amount} price: {self.price}"

class Balance(Base):
    __tablename__ = "balance"

    curr: Mapped[str] = mapped_column(String(5),primary_key=True,)
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 8),nullable=False,default=Decimal("0"),)
    reserved: Mapped[Decimal] = mapped_column(Numeric(15, 8),nullable=False,default=Decimal("0"),)

    def __repr__(self):
        return f"<Balance {self.curr}> amount: {self.amount} reserved: {self.reserved}"

class Exchange(Base):
    __tablename__ = "exchange"

    id:    Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dt:    Mapped[DateTime] = mapped_column(DateTime)
    base:  Mapped[str] = mapped_column(String(5))
    quote: Mapped[str] = mapped_column(String(5))
    bye:   Mapped[Decimal] = mapped_column(Numeric(18, 8))
    sell:  Mapped[Decimal] = mapped_column(Numeric(18, 8))
    bank:  Mapped[str] = mapped_column(String(30))
    descr: Mapped[str] = mapped_column(String(200))

    def __repr__(self):
        return f"<Exchange {self.id}> dt: {self.dt} base: {self.base} quote: {self.quote} bye: {self.bye} sell: {self.sell}"