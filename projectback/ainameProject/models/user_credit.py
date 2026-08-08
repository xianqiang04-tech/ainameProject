from datetime import datetime
from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, MappedColumn
from . import Base

class UserCredit(Base):
    __tablename__ = "user_credit"
    id:Mapped[int] = MappedColumn(Integer,primary_key=True,autoincrement=True)
    user_id:Mapped[int] = MappedColumn(Integer,ForeignKey("user.id"),unique=True,nullable=False,index=True)
    balance:Mapped[int] = MappedColumn(Integer,default=0,nullable=False)
    total_used:Mapped[int] = MappedColumn(Integer,default=0,nullable=False)
    total_recharged:Mapped[int] = MappedColumn(Integer,default=0,nullable=False)
    created_at:Mapped[datetime] = MappedColumn(DateTime,default=datetime.now,nullable=False)
    updated_at:Mapped[datetime] = MappedColumn(DateTime,default=datetime.now,onupdate=datetime.now,nullable=False)

class CreditLog(Base):
    __tablename__ = "credit_log"
    id:Mapped[int] = MappedColumn(Integer,primary_key=True,autoincrement=True)
    user_id:Mapped[int] = MappedColumn(Integer,ForeignKey("user.id"),nullable=False,index=True)
    change_count:Mapped[int] = MappedColumn(Integer,default=0,nullable=False)
    balance_after:Mapped[int] = MappedColumn(Integer,default=0,nullable=False)
    type:Mapped[str] = MappedColumn(String(200))
    remark:Mapped[str] = MappedColumn(String(200),nullable=True)
    created_at:Mapped[datetime] = MappedColumn(DateTime,default=datetime.now,nullable=False)