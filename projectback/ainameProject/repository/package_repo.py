from sqlalchemy import select
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from models.package import Package

class PackageRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # 获取全部套餐（可按类型过滤：name=起名套餐 / logo=Logo次数包）
    async def get_all_packages(self, package_type: str = None) -> List[Package]:
        async with self.session.begin():
            stmt = select(Package).where(Package.is_active == True)
            if package_type:
                stmt = stmt.where(Package.type == package_type)
            result = await self.session.scalars(stmt)
            return list(result.all())

    # 根据ID获取套餐
    async def get_package_by_id(self, package_id: int) -> Package:
        async with self.session.begin():
            result = await self.session.scalar(select(Package).where(Package.id == package_id))
            return result
