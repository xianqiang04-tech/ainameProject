from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from dependencies import get_session
from repository.package_repo import PackageRepository
from schemas.package_schemas import PackageOut

router = APIRouter(prefix="/package")

@router.get("/list", response_model=list[PackageOut])
async def package_list(
        type: str = None,
        session: AsyncSession = Depends(get_session),
):
    package_repo = PackageRepository(session=session)
    packages = await package_repo.get_all_packages(package_type=type)
    return packages

@router.get("/package/{package_id}")
async def get_package_id(
        package_id: int,
        session: AsyncSession = Depends(get_session)
):
    package_repo = PackageRepository(session=session)
    package = await package_repo.get_package_by_id(package_id)

    if not package:
        raise HTTPException(status_code=404, detail="Package not found")
    return package

