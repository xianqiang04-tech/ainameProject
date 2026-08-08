from datetime import datetime
from decimal import Decimal
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


T = TypeVar("T")


class PageOut(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int


class AdminMeOut(BaseModel):
    id: int
    email: EmailStr
    username: str
    role: str
    is_active: bool
    created_at: datetime
    last_login_at: datetime | None
    model_config = ConfigDict(from_attributes=True)


class DashboardOut(BaseModel):
    user_count: int
    active_user_count: int
    order_count: int
    paid_order_count: int
    paid_revenue: Decimal


class AdminUserListItemOut(AdminMeOut):
    balance: int


class AdminUserDetailOut(AdminUserListItemOut):
    total_used: int
    total_recharged: int
    order_count: int
    paid_order_count: int


class UserStatusUpdateIn(BaseModel):
    is_active: bool
    reason: str = Field(min_length=1, max_length=500)
    model_config = ConfigDict(str_strip_whitespace=True)


class UserStatusOut(BaseModel):
    id: int
    is_active: bool


class CreditAdjustIn(BaseModel):
    change_count: int = Field(ge=-100000, le=100000)
    reason: str = Field(min_length=1, max_length=500)
    model_config = ConfigDict(str_strip_whitespace=True)

    @model_validator(mode="after")
    def validate_change_count(self):
        if self.change_count == 0:
            raise ValueError("change_count 不能为 0")
        return self


class CreditAdjustOut(BaseModel):
    user_id: int
    change_count: int
    balance: int


class AdminPackageCreateIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: Decimal = Field(ge=0, max_digits=10, decimal_places=2)
    credit_count: int = Field(ge=1)
    is_active: bool = True
    reason: str | None = Field(default=None, min_length=1, max_length=500)
    model_config = ConfigDict(str_strip_whitespace=True)


class AdminPackageUpdateIn(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    price: Decimal | None = Field(
        default=None, ge=0, max_digits=10, decimal_places=2
    )
    credit_count: int | None = Field(default=None, ge=1)
    is_active: bool | None = None
    reason: str = Field(min_length=1, max_length=500)
    model_config = ConfigDict(str_strip_whitespace=True)

    @model_validator(mode="after")
    def validate_changes(self):
        if all(
            value is None
            for value in (self.name, self.price, self.credit_count, self.is_active)
        ):
            raise ValueError("至少提供一个需要修改的套餐字段")
        return self


class AdminPackageOut(BaseModel):
    id: int
    name: str
    price: Decimal
    credit_count: int
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class AdminOrderOut(BaseModel):
    id: int
    order_no: str
    user_id: int
    user_email: EmailStr
    username: str
    package_id: int
    package_name: str
    amount: Decimal
    credit_count: int
    status: str
    alipay_trade_no: str | None
    created_at: datetime
    paid_at: datetime | None


class AdminAuditLogOut(BaseModel):
    id: int
    admin_id: int
    admin_email: EmailStr
    admin_username: str
    action: str
    target_type: str
    target_id: str | None
    changes: dict[str, Any] | None
    reason: str | None
    created_at: datetime
