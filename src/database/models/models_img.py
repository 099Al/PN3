from typing import List

from sqlalchemy import (
    String, Integer, Text, DateTime, Boolean, Numeric,
    ForeignKey, Column,
    UniqueConstraint, BigInteger
)

from decimal import Decimal
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
import enum
from sqlalchemy import Enum as SqlEnum

from src.database.models.models_types import SideTypeEnum, OrderTypeEnum
from src.database.models.base import Base



class Im_ActiveOrder(Base):
    __tablename__ = 'im_active_orders'
    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[DateTime] = mapped_column(DateTime)
    unix_date: Mapped[int]
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
        return f"<IM_ActiveOrder {self.id}> date: {self.date} side: {self.side} amount: {self.amount} price: {self.price}"

class Im_Balance(Base):
    __tablename__ = "im_balance"

    curr: Mapped[str] = mapped_column(String(5),primary_key=True,)
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 8),nullable=False,default=Decimal("0"),)
    reserved: Mapped[Decimal] = mapped_column(Numeric(15, 8),nullable=False,default=Decimal("0"),)

class Im_CexHistoryTik(Base):
    __tablename__ = "im_cex_history_tik"

    tid:        Mapped[int] = mapped_column(BigInteger, primary_key=True)
    type:       Mapped[str] = mapped_column(String(6))
    unixdate:   Mapped[int] = mapped_column(BigInteger)
    date:       Mapped[DateTime] = mapped_column(DateTime)
    amount:     Mapped[Decimal] = mapped_column(Numeric(11, 8))
    price:      Mapped[Decimal] = mapped_column(Numeric(9, 2))
    sys_insert: Mapped[DateTime] = mapped_column(DateTime)

class Im_Stg_CexHistoryTik(Base):
    __tablename__ = "im_stg_cex_history_tik"

    tid:        Mapped[int] = mapped_column(BigInteger, primary_key=True)
    type:       Mapped[str] = mapped_column(String(6))
    unixdate:   Mapped[int] = mapped_column(BigInteger)
    date:       Mapped[DateTime] = mapped_column(DateTime)
    amount:     Mapped[Decimal] = mapped_column(Numeric(11, 8))
    price:      Mapped[Decimal] = mapped_column(Numeric(9, 2))
    sys_insert: Mapped[DateTime] = mapped_column(DateTime)


class Im_Transactions(Base):
    __tablename__ = "im_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(Integer)
    order_amount: Mapped[Decimal] = mapped_column(Numeric(11, 8))
    order_price: Mapped[Decimal] = mapped_column(Numeric(9, 2))
    order_reserved: Mapped[Decimal] = mapped_column(Numeric(20, 4))
    order_side: Mapped[str] = mapped_column(String(6))
    tid: Mapped[int] = mapped_column(BigInteger)
    unixdate: Mapped[int] = mapped_column(BigInteger)
    date: Mapped[DateTime] = mapped_column(DateTime)
    transact_info: Mapped[str] = mapped_column(Text)
