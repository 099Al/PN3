from typing import List

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

from src.database.models import SideType, OrderType
from src.database.models.base import Base



class Im_ActiveOrder(Base):
    __tablename__ = 'im_active_orders'
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
        return f"<IM_ActiveOrder {self.id}> date: {self.date} side: {self.side} amount: {self.amount} price: {self.price}"

class Im_Balance(Base):
    __tablename__ = "im_balance"

    curr: Mapped[str] = mapped_column(String(5),primary_key=True,)
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 8),nullable=False,default=Decimal("0"),)
    reserved: Mapped[Decimal] = mapped_column(Numeric(15, 8),nullable=False,default=Decimal("0"),)
