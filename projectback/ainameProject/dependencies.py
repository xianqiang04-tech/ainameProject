from core.mailtools import create_mail_instance
from core.authtools import AuthHandler
from fastapi import Depends, HTTPException
from fastapi_mail import FastMail
from sqlalchemy import select
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

from models.User import User

async def get_email() -> FastMail:
    return create_mail_instance()

from models import AsyncSessionFactory
from sqlalchemy.ext.asyncio.session import AsyncSession

async def get_session():
    session = AsyncSessionFactory()
    try:
        yield session
    finally:
        await session.close()


auth_handler = AuthHandler()


async def get_current_user(
    user_id: int = Depends(auth_handler.auth_access_dependency),
) -> User:
    async with AsyncSessionFactory() as session:
        user = await session.scalar(select(User).where(User.id == user_id))

    if user is None:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="登录用户不存在",
        )
    return user


async def require_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="账号已停用",
        )
    if current_user.role != "admin":
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="需要管理员权限",
        )
    return current_user
