import random
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.testing.pickleable import Order

from models.package import Package
from models.user_credit import UserCredit, CreditLog
from models.user_order import UserOrder

class OrderRepository:
    def __init__(self, session):
        self.session = session

    # 生成订单号
    def create_order_no(self):
        time_str = datetime.now().strftime("%Y%m%d%H%M%S")
        random_str = str(random.randint(100000, 999999))
        order_no = time_str + random_str
        return order_no

    async def create_order(self, package: Package, user_id: int):
        async with self.session.begin():
            order = UserOrder(
                order_no=self.create_order_no(),
                user_id=user_id,
                package_id=package.id,
                amount=package.price,
                credit_count=package.credit_count,
                package_type=package.type,
                status="pending"
            )
            self.session.add(order)
            await self.session.flush()
            return order

    async def get_by_order_no(self, order_no):
        async with self.session.begin():
            order = await self.session.scalar(select(UserOrder).where(UserOrder.order_no == order_no))
            return order

    async def pay_success(self, order_no, alipay_trade_no):
        async with self.session.begin():
            order = await self.session.scalar(select(UserOrder).where(UserOrder.order_no == order_no).with_for_update())

            if not order:
                raise ValueError("Order Not Found")
            # 订单可能被多次异步调用，所以，非常必要判断状态，如果已经做过处理，避免重复处理
            if order.status == "paid":
                return order,False

            if order.status != "pending":
                raise ValueError("订单状态异常")
            # 把订单状态改为已付款
            order.status = "paid"
            order.alipay_trade_no = alipay_trade_no
            order.paid_at = datetime.now()
            # 增加次数（按套餐类型发放到对应账户）
            userCredit: UserCredit = await self.session.scalar(select(UserCredit).where(UserCredit.user_id == order.user_id).with_for_update())
            if order.package_type == "logo":
                userCredit.logo_balance = userCredit.logo_balance + order.credit_count

                log = CreditLog(
                    user_id=order.user_id,
                    change_count=order.credit_count,
                    balance_after=userCredit.logo_balance,
                    type="recharge_logo",
                    remark=f"支付成功，充值Logo次数为{order.credit_count}"
                )
            else:
                userCredit.balance = userCredit.balance + order.credit_count

                log = CreditLog(
                    user_id=order.user_id,
                    change_count=order.credit_count,
                    balance_after=userCredit.balance,
                    type="recharge",
                    remark=f"支付成功，充值次数为{order.credit_count}"
                )
            self.session.add(log)
            return order,True