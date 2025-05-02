from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi import Request
from pathlib import Path
from app.services.auth import create_email_token
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")

conf = ConnectionConfig(
    MAIL_USERNAME='8e030f958a6730',
    MAIL_PASSWORD="your_password",
    MAIL_FROM="8e030f958a6730@mailtrap.io",
    MAIL_PORT=587,
    MAIL_SERVER="8e030f958a6730@mailtrap.io",
    MAIL_FROM_NAME="Contacts App",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)



fm = FastMail(conf)


async def send_confirmation_email(request: Request, email: str, username: str, host: str):
    """
        Sends a confirmation email with a verification link.

        :param request: Request: The FastAPI request object to build base URL.
        :param email: str: The recipient's email address.
        :param username: str: The recipient's username for personalization.
        :param host: str: The host URL to include in the confirmation link.
        :return: None
        :raises Exception: If the email fails to send.
        """
    token = create_email_token({"sub": email})
    host = request.base_url._url.strip("/")  # http://127.0.0.1:8000

    confirm_link = f"{host}/auth/confirm-email/{token}"

    html_content = templates.get_template("email_template.html").render({
        "request": request,
        "username": username,
        "confirm_link": confirm_link,
    })

    message = MessageSchema(
        subject="Підтвердження реєстрації",
        recipients=[email],
        body=html_content,
        subtype="html"
    )

    try:
        await fm.send_message(message)
        print("Email sent successfully")
    except Exception as e:
        print(f"Error sending email: {e}")
        raise