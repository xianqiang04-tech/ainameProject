from datetime import datetime
from decimal import Decimal
from sqlalchemy import Integer, String, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from . import Base

class UserOrder(Base):
    __tablename__ = 'user_order'
    id: Mapped[int] = mapped_column(Integer, primary_key=True,autoincrement=True)
    order_no: Mapped[str] = mapped_column(String(100),unique=True,index=True,nullable=False)
    user_id: Mapped[int] = mapped_column(Integer,ForeignKey("user.id"),nullable=False)
    package_id: Mapped[int] = mapped_column(Integer,ForeignKey("package.id"),nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10,2),nullable=False)
    credit_count: Mapped[int] = mapped_column(Integer,nullable=False)
    status: Mapped[str] = mapped_column(String(100),default="pending",nullable=False)
    alipay_trade_no: Mapped[str] = mapped_column(String(100),nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime,default=datetime.now(),nullable=False)
    paid_at: Mapped[datetime] = mapped_column(DateTime,nullable=True)