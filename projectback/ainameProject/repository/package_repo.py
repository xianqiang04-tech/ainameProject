from sqlalchemy import select
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from models.package import Package

class PackageRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # 获取全部套餐
    async def get_all_packages(self) -> List[Package]:
        async with self.session.begin():
            result = await self.session.scalars(select(Package).where(Package.is_active == True))
            return list(result.all())

    # 根据ID获取套餐
    async def get_package_by_id(self, package_id: int) -> Package:
        async with self.session.begin():
            result = await self.session.scalar(select(Package).where(Package.id == package_id))
            return result
