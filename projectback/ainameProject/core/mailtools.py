from fastapi_mail import FastMail,ConnectionConfig
from dotenv import load_dotenv
load_dotenv()
import os

def create_mail_instance() -> FastMail:
    config = ConnectionConfig(
        MAIL_SERVER=os.getenv("MAIL_SERVER"),
        MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
        MAIL_FROM=os.getenv("MAIL_FROM"),
        MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
        MAIL_PORT=os.getenv("MAIL_PORT"),
        MAIL_FROM_NAME=os.getenv("MAIL_FROM_NAME"),
        MAIL_SSL_TLS=False,
        MAIL_STARTTLS=True,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True,
    )
    return FastMail(config)