import logging
import os
import re
import threading
from telebot import TeleBot
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.mime.text import MIMEText

# Replace with your actual Telegram Bot API key
API_KEY = "7450217483:AAF47whHcWg4gi0OLQRcDF3iZ2rpRvMx4JY"
DEFAULT_RECEIVER_EMAIL = 'auditbettro@rrbubgb.in'

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Create file handler which logs even debug messages
fh = logging.FileHandler('bot.log')
fh.setLevel(logging.DEBUG)

# Create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# Create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)

# Create a TeleBot object
bot = TeleBot(API_KEY)

# Define attachments directory (create if it doesn't exist)
attachments_dir = "attachments"
# Global variables to keep track of attachments and receiver email
attachments = []
current_receiver_email = None
timer = None

# Timeout in seconds (e.g., 10 seconds of inactivity triggers email sending)
TIMEOUT = 10
os.makedirs(attachments_dir, exist_ok=True)

def send_email(attachments, recipient_email, smtp_server='smtp.gmail.com', smtp_port=587):
    # Create a multipart message
    msg = MIMEMultipart()
    msg['From'] = 'telegramemailbot347@gmail.com'
    msg['To'] = recipient_email
    msg['Subject'] = "Attachments"

    # Attach the email body
    msg.attach(MIMEText("Please find attached your requested documents.", 'plain'))

    # Attach files
    for file_path in attachments:
        if os.path.exists(file_path):
            with open(file_path, 'rb') as file:
                # Create a MIMEBase instance
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(file.read())
                encoders.encode_base64(part)
                # Add header with the filename
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {os.path.basename(file_path)}',
                )
                # Attach the file to the email
                msg.attach(part)
        else:
            logging.debug(f"File not found: {file_path}")
        os.remove(file_path)
    # Send the email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Upgrade to a secure connection
            server.login('telegramemailbot347@gmail.com', 'hkdwuetxcggzxgnt')
            server.send_message(msg)
            logging.debug('Email sent successfully.')
    except Exception as e:
        logging.debug(f"Failed to send email. Error: {e}")

def reset_timer():
    global timer
    if timer:
        timer.cancel()
    timer = threading.Timer(TIMEOUT, send_attachments)
    timer.start()

@bot.message_handler(content_types=["document"])
def handle_document(message):
    global attachments, current_receiver_email

    document = message.document
    file_id = document.file_id
    file_name = document.file_name  # Preserve original filename
    caption = message.caption
    logging.debug(f"Received document: {file_name} with file_id: {file_id}")

    # Determine the receiver email from captions
    if not current_receiver_email:
        current_receiver_email = caption if is_valid_email(caption) else DEFAULT_RECEIVER_EMAIL

    # Get file info (including download URL)
    try:
        file_info = bot.get_file(file_id)
        download_url = f"https://api.telegram.org/file/bot{API_KEY}/{file_info.file_path}"
        response = requests.get(download_url)
        response.raise_for_status()  # Check for request errors

        # Save the document
        file_path = os.path.join(attachments_dir, file_name)
        with open(file_path, "wb") as f:
            f.write(response.content)
        logging.info(f"Attachment saved: {file_path}")

        # Add to user's attachments
        attachments.append(file_path)
        bot.reply_to(message, f"Attachment saved: {file_name}")

        # Reset the timer each time a document is received
        reset_timer()
        bot.reply_to(message, f"Attachment sent to '{current_receiver_email}'")
    except Exception as e:
        logging.error(f"Error downloading or saving file: {e}")
        bot.reply_to(message, "An error occurred while saving the file.")

def is_valid_email(email):
    # Define the regular expression for a valid email address
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    # Use re.match to check if the email matches the regex
    return re.match(regex, email) is not None if email else False
def send_attachments():
    global attachments, current_receiver_email, timer

    if attachments:
        send_email(attachments, current_receiver_email)
        # Clear attachments and receiver email after sending
        attachments = []
        current_receiver_email = None

    # Clear the timer
    timer = None

if __name__ == "__main__":
    # Start the Bot
    try:
        logging.info("Starting bot...")
        bot.infinity_polling()
    except Exception as e:
        logging.critical(f"Critical error: {e}")
