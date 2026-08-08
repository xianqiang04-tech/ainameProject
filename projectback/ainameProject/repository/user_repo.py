from sqlalchemy import select,exists
from sqlalchemy.ext.asyncio.session import AsyncSession
from models.User import User
from schemas.user_schemas import UserCreateSchema

class UserRepository:
    def __init__(self,session:AsyncSession):
        self.session = session

    async def get_user_by_email(self,email:str):
        async with self.session.begin():
            return await self.session.scalar(select(User).where(User.email == email))

    async def email_is_exist(self,email:str):
        async with self.session.begin():
            stmt = select(exists().where(User.email == email))
            return await self.session.scalar(stmt)

    async def create(self,user_schema:UserCreateSchema):
        async with self.session.begin():
            user = User(**user_schema.model_dump())
            self.session.add(user)
            await self.session.flush()
            return user