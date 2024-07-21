import logging
import os
from telebot import TeleBot
import requests

# Replace with your actual Telegram Bot API key
API_KEY = "7450217483:AAGg7gwLDj7B368rT2it65B8gopfOEWPq6k"
RECEIVER_EMAIL = 'auditbettro@rrbubgb.in'

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
os.makedirs(attachments_dir, exist_ok=True)

def send_email(file_path: str):
    from gmail import GMail, Message
    gmail = GMail('telegramemailbot347@gmail.com', 'hkdwuetxcggzxgnt', True)
    msg = Message(file_path.split('/')[-1], to=RECEIVER_EMAIL, text='Here is your attachment.', attachments=[file_path])
    gmail.send(msg)
    logging.debug(f"Email sent with attachment: {file_path}")

# Handle incoming messages
@bot.message_handler(content_types=["document"])
def handle_document(message):
    document = message.document
    if document:
        file_id = document.file_id
        file_name = document.file_name  # Preserve original filename

        logging.debug(f"Received document: {file_name} with file_id: {file_id}")

        # Get file info (including download URL)
        try:
            file_info = bot.get_file(file_id)
            download_url = f"https://api.telegram.org/file/bot{API_KEY}/{file_info.file_path}"
            logging.debug(f"File info retrieved: {file_info}")
        except Exception as e:
            logging.error(f"Error retrieving file info: {e}")
            bot.reply_to(message, "An error occurred while processing the file.")
            return

        # Download the file and save locally
        try:
            response = requests.get(download_url)
            response.raise_for_status()  # Check for request errors
            file_path = os.path.join(attachments_dir, file_name)
            with open(file_path, "wb") as f:
                f.write(response.content)
            logging.info(f"Attachment saved: {file_path}")
            send_email(file_path)
            bot.reply_to(message, f"Attachment '{file_name}' sent to '{RECEIVER_EMAIL}'")
        except Exception as e:
            logging.error(f"Error downloading or saving file: {e}")
            bot.reply_to(message, "An error occurred while saving the file.")

if __name__ == "__main__":
    # Start the Bot
    try:
        logging.info("Starting bot...")
        bot.infinity_polling()
    except Exception as e:
        logging.critical(f"Critical error: {e}")
