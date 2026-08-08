from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.user_credit import UserCredit, CreditLog

class CreditRepository:
    def __init__(self,session):
        self.session = session

    async def create_register_credit(self,user_id:int,gift_count:int=3):
        async with self.session.begin():
            # 注册成功后，给用户创建次数账户，并赠送3次起名次数。
            credit = UserCredit(
                user_id=user_id,
                balance= gift_count,
                total_used= 0,
                total_recharged= 0
            )
            self.session.add(credit)

            log = CreditLog(
                user_id=user_id,
                change_count=gift_count,
                balance_after=gift_count,
                type="register_gift",
                remark=f"注册赠送{gift_count}次起名机会"
            )
            self.session.add(log)

            return credit

    # 获取账户剩余次数,根据用户id获取账户次数
    async def get_credit(self,user_id:int):
        async with self.session.begin():
            credit = await self.session.scalar(select(UserCredit).where(UserCredit.user_id == user_id))
            if not credit:
                return 0
            return credit.balance

    # 消费一次
    async def consume_name_credit(self,user_id:int):
        async with self.session.begin():
            # with_for_update 锁表 , 我们操作时不让其他人操作
            credit = await self.session.scalar(select(UserCredit).where(UserCredit.user_id == user_id).with_for_update())
            if not credit:
                raise ValueError("用户账户不存在")
            if credit.balance <= 0:
                raise ValueError("次数不足")
            # 1.查询credit表
            # 2.总次数减1，使用次数加1
            credit.balance -= 1
            credit.total_used += 1
            # 3.日志表记录1次
            log = CreditLog(
                user_id=user_id,
                change_count=-1,
                balance_after=credit.balance,
                type="consume_name",
                remark="AI起名消耗了1次"
            )
            self.session.add(log)

            return credit.balance
