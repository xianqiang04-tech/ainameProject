from fastapi import FastAPI
from dependencies import get_email
from routers.auth_router import router as auth_router
from routers.name_router import router as name_router
from routers.credit_router import router as credit_router
from routers.package_router import router as package_router
from routers.pay_router import router as pay_router
from routers.rag_router import router as rag_router
from routers.admin_router import router as admin_router

from fastapi import FastAPI,Depends
from starlette.responses import JSONResponse
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr, BaseModel
from typing import List
from contextlib import asynccontextmanager
from core.workflow import init_workflow_graph, close_workflow_graph


# @asynccontextmanager 把下面的 lifespan 函数变成一个“上下文管理器”,在 FastAPI 中，它专门用来界定“启动前”和“关闭后”两个不同的阶段。
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 服务启动时，安全地初始化带记忆的工作流
    await init_workflow_graph()
    # 在这个 yield 关键字之上的所有代码，都会在 FastAPI 应用启动、但还没有开始接收任何外部网络请求的时候执行
    # 在这个 yield 关键字之下的所有代码，只有在你停止服务器，或者服务器被关闭时才会执行。
    yield
    # 服务停止时，清理数据库连接
    await close_workflow_graph()

from pathlib import Path
from fastapi.staticfiles import StaticFiles
from routers.logo_router import router as logo_router
# 绑定到 FastAPI 实例上
app = FastAPI(lifespan=lifespan)
BACKEND_DIR = Path(__file__).resolve().parent
STATIC_DIR = BACKEND_DIR / "static"
(STATIC_DIR / "logos").mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

app.include_router(auth_router)
app.include_router(name_router)
app.include_router(credit_router)
app.include_router(package_router)
app.include_router(pay_router)
app.include_router(rag_router)
app.include_router(logo_router)
app.include_router(admin_router)
@app.post("/email")
async def simple_send(mail:FastMail=Depends(get_email)):
    html = """<p>Hi this test mail, thanks for using Fastapi-mail</p> """

    message = MessageSchema(
        subject="ai_name code",
        recipients=["1647658863@qq.com"],
        body=html,
        subtype=MessageType.html)
    # 根据配置构造fastmail
    # fastmail发送消息
    await mail.send_message(message)
    return {"message":"邮件发送成功，请到你的邮箱查看"}
