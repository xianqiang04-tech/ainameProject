from fastapi import APIRouter, Depends, HTTPException,Request
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import PlainTextResponse

from core.alipaytools import (
create_alipay,
get_alipay_gateway,
get_notify_url,
get_return_url,
)
from core.authtools import AuthHandler
from dependencies import get_session
from models.user_order import UserOrder
from repository.order_repo import OrderRepository
from repository.package_repo import PackageRepository
from schemas.pay_schemas import CreateOrderIn, CreateOrderOut
from decimal import Decimal

router = APIRouter(prefix="/pay")

auth_handler = AuthHandler()

@router.post("/create_order",tags=["pay"],response_model=CreateOrderOut)
async def create_order(
        packageid: CreateOrderIn,
        session: AsyncSession = Depends(get_session),
        user_id: int=Depends(auth_handler.auth_access_dependency)
):
    # 1. 根据用户传递过来的id,查询数据，获取套餐，不能让前端传套餐数据，不然很容易造假
    # 只能传id，如果id造假，我们直接返回报错
    package_repo = PackageRepository(session=session)
    package = await package_repo.get_package_by_id(packageid.package_id)
    if package is None:
        raise HTTPException(status_code=404, detail="Package not found")
    # 2. 去生成订单
    orderRepo = OrderRepository(session)
    order = await orderRepo.create_order(package, user_id)

    # 3.创建支付宝链接
    alipay = create_alipay()
    order_string = alipay.api_alipay_trade_page_pay(
        out_trade_no=order.order_no,
        subject=f"购买{package.name}",
        total_amount=str(order.amount),
        return_url=get_return_url(),
        notify_url=get_notify_url()
    )

    pay_url = f"{get_alipay_gateway()}?{order_string}"

    return CreateOrderOut(
        order_no=order.order_no,
        amount=order.amount,
        credit_count=order.credit_count,
        pay_url=pay_url,
    )

from fastapi.responses import HTMLResponse

@router.post("/alipay_notify")
# 异步函数代码，此处需要公网服务器。但是逻辑必须理解
async def alipay_notify(
        request: Request,
        session: AsyncSession = Depends(get_session),
):
    # 1.获取支付宝post过来的表单
    form_data = await request.form()
    notify_data = dict(form_data)

    # 2.取参数
    sign = notify_data.pop("sign", None)
    notify_data.pop("sign_type", None)

    if not sign:
        return HTTPException(400,"没有合法签名")

    alipay = create_alipay()
    verify_result = alipay.verify(notify_data, sign)
    if not verify_result:
        return PlainTextResponse("failure")

    order_no =notify_data.get("out_trade_no")
    total_amount = notify_data.get("total_amount")
    alipay_trade_no = notify_data.get("trade_no")
    trade_status = notify_data.get("trade_status")

    if not order_no:
        return PlainTextResponse("failure")

    if trade_status not in ["TRADE_SUCCESS","TRADE_FINISHED"]:
        return PlainTextResponse("failure")

    order_repo = OrderRepository(session)
    order:UserOrder = await order_repo.get_by_order_no(order_no)

    if not order:
        return PlainTextResponse("failure")

    if Decimal(str(order.amount)) != Decimal(str(total_amount)):
        return PlainTextResponse("failure")

    # 1.修改订单状态、增加账户次数、写流水
    await order_repo.pay_success(order_no,alipay_trade_no)
    return PlainTextResponse("success")

@router.get("/success", response_class=HTMLResponse)
async def pay_success(request: Request,
                      session: AsyncSession = Depends(get_session)):


    # 1. 获取支付宝浏览器跳转回来时携带的参数
    params = dict(request.query_params)

    # 2. 获取订单号
    order_no = params.get("out_trade_no")
    alipay_trade_no = params.get("trade_no", "")
    total_amount = params.get("total_amount")

    if not order_no:
        return """
        <html>
            <head><meta charset="utf-8"></head>
            <body>
                <h2>支付结果异常</h2>
                <p>没有获取到订单号 out_trade_no。</p>
            </body>
        </html>
        """

    # 3. 验签
    #sign_data = params.copy()
    sign = params.pop("sign", None)
    params.pop("sign_type", None)

    if not sign:
        return """
        <html>
            <head><meta charset="utf-8"></head>
            <body>
                <h2>支付结果异常</h2>
                <p>没有获取到支付宝签名。</p>
            </body>
        </html>
        """

    alipay = create_alipay()
    print("接收到的参数:", params)
    print("提取的签名:", params.get("sign"))
    verify_result = alipay.verify(params, sign)

    if not verify_result:
        return """
        <html>
            <head><meta charset="utf-8"></head>
            <body>
                <h2>支付结果异常</h2>
                <p>支付宝验签失败，请检查支付宝公钥配置。</p>
            </body>
        </html>
        """

    order_repo = OrderRepository(session=session)

    # 4. 查询本地订单
    order = await order_repo.get_by_order_no(order_no)

    if not order:
        return """
        <html>
            <head><meta charset="utf-8"></head>
            <body>
                <h2>支付结果异常</h2>
                <p>订单不存在。</p>
            </body>
        </html>
        """

    # 5. 校验金额，防止有人伪造回跳地址
    if total_amount is not None:
        if Decimal(str(order.amount)) != Decimal(str(total_amount)):
            return """
            <html>
                <head><meta charset="utf-8"></head>
                <body>
                    <h2>支付结果异常</h2>
                    <p>订单金额校验失败。</p>
                </body>
            </html>
            """

    try:
        # 6. 修改数据库：
        # 订单 pending -> paid
        # 增加用户次数
        # 写入次数流水
        order, is_first_success = await order_repo.pay_success(
            order_no=order_no,
            alipay_trade_no=alipay_trade_no,
        )
    except Exception as e:
        return f"""
        <html>
            <head><meta charset="utf-8"></head>
            <body>
                <h2>支付处理失败</h2>
                <p>{str(e)}</p>
            </body>
        </html>
        """

    # 7. 返回支付成功页面
    if is_first_success:
        message = f"支付成功，已为您增加 {order.credit_count} 次起名次数。"
    else:
        message = "该订单之前已经处理过，请不要重复刷新页面。"

    return f"""
    <html>
        <head>
            <meta charset="utf-8">
            <title>支付成功</title>
        </head>
        <body>
            <h2>支付完毕</h2>
            <p>{message}</p>
            <p>订单号：{order.order_no}</p>
            <p>订单状态：{order.status}</p>
        </body>
    </html>
    """
