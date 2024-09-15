import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os

# Загрузить переменные окружения из файла .env
load_dotenv()

# Извлечь данные из переменных окружения
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT'))
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')


def send_email(to_email, subject, message, from_email):
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(message, 'plain'))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            # Определите, использовать ли TLS/SSL
            if SMTP_PORT in [465]:
                server.starttls()  # Начать TLS для безопасности
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
            print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")

# Загрузить данные из JSON-файла
with open('data/emails.json', 'r', encoding='utf-8') as file:
    email_data = json.load(file)

# Отправить письма
for entry in email_data:
    send_email(
        to_email=entry['email'],
        subject=entry['subject'],
        message=entry['message'],
        from_email=SMTP_USERNAME
    )
