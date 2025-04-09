

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr
from jinja2 import Environment, FileSystemLoader



from errors.exception import InternalProcessingError
from tools.log import Log
from config.setting import Settings


settings = Settings()
file_loader = FileSystemLoader(searchpath="templates/")
env = Environment(loader=file_loader, auto_reload=True, autoescape=True)


class MailService:
    mail_config = ConnectionConfig(
        MAIL_USERNAME="kweku4sta@gmail.com",
        MAIL_PASSWORD=settings.MAIL_PASSWORD,
        MAIL_FROM="kweku4sta@gmail.com",
        MAIL_FROM_NAME="BDCOMCPricing",
        MAIL_PORT=465,
        MAIL_SERVER="smtp.gmail.com",
        MAIL_SSL_TLS=True,
        MAIL_STARTTLS=False,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True,
        TEMPLATE_FOLDER="templates"
    )


    @classmethod
    async def send_email(cls, email: EmailStr, msg: str , subject: str, content: dict[str, str] = None):
        template = env.get_template('email.html')
        html = template.render(
            header = content.get('header'),
            title = content.get('title'),
            reset_code = content.get('reset_code'),
            email = content.get('email'),
            name = content.get('name'),
            content = msg,
        )

        try: 
            receipient_emails = email.split(',')
            message = MessageSchema(
                subject=subject,
                recipients=receipient_emails,
                body=html, subtype=MessageType.html,
                headers={"Reply-to": "no-reply@bdcomc.com"}
                
            )

            fm = FastMail(cls.mail_config)
            await fm.send_message(message, template_name='email.html')
            return True
        except ConnectionErrors as e: 
            Log.mail_log_handler(str(e), email, subject, msg)
            raise ConnectionError(str(e)) from e
        except Exception as e: 
            Log.mail_log_handler(str(e), email, subject, msg)
            raise InternalProcessingError(str(e)) from e
        

    

