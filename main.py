from telegram import Update, Poll
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from flask import Flask
from threading import Thread
import logging

# Bot Token और Owner/Group ID भरें
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
OWNER_CHAT_ID = -1001234567890  # Group या Personal Chat ID

# Flask for uptime
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to MCQ Quiz Bot!\n\n"
        "Send questions like this:\n"
        "Question\nOption1\nOption2✅\nOption3\nOption4\nEx: Explanation (optional)\n\n"
        "Separate questions by blank lines."
    )

# Process a single quiz block
async def process_single_question(update: Update, context: ContextTypes.DEFAULT_TYPE, block: str):
    lines = [line.strip() for line in block.strip().split('\n') if line.strip()]
    if len(lines) < 3:
        return

    question = lines[0]
    options = []
    correct_option_id = None
    explanation = None

    for idx, line in enumerate(lines[1:]):
        if line.lower().startswith('ex:'):
            explanation = line[3:].strip()
            break
        if '✅' in line:
            options.append(line.replace('✅', '').strip())
            correct_option_id = idx
        else:
            options.append(line.strip())

    if correct_option_id is None or len(options) < 2:
        return

    explanation = explanation + " @Quiz_Smart" if explanation else "@Quiz_Smart"

    await update.message.reply_poll(
        question=question,
        options=options,
        type=Poll.QUIZ,
        correct_option_id=correct_option_id,
        explanation=explanation,
        is_anonymous=True
    )

    try:
        await context.bot.send_poll(
            chat_id=OWNER_CHAT_ID,
            question=question,
            options=options,
            type=Poll.QUIZ,
            correct_option_id=correct_option_id,
            explanation=explanation,
            is_anonymous=True
        )
    except Exception as e:
        print("Error sending to owner:", e)

# Multiple question handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    blocks = update.message.text.strip().split('\n\n')
    for block in blocks:
        await process_single_question(update, context, block)

# Bot Starter
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    keep_alive()

    app_bot = ApplicationBuilder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app_bot.run_polling()
