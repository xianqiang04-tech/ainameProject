import password
from . import Base
from sqlalchemy.orm import mapped_column,Mapped
from sqlalchemy import Boolean, DateTime, Integer, String, func
from pwdlib import PasswordHash
from datetime import datetime
password_hash = PasswordHash.recommended()

class User(Base):
    __tablename__ = 'user'
    id:Mapped[int] = mapped_column(Integer,primary_key=True,autoincrement=True)
    email:Mapped[String] = mapped_column(String(100),unique=True)
    username:Mapped[String] = mapped_column(String(100))
    _password:Mapped[String] = mapped_column(String(200))
    role: Mapped[str] = mapped_column(
        String(20), default="user", server_default="user", nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default="true", nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, server_default=func.now(), nullable=False
    )
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # 密码初始化的时机  *args 能接收所有按照位置传递的参数，形成一个列表
    # **kwargs 能接受所有名称绑定的参数 , key=value , 形成一个字典
    def __init__(self,*args,**kwargs):
        password = kwargs.pop('password',None)
        super().__init__(*args, **kwargs)
        if password:
            self.password = password

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self,password):
        self._password = password_hash.hash(password)

    def check_password(self,password):
        return password_hash.verify(password,self._password)
