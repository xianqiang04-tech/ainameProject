import argparse
import asyncio
import sys

from pydantic import ValidationError
from sqlalchemy import select

from models import AsyncSessionFactory, engine
from models.User import User
from schemas.user_schemas import UserCreateSchema


async def create_admin(username: str, email: str, password: str) -> User:
    validated = UserCreateSchema(
        username=username,
        email=email,
        password=password,
    )

    async with AsyncSessionFactory() as session:
        async with session.begin():
            existing = await session.scalar(select(User).where(User.email == email))
            if existing is not None:
                raise ValueError(f"邮箱 {email} 已存在，未覆盖原账号")

            admin = User(
                username=validated.username,
                email=str(validated.email),
                password=validated.password,
                role="admin",
                is_active=True,
            )
            session.add(admin)
            await session.flush()
        return admin


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="创建一个初始管理员账号")
    parser.add_argument("--username", required=True)
    parser.add_argument("--email", required=True)
    parser.add_argument("--password", required=True)
    return parser.parse_args()


async def async_main() -> int:
    args = parse_args()
    try:
        admin = await create_admin(args.username, args.email, args.password)
    except (ValidationError, ValueError) as exc:
        print(f"创建失败：{exc}", file=sys.stderr)
        return 1
    finally:
        await engine.dispose()

    print(f"管理员创建成功：id={admin.id}, email={admin.email}")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(async_main()))
