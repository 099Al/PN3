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
    __table_args__ = {"schema": "emulator"}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    accountId: Mapped[str] = mapped_column(String(50), nullable=True)
    date: Mapped[DateTime] = mapped_column(DateTime)
    unix_date: Mapped[BigInteger] = mapped_column(BigInteger, nullable=False)
    base: Mapped[str] = mapped_column(String(5), nullable=True)
    quote: Mapped[str] = mapped_column(String(5), nullable=True)
    side: Mapped[str] = mapped_column(String(5), nullable=True,)
    amount: Mapped[Decimal] = mapped_column(Numeric(20, 8))
    price: Mapped[Decimal] = mapped_column(Numeric(20, 4))
    reserved: Mapped[Decimal] = mapped_column(Numeric(20, 4))
    order_type: Mapped[str] = mapped_column(String(5), nullable=True)
    #full_traid: Mapped[str] = mapped_column(Text, nullable=True)
    sys_date: Mapped[DateTime] = mapped_column(DateTime, nullable=False)

    def __repr__(self):
        return f"<IM_ActiveOrder {self.id}> date: {self.date} side: {self.side} amount: {self.amount} price: {self.price}"

class Im_Balance(Base):
    __tablename__ = "im_balance"
    __table_args__ = {"schema": "emulator"}

    accountId: Mapped[str] = mapped_column(String(50), nullable=True)
    curr: Mapped[str] = mapped_column(String(5),primary_key=True,)
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 8), nullable=False)
    reserved: Mapped[Decimal] = mapped_column(Numeric(15, 8), nullable=True)

class Im_CexHistoryTik(Base):
    __tablename__ = "im_cex_history_tik"
    __table_args__ = {"schema": "emulator"}

    tid:        Mapped[str] = mapped_column(String(100), primary_key=True)
    unixdate:   Mapped[int] = mapped_column(BigInteger)
    date:       Mapped[DateTime] = mapped_column(DateTime)
    # side:       Mapped[str] = mapped_column(SideTypeEnum)
    side: Mapped[str] = mapped_column(String(6))
    amount:     Mapped[Decimal] = mapped_column(Numeric(11, 8))
    price:      Mapped[Decimal] = mapped_column(Numeric(9, 2))
    trade_data: Mapped[str] = mapped_column(Text, nullable=True)
    accountId: Mapped[str] = mapped_column(String(50), nullable=True)

class ImCexHistoryFileLog(Base):
    __tablename__ = "im_cex_history_file_log"
    __table_args__ = {"schema": "emulator"}

    accountId: Mapped[str] = mapped_column(String(50), nullable=True)
    filename = Column(Text, primary_key=True)
    loaded_at = Column(DateTime(timezone=True), nullable=False)
    file_mtime = Column(BigInteger, nullable=False)
    file_size = Column(BigInteger, nullable=False)

class Im_Stg_CexHistoryTik(Base):
    __tablename__ = "im_stg_cex_history_tik"
    __table_args__ = {"schema": "emulator"}

    tid: Mapped[str] = mapped_column(String(100), primary_key=True)
    unixdate: Mapped[int] = mapped_column(BigInteger)
    date: Mapped[DateTime] = mapped_column(DateTime)
    # side: Mapped[str] = mapped_column(SideTypeEnum)
    side: Mapped[str] = mapped_column(String(6))
    amount: Mapped[Decimal] = mapped_column(Numeric(11, 8))
    price: Mapped[Decimal] = mapped_column(Numeric(9, 2))
    trade_data: Mapped[str] = mapped_column(Text, nullable=True)
    accountId: Mapped[str] = mapped_column(String(50), nullable=True)


class Im_Transaction(Base):
    __tablename__ = "im_transactions"
    __table_args__ = {"schema": "emulator"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # IDs
    transaction_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    order_id: Mapped[int | None] = mapped_column(Integer, index=True)

    # Time
    timestamp: Mapped[DateTime] = mapped_column(DateTime)
    unix_ms: Mapped[int] = mapped_column(BigInteger)

    # Accounting
    type: Mapped[str] = mapped_column(String(20))        # trade | commission | fee | correction
    currency: Mapped[str] = mapped_column(String(10))    # BTC | USD
    amount: Mapped[Decimal] = mapped_column(Numeric(20, 8))  # signed!

    # Meta
    account_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)

