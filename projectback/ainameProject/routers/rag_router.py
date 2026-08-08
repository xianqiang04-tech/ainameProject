import os
import json
import shutil
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, Depends
from core.authtools import AuthHandler
from core.rag_service import process_and_store_file
from dotenv import load_dotenv
from schemas.name_schemas import NameIn,NameResultSchema
from core.workflow import genrate_naming
import aio_pika
load_dotenv()
auth_handler = AuthHandler()
router = APIRouter(prefix="/knowledge", tags=["知识库"])

# 上传文件保存的文件夹
UPLOAD_FOLDER=os.getenv("UPLOAD_FOLDER")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

async def send_to_queue(message_dict: dict):
    QUEUE_NAME = "rag_document_queue"
    RABBITMQ_URL = os.getenv("RABBITMQ_URL")
    connection = await aio_pika.connect_robust(RABBITMQ_URL)

    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue(QUEUE_NAME,durable=True)
        message_body = json.dumps(message_dict).encode("utf-8")

        await channel.default_exchange.publish(
            aio_pika.Message(body=message_body),
            routing_key=queue.name,
        )


@router.post("/upload")
async def upload_file( background_tasks: BackgroundTasks,
                       file: UploadFile = File(...),
                       user_id:int=Depends(auth_handler.auth_access_dependency)):
    # 为了防止不同用户起相同名字，在文件名前加上use_id
    file_path = os.path.join(UPLOAD_FOLDER, f"{user_id}_{file.filename}")
    # 用户上传的文件，我们暂时存储在本地的某一个文件夹下，文件夹名字是uploads
    with open(file_path,"wb") as f:
        shutil.copyfileobj(file.file, f)

    # 后台启动任务
    # 后台执行process_and_store_file函数，作为独立任务
    task_message = {
        "user_id":user_id,
        "file_path":file_path,
    }

    await send_to_queue(task_message)

    return {"result": "success",
            "message": f"文件 {file.filename} 上传成功！后台正在为您构建专属知识库，请稍候测试起名功能。"
            }

