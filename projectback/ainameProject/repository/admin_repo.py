from datetime import datetime
from decimal import Decimal

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from models.User import User
from models.admin_audit_log import AdminAuditLog
from models.package import Package
from models.user_credit import UserCredit
from models.user_order import UserOrder


class AdminRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_dashboard(self) -> dict:
        user_count = await self.session.scalar(select(func.count(User.id)))
        active_user_count = await self.session.scalar(
            select(func.count(User.id)).where(User.is_active.is_(True))
        )
        order_count = await self.session.scalar(select(func.count(UserOrder.id)))
        paid_order_count = await self.session.scalar(
            select(func.count(UserOrder.id)).where(UserOrder.status == "paid")
        )
        paid_revenue = await self.session.scalar(
            select(func.coalesce(func.sum(UserOrder.amount), 0)).where(
                UserOrder.status == "paid"
            )
        )
        return {
            "user_count": user_count or 0,
            "active_user_count": active_user_count or 0,
            "order_count": order_count or 0,
            "paid_order_count": paid_order_count or 0,
            "paid_revenue": Decimal(paid_revenue or 0),
        }

    async def list_users(
        self,
        keyword: str | None,
        is_active: bool | None,
        page: int,
        page_size: int,
    ) -> tuple[list[dict], int]:
        filters = []
        if keyword:
            pattern = f"%{keyword.strip()}%"
            filters.append(
                or_(User.email.ilike(pattern), User.username.ilike(pattern))
            )
        if is_active is not None:
            filters.append(User.is_active.is_(is_active))

        total = await self.session.scalar(
            select(func.count(User.id)).where(*filters)
        )
        statement = (
            select(
                User.id,
                User.email,
                User.username,
                User.role,
                User.is_active,
                User.created_at,
                User.last_login_at,
                func.coalesce(UserCredit.balance, 0).label("balance"),
            )
            .outerjoin(UserCredit, UserCredit.user_id == User.id)
            .where(*filters)
            .order_by(User.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        rows = (await self.session.execute(statement)).mappings().all()
        return [dict(row) for row in rows], total or 0

    async def get_user_detail(self, user_id: int) -> dict | None:
        statement = (
            select(
                User.id,
                User.email,
                User.username,
                User.role,
                User.is_active,
                User.created_at,
                User.last_login_at,
                func.coalesce(UserCredit.balance, 0).label("balance"),
                func.coalesce(UserCredit.total_used, 0).label("total_used"),
                func.coalesce(UserCredit.total_recharged, 0).label(
                    "total_recharged"
                ),
            )
            .outerjoin(UserCredit, UserCredit.user_id == User.id)
            .where(User.id == user_id)
        )
        row = (await self.session.execute(statement)).mappings().first()
        if row is None:
            return None

        order_count = await self.session.scalar(
            select(func.count(UserOrder.id)).where(UserOrder.user_id == user_id)
        )
        paid_order_count = await self.session.scalar(
            select(func.count(UserOrder.id)).where(
                UserOrder.user_id == user_id,
                UserOrder.status == "paid",
            )
        )
        result = dict(row)
        result.update(
            order_count=order_count or 0,
            paid_order_count=paid_order_count or 0,
        )
        return result

    async def get_user_for_update(self, user_id: int) -> User | None:
        return await self.session.scalar(
            select(User).where(User.id == user_id).with_for_update()
        )

    async def get_credit_for_update(self, user_id: int) -> UserCredit | None:
        return await self.session.scalar(
            select(UserCredit)
            .where(UserCredit.user_id == user_id)
            .with_for_update()
        )

    async def list_packages(
        self,
        keyword: str | None,
        is_active: bool | None,
        page: int,
        page_size: int,
    ) -> tuple[list[Package], int]:
        filters = []
        if keyword:
            filters.append(Package.name.ilike(f"%{keyword.strip()}%"))
        if is_active is not None:
            filters.append(Package.is_active.is_(is_active))

        total = await self.session.scalar(
            select(func.count(Package.id)).where(*filters)
        )
        packages = await self.session.scalars(
            select(Package)
            .where(*filters)
            .order_by(Package.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(packages.all()), total or 0

    async def get_package_for_update(self, package_id: int) -> Package | None:
        return await self.session.scalar(
            select(Package).where(Package.id == package_id).with_for_update()
        )

    async def package_name_exists(
        self, name: str, exclude_id: int | None = None
    ) -> bool:
        statement = select(Package.id).where(Package.name == name)
        if exclude_id is not None:
            statement = statement.where(Package.id != exclude_id)
        return await self.session.scalar(statement) is not None

    async def list_orders(
        self,
        order_no: str | None,
        user_id: int | None,
        status: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[dict], int]:
        filters = []
        if order_no:
            filters.append(UserOrder.order_no.ilike(f"%{order_no.strip()}%"))
        if user_id is not None:
            filters.append(UserOrder.user_id == user_id)
        if status is not None:
            filters.append(UserOrder.status == status)

        total = await self.session.scalar(
            select(func.count(UserOrder.id)).where(*filters)
        )
        statement = (
            select(
                UserOrder.id,
                UserOrder.order_no,
                UserOrder.user_id,
                User.email.label("user_email"),
                User.username,
                UserOrder.package_id,
                Package.name.label("package_name"),
                UserOrder.amount,
                UserOrder.credit_count,
                UserOrder.status,
                UserOrder.alipay_trade_no,
                UserOrder.created_at,
                UserOrder.paid_at,
            )
            .join(User, User.id == UserOrder.user_id)
            .join(Package, Package.id == UserOrder.package_id)
            .where(*filters)
            .order_by(UserOrder.created_at.desc(), UserOrder.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        rows = (await self.session.execute(statement)).mappings().all()
        return [dict(row) for row in rows], total or 0

    async def get_order(self, order_id: int) -> dict | None:
        statement = (
            select(
                UserOrder.id,
                UserOrder.order_no,
                UserOrder.user_id,
                User.email.label("user_email"),
                User.username,
                UserOrder.package_id,
                Package.name.label("package_name"),
                UserOrder.amount,
                UserOrder.credit_count,
                UserOrder.status,
                UserOrder.alipay_trade_no,
                UserOrder.created_at,
                UserOrder.paid_at,
            )
            .join(User, User.id == UserOrder.user_id)
            .join(Package, Package.id == UserOrder.package_id)
            .where(UserOrder.id == order_id)
        )
        row = (await self.session.execute(statement)).mappings().first()
        return dict(row) if row else None

    async def list_audit_logs(
        self,
        admin_id: int | None,
        action: str | None,
        target_type: str | None,
        target_id: str | None,
        created_from: datetime | None,
        created_to: datetime | None,
        page: int,
        page_size: int,
    ) -> tuple[list[dict], int]:
        filters = []
        if admin_id is not None:
            filters.append(AdminAuditLog.admin_id == admin_id)
        if action:
            filters.append(AdminAuditLog.action == action)
        if target_type:
            filters.append(AdminAuditLog.target_type == target_type)
        if target_id:
            filters.append(AdminAuditLog.target_id == target_id)
        if created_from:
            filters.append(AdminAuditLog.created_at >= created_from)
        if created_to:
            filters.append(AdminAuditLog.created_at <= created_to)

        total = await self.session.scalar(
            select(func.count(AdminAuditLog.id)).where(*filters)
        )
        admin_user = aliased(User)
        statement = (
            select(
                AdminAuditLog.id,
                AdminAuditLog.admin_id,
                admin_user.email.label("admin_email"),
                admin_user.username.label("admin_username"),
                AdminAuditLog.action,
                AdminAuditLog.target_type,
                AdminAuditLog.target_id,
                AdminAuditLog.changes,
                AdminAuditLog.reason,
                AdminAuditLog.created_at,
            )
            .join(admin_user, admin_user.id == AdminAuditLog.admin_id)
            .where(*filters)
            .order_by(AdminAuditLog.created_at.desc(), AdminAuditLog.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        rows = (await self.session.execute(statement)).mappings().all()
        return [dict(row) for row in rows], total or 0
