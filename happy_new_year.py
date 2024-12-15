import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader
import os
import logging


# Загрузить переменные окружения из файла .env
load_dotenv()

# Извлечь данные из переменных окружения
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT'))
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')

# Проверить на наличие обязательных переменных
if not all([SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD]):
    raise ValueError("Missing required SMTP environment variables.")

# Настройка логирования
logging.basicConfig(level=logging.INFO)


def send_email(to_email, subject, html_message, from_email, image_path):
    """
    Функция для отправки письма с вложением изображения.
    """
    msg = MIMEMultipart('related')
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    # Добавить HTML-часть в письмо
    html_part = MIMEText(html_message, 'html')
    msg.attach(html_part)

    # Прикрепить изображение новогодней открытки
    attach_image(msg, image_path)

    # Подключение к серверу SMTP
    send_via_smtp(msg, to_email, from_email)


def attach_image(msg, image_path):
    """
    Функция для прикрепления изображения к письму.
    """
    try:
        with open(image_path, 'rb') as img_file:
            img = MIMEImage(img_file.read())
            img.add_header('Content-ID', '<header_image>')  # Используется в HTML-шаблоне как cid:header_image
            img.add_header('Content-Disposition', 'inline', filename=os.path.basename(image_path))
            msg.attach(img)
    except FileNotFoundError:
        logging.error(f"Изображение '{image_path}' не найдено")


def send_via_smtp(msg, to_email, from_email):
    """
    Функция для отправки письма через SMTP сервер.
    """
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Защищенное соединение
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
            logging.info(f"Email отправлен на {to_email}")
    except Exception as e:
        logging.error(f"Ошибка при отправке email на {to_email}: {e}")


def load_email_data(file_path):
    """
    Функция для загрузки данных email из JSON-файла.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        logging.error("JSON файл с данными не найден!")
        exit()


def generate_html_message(name, subject):
    """
    Функция для генерации HTML-сообщения с использованием Jinja2 шаблона.
    """
    template_loader = FileSystemLoader('templates')  # Указываем директорию с шаблонами
    template_env = Environment(loader=template_loader)

    try:
        template = template_env.get_template('email_template.html')
        # Рендеринг шаблона с данными
        return template.render(name=name, subject=subject)
    except Exception as e:
        logging.error(f"Ошибка при рендеринге шаблона: {e}")
        exit()


def main():
    """
    Основная функция для отправки писем.
    """
    email_data = load_email_data('data/emails_2025.json')

    for entry in email_data:
        # Пропускаем записи с недостающими полями email или name
        if not entry.get('email') or not entry.get('name') or not entry.get('subject'):
            logging.warning(f"Пропущена запись с недостающими данными: {entry}")
            continue
        
        # Генерация HTML-сообщения
        html_message = generate_html_message(entry['name'], entry['subject'])

        # Отправка email
        send_email(
            to_email=entry['email'],
            subject=entry['subject'],
            html_message=html_message,
            from_email=SMTP_USERNAME,
            image_path=entry['img_postcard']
        )


if __name__ == "__main__":
    main()
