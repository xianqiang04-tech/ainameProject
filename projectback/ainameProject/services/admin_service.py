from datetime import datetime
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN
from starlette.status import HTTP_404_NOT_FOUND, HTTP_409_CONFLICT

from models.User import User
from models.admin_audit_log import AdminAuditLog
from models.package import Package
from models.user_credit import CreditLog, UserCredit
from repository.admin_repo import AdminRepository
from schemas.admin_schemas import AdminPackageCreateIn, AdminPackageUpdateIn
from schemas.admin_schemas import CreditAdjustIn, UserStatusUpdateIn


class AdminService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = AdminRepository(session)

    async def dashboard(self) -> dict:
        return await self.repository.get_dashboard()

    async def list_users(self, **filters) -> tuple[list[dict], int]:
        return await self.repository.list_users(**filters)

    async def get_user_detail(self, user_id: int) -> dict:
        user = await self.repository.get_user_detail(user_id)
        if user is None:
            raise HTTPException(HTTP_404_NOT_FOUND, "用户不存在")
        return user

    async def update_user_status(
        self,
        admin: User,
        user_id: int,
        data: UserStatusUpdateIn,
    ) -> dict:
        async with self.session.begin():
            target = await self.repository.get_user_for_update(user_id)
            if target is None:
                raise HTTPException(HTTP_404_NOT_FOUND, "用户不存在")
            if target.id == admin.id:
                raise HTTPException(HTTP_403_FORBIDDEN, "不能停用自己的管理员账号")
            if target.role == "admin":
                raise HTTPException(HTTP_403_FORBIDDEN, "第一版不允许修改管理员账号")
            if target.is_active == data.is_active:
                raise HTTPException(HTTP_400_BAD_REQUEST, "用户状态没有变化")

            before = target.is_active
            target.is_active = data.is_active
            self._add_audit_log(
                admin_id=admin.id,
                action="user.status_update",
                target_type="user",
                target_id=str(target.id),
                changes={"before": {"is_active": before}, "after": {"is_active": data.is_active}},
                reason=data.reason,
            )
        return {"id": target.id, "is_active": target.is_active}

    async def adjust_credit(
        self,
        admin: User,
        user_id: int,
        data: CreditAdjustIn,
    ) -> dict:
        async with self.session.begin():
            target = await self.repository.get_user_for_update(user_id)
            if target is None:
                raise HTTPException(HTTP_404_NOT_FOUND, "用户不存在")
            if target.role == "admin":
                raise HTTPException(HTTP_403_FORBIDDEN, "不能调整管理员账号次数")

            credit = await self.repository.get_credit_for_update(user_id)
            if credit is None:
                credit = UserCredit(
                    user_id=user_id,
                    balance=0,
                    total_used=0,
                    total_recharged=0,
                    logo_balance=0,
                    logo_total_used=0,
                )
                self.session.add(credit)
                await self.session.flush()

            is_logo = data.account_type == "logo"
            before_balance = credit.logo_balance if is_logo else credit.balance
            new_balance = before_balance + data.change_count
            if new_balance < 0:
                raise HTTPException(HTTP_409_CONFLICT, "调整后余额不能小于 0")

            if is_logo:
                credit.logo_balance = new_balance
            else:
                credit.balance = new_balance
            self.session.add(
                CreditLog(
                    user_id=user_id,
                    change_count=data.change_count,
                    balance_after=new_balance,
                    type="admin_adjust_logo" if is_logo else "admin_adjust",
                    remark=f"管理员调整：{data.reason}"[:200],
                )
            )
            self._add_audit_log(
                admin_id=admin.id,
                action="user.credit_adjust",
                target_type="user_credit",
                target_id=str(user_id),
                changes={
                    "account_type": data.account_type,
                    "before": {"balance": before_balance},
                    "after": {"balance": new_balance},
                    "change_count": data.change_count,
                },
                reason=data.reason,
            )
        return {
            "user_id": user_id,
            "change_count": data.change_count,
            "balance": new_balance,
        }

    async def list_packages(self, **filters) -> tuple[list[Package], int]:
        return await self.repository.list_packages(**filters)

    async def create_package(
        self, admin: User, data: AdminPackageCreateIn
    ) -> Package:
        async with self.session.begin():
            name = data.name.strip()
            if await self.repository.package_name_exists(name):
                raise HTTPException(HTTP_409_CONFLICT, "套餐名称已经存在")

            package = Package(
                name=name,
                price=data.price,
                credit_count=data.credit_count,
                type=data.type,
                is_active=data.is_active,
            )
            self.session.add(package)
            await self.session.flush()
            self._add_audit_log(
                admin_id=admin.id,
                action="package.create",
                target_type="package",
                target_id=str(package.id),
                changes={"after": self._package_snapshot(package)},
                reason=data.reason,
            )
        return package

    async def update_package(
        self,
        admin: User,
        package_id: int,
        data: AdminPackageUpdateIn,
    ) -> Package:
        async with self.session.begin():
            package = await self.repository.get_package_for_update(package_id)
            if package is None:
                raise HTTPException(HTTP_404_NOT_FOUND, "套餐不存在")

            if data.name is not None:
                name = data.name.strip()
                if await self.repository.package_name_exists(name, package_id):
                    raise HTTPException(HTTP_409_CONFLICT, "套餐名称已经存在")
            else:
                name = package.name

            before = self._package_snapshot(package)
            package.name = name
            if data.price is not None:
                package.price = data.price
            if data.credit_count is not None:
                package.credit_count = data.credit_count
            if data.type is not None:
                package.type = data.type
            if data.is_active is not None:
                package.is_active = data.is_active

            after = self._package_snapshot(package)
            if before == after:
                raise HTTPException(HTTP_400_BAD_REQUEST, "套餐内容没有变化")

            self._add_audit_log(
                admin_id=admin.id,
                action="package.update",
                target_type="package",
                target_id=str(package.id),
                changes={"before": before, "after": after},
                reason=data.reason,
            )
        return package

    async def list_orders(self, **filters) -> tuple[list[dict], int]:
        return await self.repository.list_orders(**filters)

    async def get_order(self, order_id: int) -> dict:
        order = await self.repository.get_order(order_id)
        if order is None:
            raise HTTPException(HTTP_404_NOT_FOUND, "订单不存在")
        return order

    async def list_audit_logs(self, **filters) -> tuple[list[dict], int]:
        created_from = filters.get("created_from")
        created_to = filters.get("created_to")
        if created_from and created_to and created_from > created_to:
            raise HTTPException(HTTP_400_BAD_REQUEST, "开始时间不能晚于结束时间")
        return await self.repository.list_audit_logs(**filters)

    def _add_audit_log(
        self,
        admin_id: int,
        action: str,
        target_type: str,
        target_id: str | None,
        changes: dict | None,
        reason: str | None,
    ) -> None:
        self.session.add(
            AdminAuditLog(
                admin_id=admin_id,
                action=action,
                target_type=target_type,
                target_id=target_id,
                changes=changes,
                reason=reason,
                created_at=datetime.now(),
            )
        )

    @staticmethod
    def _package_snapshot(package: Package) -> dict:
        return {
            "name": package.name,
            "price": str(Decimal(package.price)),
            "credit_count": package.credit_count,
            "type": package.type,
            "is_active": package.is_active,
        }
