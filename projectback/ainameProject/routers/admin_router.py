from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_session, require_admin_user
from models.User import User
from schemas.admin_schemas import AdminAuditLogOut, AdminMeOut
from schemas.admin_schemas import AdminOrderOut, AdminPackageCreateIn
from schemas.admin_schemas import AdminPackageOut, AdminPackageUpdateIn
from schemas.admin_schemas import AdminUserDetailOut, AdminUserListItemOut
from schemas.admin_schemas import CreditAdjustIn, CreditAdjustOut, DashboardOut
from schemas.admin_schemas import PageOut, UserStatusOut, UserStatusUpdateIn
from services.admin_service import AdminService


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/me", response_model=AdminMeOut)
async def get_admin_me(
    admin: User = Depends(require_admin_user),
):
    return admin


@router.get("/dashboard", response_model=DashboardOut)
async def get_dashboard(
    _: User = Depends(require_admin_user),
    session: AsyncSession = Depends(get_session),
):
    return await AdminService(session).dashboard()


@router.get("/users", response_model=PageOut[AdminUserListItemOut])
async def list_users(
    keyword: str | None = Query(default=None, max_length=100),
    is_active: bool | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    _: User = Depends(require_admin_user),
    session: AsyncSession = Depends(get_session),
):
    items, total = await AdminService(session).list_users(
        keyword=keyword,
        is_active=is_active,
        page=page,
        page_size=page_size,
    )
    return PageOut(items=items, total=total, page=page, page_size=page_size)


@router.get("/users/{user_id}", response_model=AdminUserDetailOut)
async def get_user_detail(
    user_id: int,
    _: User = Depends(require_admin_user),
    session: AsyncSession = Depends(get_session),
):
    return await AdminService(session).get_user_detail(user_id)


@router.patch("/users/{user_id}/status", response_model=UserStatusOut)
async def update_user_status(
    user_id: int,
    data: UserStatusUpdateIn,
    admin: User = Depends(require_admin_user),
    session: AsyncSession = Depends(get_session),
):
    return await AdminService(session).update_user_status(admin, user_id, data)


@router.post("/users/{user_id}/credits/adjust", response_model=CreditAdjustOut)
async def adjust_user_credit(
    user_id: int,
    data: CreditAdjustIn,
    admin: User = Depends(require_admin_user),
    session: AsyncSession = Depends(get_session),
):
    return await AdminService(session).adjust_credit(admin, user_id, data)


@router.get("/packages", response_model=PageOut[AdminPackageOut])
async def list_packages(
    keyword: str | None = Query(default=None, max_length=100),
    is_active: bool | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    _: User = Depends(require_admin_user),
    session: AsyncSession = Depends(get_session),
):
    items, total = await AdminService(session).list_packages(
        keyword=keyword,
        is_active=is_active,
        page=page,
        page_size=page_size,
    )
    return PageOut(items=items, total=total, page=page, page_size=page_size)


@router.post(
    "/packages",
    response_model=AdminPackageOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_package(
    data: AdminPackageCreateIn,
    admin: User = Depends(require_admin_user),
    session: AsyncSession = Depends(get_session),
):
    return await AdminService(session).create_package(admin, data)


@router.patch("/packages/{package_id}", response_model=AdminPackageOut)
async def update_package(
    package_id: int,
    data: AdminPackageUpdateIn,
    admin: User = Depends(require_admin_user),
    session: AsyncSession = Depends(get_session),
):
    return await AdminService(session).update_package(admin, package_id, data)


@router.get("/orders", response_model=PageOut[AdminOrderOut])
async def list_orders(
    order_no: str | None = Query(default=None, max_length=100),
    user_id: int | None = Query(default=None, ge=1),
    order_status: Literal["pending", "paid"] | None = Query(
        default=None, alias="status"
    ),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    _: User = Depends(require_admin_user),
    session: AsyncSession = Depends(get_session),
):
    items, total = await AdminService(session).list_orders(
        order_no=order_no,
        user_id=user_id,
        status=order_status,
        page=page,
        page_size=page_size,
    )
    return PageOut(items=items, total=total, page=page, page_size=page_size)


@router.get("/orders/{order_id}", response_model=AdminOrderOut)
async def get_order(
    order_id: int,
    _: User = Depends(require_admin_user),
    session: AsyncSession = Depends(get_session),
):
    return await AdminService(session).get_order(order_id)


@router.get("/audit-logs", response_model=PageOut[AdminAuditLogOut])
async def list_audit_logs(
    admin_id: int | None = Query(default=None, ge=1),
    action: str | None = Query(default=None, max_length=100),
    target_type: str | None = Query(default=None, max_length=50),
    target_id: str | None = Query(default=None, max_length=100),
    created_from: datetime | None = None,
    created_to: datetime | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    _: User = Depends(require_admin_user),
    session: AsyncSession = Depends(get_session),
):
    items, total = await AdminService(session).list_audit_logs(
        admin_id=admin_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        created_from=created_from,
        created_to=created_to,
        page=page,
        page_size=page_size,
    )
    return PageOut(items=items, total=total, page=page, page_size=page_size)
