import random
import string
from datetime import datetime
from typing import Annotated
from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import EmailStr
from fastapi_mail import FastMail, MessageSchema, MessageType
# 如果你用的是 fastapi-mail，建议用 aiosmtplib 的异常
from aiosmtplib.errors import SMTPException, SMTPResponseException
from core.redistools import get_redis
# 下面这几个路径按你项目实际位置改
from dependencies import get_email
from repository.user_repo import UserRepository
from repository.credit_repo import CreditRepository
from redis.asyncio import Redis
from core.redistools import get_redis
from fastapi import Depends, HTTPException

# from schemas import ResponseOut

router = APIRouter(prefix="/auth", tags=["email"])

@router.get("/code")
async def getcode(email:Annotated[EmailStr,Query(...)],
                  mail:FastMail=Depends(get_email),
                  redisclient:Redis=Depends(get_redis)):
    # 1.生成验证码
    source = string.digits*4
    code = "".join(random.sample(source,4))

    # 2.发送邮件给用户
    message = MessageSchema(
        subject="【智能起名平台】注册验证码",
        recipients=[email],
        body=f"您的验证码是:{code},五分钟内有效",
        subtype=MessageType.plain,
    )
    await mail.send_message(message)

    # 3.存入redis
    await redisclient.set(f"regist:code:{email}",code,300)
    return {"result":"success","message":"验证码已成功发送至您的邮箱"}

# 用户注册功能
from schemas.user_schemas import RegisterIn, UserCreateSchema
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy import select
from dependencies import get_session

# 1.接收用户传过来的参数:用户名(一般情况下:邮箱/手机号),密码,验证吗
@router.post("/register")
async def register(data:RegisterIn,
                   session:AsyncSession=Depends(get_session),
                   redisclient:Redis=Depends(get_redis)):

    # 2.验证参数(redis)
    # 2.1 邮箱，数据库查询,看看这个邮箱是否被注册。没被注册，可以，已经注册，告诉用户可以直接登录
    userrepo = UserRepository(session)
    email_is_exist = await userrepo.email_is_exist(data.email)
    if email_is_exist:
        raise HTTPException(status_code=400,detail="该邮箱已经存在，请直接登录")
    # 2.2 验证码
    redis_key = f"regist:code:{data.email}"
    save_code = await redisclient.get(redis_key)
    if not save_code:
        raise HTTPException(400,"验证码不存在，或已经过期")
    if save_code != data.code:
        raise HTTPException(400,"验证码输入错误，请注意核对")

    # 3.注册:向数据库插入一条数据(用户信息)
    usermodel = UserCreateSchema(email=data.email,password=data.password,username=data.username)
    user: User = await userrepo.create(usermodel)

    # 创建账户，并赠送3次使用次数
    creditRepository = CreditRepository(session)
    await creditRepository.create_register_credit(user_id=user.id,gift_count=3)

    await redisclient.delete(redis_key)
    return {"message":"恭喜您注册成功"}

from schemas.user_schemas import LoginIn,LoginoutSchema
from models.User import User
from core.authtools import AuthHandler

auth_handler = AuthHandler()
# 登陆时一般接收用户名和密码
@router.post("/login",response_model=LoginoutSchema)
async def login(loginInfo:LoginIn,
                session:AsyncSession=Depends(get_session)):
    async with session.begin():
        user: User | None = await session.scalar(
            select(User).where(User.email == loginInfo.email)
        )
        if not user:
            raise HTTPException(status_code=400,detail="该用户不存在")

        if not user.check_password(loginInfo.password):
            raise HTTPException(status_code=400,detail="密码错误，请重新输入")

        if not user.is_active:
            raise HTTPException(status_code=403, detail="账号已停用")

        user.last_login_at = datetime.now()

    # 3.生成JWT token,返回
    tokens = auth_handler.encode_login_token(user_id=user.id)
    return{
        "user":user,
        "access_token":tokens["access_token"],
        "refresh_token":tokens["refresh_token"]
    }
