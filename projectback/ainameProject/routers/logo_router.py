import asyncio

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.authtools import AuthHandler
from core.logo_tools import generate_company_logo
from dependencies import get_session
from repository.credit_repo import CreditRepository
from schemas.logo_schemas import LogoGenerateIn, LogoGenerateOut


router = APIRouter(prefix="/logos", tags=["logos"])
auth_handler = AuthHandler()


@router.post("/generate", response_model=LogoGenerateOut)
async def generate_logo(
        data: LogoGenerateIn,
        user_id: int = Depends(auth_handler.auth_access_dependency),
        session: AsyncSession = Depends(get_session),
):
    company_name = data.company_name.strip()
    if not company_name:
        raise HTTPException(status_code=400, detail="请输入企业名称")

    credit_repository = CreditRepository(session)
    credit = await credit_repository.get_credit_detail(user_id)
    logo_balance = credit.logo_balance if credit else 0
    # 1.先查询剩余的Logo次数，如果有，调用生成工具，如果没有，告诉用户充值
    if logo_balance <= 0:
        raise HTTPException(status_code=400, detail="Logo次数不足，请充值后使用")

    # 2.先扣次数（行锁下并发双击会被拦截）；生成失败再退还
    try:
        await credit_repository.consume_logo_credit(user_id=user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Logo次数不足，请充值后使用")

    # 3.调用Logo生成接口（同步 httpx 调用放到线程中执行，避免阻塞事件循环）
    try:
        logo = await asyncio.to_thread(
            generate_company_logo,
            company_name=company_name,
            style_feedback=data.style_feedback,
        )
    except Exception as e:
        # 生成失败，退还本次扣除的Logo次数
        await credit_repository.grant_logo_credit(
            user_id=user_id,
            count=1,
            remark="Logo生成失败，退还1次",
        )
        print(f"logo generate failed: {e}")
        raise HTTPException(status_code=500, detail="Logo生成失败，次数已退回，请稍后重试")

    return {
        "company_name": company_name,
        **logo,
    }
