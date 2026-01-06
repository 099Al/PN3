from typing import List

from sqlalchemy import (
    String, Integer, Text, DateTime, Boolean, Decimal,
    ForeignKey, Column,
    UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
import enum
from sqlalchemy import Enum as SqlEnum

from src.database.models.base import Base


class SideType(enum.Enum):
    BUE = "buy"
    SELL = "sell"

class OrderType(enum.Enum):
    LIMIT = "limit"
    MARKET = "market"


class ActiveOrder(BaseModel):
    __tablename__ = 'active_orders'
    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[DateTime] = mapped_column(DateTime)
    unix_date: Optional[int]
    base: Mapped[str] = mapped_column(String(5), nullable=True)
    quote: Mapped[str] = mapped_column(String(5), nullable=True)
    side: Mapped[SideType] = mapped_column(SqlEnum(SideType), nullable=True,)
    amount: Mapped[Decimal] = mapped_column(Numeric(20, 8))
    price: Mapped[Decimal] = mapped_column(Numeric(20, 4))
    reserved: Mapped[Decimal] = mapped_column(Numeric(20, 4))
    order_type: Mapped[OrderType] = mapped_column(SqlEnum(OrderType), nullable=True)
    full_traid: Optional[str]
    algo: Optional[str]
    sys_date: Mapped[DateTime] = mapped_column(DateTime)

    def __repr__(self):
        return f"<ActiveOrder {self.id}> date: {self.date} side: {self.side} amount: {self.amount} price: {self.price}"
