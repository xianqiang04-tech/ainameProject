import asyncio
import json
import sys
import aio_pika
from core.rag_service import process_and_store_file
import settings
from dotenv import load_dotenv
import os
load_dotenv()

async def process_message(message: aio_pika.IncomingMessage):
    async with message.process():
        task_data = json.loads(message.body.decode('utf-8'))
        user_id = task_data.get("user_id")
        file_path = task_data.get("file_path")

        process_and_store_file(file_path, user_id)

async def main():
    RABBITMQ_URL = os.getenv("RABBITMQ_URL")
    connection = await aio_pika.connect(RABBITMQ_URL)
    channel = await connection.channel()

    await channel.set_qos(prefetch_count=1)
    queue = await channel.declare_queue(settings.QUEUE_NAME, durable=True)

    # 创建消费函数
    await queue.consume(process_message)
    # 控制消费者一直监听等待
    await asyncio.Future()

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())