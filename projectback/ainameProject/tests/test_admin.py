import unittest
from types import SimpleNamespace

from fastapi import HTTPException

from core.authtools import AuthHandler
from dependencies import require_admin_user
from models.User import User
from models.admin_audit_log import AdminAuditLog
from models.user_credit import CreditLog
from schemas.admin_schemas import AdminPackageCreateIn, AdminPackageUpdateIn
from schemas.admin_schemas import CreditAdjustIn
from schemas.admin_schemas import UserStatusUpdateIn
from schemas.user_schemas import LoginoutSchema
from services.admin_service import AdminService


class FakeTransaction:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        return False


class FakeSession:
    def __init__(self):
        self.added = []

    def begin(self):
        return FakeTransaction()

    def add(self, model):
        self.added.append(model)

    async def flush(self):
        return None


class FakeAdminRepository:
    def __init__(self, user=None, credit=None):
        self.user = user
        self.credit = credit

    async def get_user_for_update(self, user_id):
        return self.user

    async def get_credit_for_update(self, user_id):
        return self.credit


class AdminSchemaTests(unittest.TestCase):
    def test_login_response_keeps_admin_role(self):
        response = LoginoutSchema.model_validate(
            {
                "user": SimpleNamespace(
                    email="admin@admin.com", username="admin", role="admin"
                ),
                "access_token": "access-token",
                "refresh_token": "refresh-token",
            }
        )
        self.assertEqual(response.user.role, "admin")

    def test_credit_adjust_rejects_zero(self):
        with self.assertRaises(ValueError):
            CreditAdjustIn(change_count=0, reason="test")

    def test_package_update_requires_a_change(self):
        with self.assertRaises(ValueError):
            AdminPackageUpdateIn(reason="test")

    def test_package_name_rejects_only_whitespace(self):
        with self.assertRaises(ValueError):
            AdminPackageCreateIn(name="   ", price="1.00", credit_count=1)

    def test_openapi_contains_admin_routes(self):
        from main import app

        paths = app.openapi()["paths"]
        self.assertIn("/admin/dashboard", paths)
        self.assertIn("/admin/users/{user_id}/credits/adjust", paths)
        self.assertIn("/admin/audit-logs", paths)


class AdminAuthTests(unittest.IsolatedAsyncioTestCase):
    async def test_require_admin_accepts_active_admin(self):
        admin = SimpleNamespace(role="admin", is_active=True)
        self.assertIs(await require_admin_user(admin), admin)

    async def test_require_admin_rejects_normal_user(self):
        user = SimpleNamespace(role="user", is_active=True)
        with self.assertRaises(HTTPException) as caught:
            await require_admin_user(user)
        self.assertEqual(caught.exception.status_code, 403)

    async def test_require_admin_rejects_inactive_admin(self):
        admin = SimpleNamespace(role="admin", is_active=False)
        with self.assertRaises(HTTPException) as caught:
            await require_admin_user(admin)
        self.assertEqual(caught.exception.status_code, 403)

    async def test_missing_bearer_credentials_returns_401(self):
        handler = AuthHandler()
        with self.assertRaises(HTTPException) as caught:
            handler.auth_access_dependency(None)
        self.assertEqual(caught.exception.status_code, 401)


class AdminServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_credit_adjust_writes_credit_and_audit_logs(self):
        session = FakeSession()
        service = AdminService(session)
        target = SimpleNamespace(id=2, role="user")
        credit = SimpleNamespace(balance=3)
        service.repository = FakeAdminRepository(target, credit)
        admin = SimpleNamespace(id=1, role="admin")

        result = await service.adjust_credit(
            admin,
            2,
            CreditAdjustIn(change_count=2, reason="manual test"),
        )

        self.assertEqual(result["balance"], 5)
        self.assertEqual(credit.balance, 5)
        self.assertTrue(any(isinstance(item, CreditLog) for item in session.added))
        self.assertTrue(
            any(isinstance(item, AdminAuditLog) for item in session.added)
        )

    async def test_credit_adjust_rejects_negative_balance(self):
        session = FakeSession()
        service = AdminService(session)
        target = SimpleNamespace(id=2, role="user")
        credit = SimpleNamespace(balance=1)
        service.repository = FakeAdminRepository(target, credit)

        with self.assertRaises(HTTPException) as caught:
            await service.adjust_credit(
                SimpleNamespace(id=1, role="admin"),
                2,
                CreditAdjustIn(change_count=-2, reason="manual test"),
            )
        self.assertEqual(caught.exception.status_code, 409)
        self.assertEqual(credit.balance, 1)

    async def test_admin_cannot_change_own_status(self):
        session = FakeSession()
        service = AdminService(session)
        admin = SimpleNamespace(id=1, role="admin", is_active=True)
        service.repository = FakeAdminRepository(admin)

        with self.assertRaises(HTTPException) as caught:
            await service.update_user_status(
                admin,
                1,
                UserStatusUpdateIn(is_active=False, reason="manual test"),
            )
        self.assertEqual(caught.exception.status_code, 403)


if __name__ == "__main__":
    unittest.main()
