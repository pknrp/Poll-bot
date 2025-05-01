from telegram import Update, Poll
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from flask import Flask
from threading import Thread
import logging

# Bot Token और Owner Chat ID भरें
BOT_TOKEN = "7343225665:AAFezP5GGyjDo4-jjYCORmc3j0t7WjwXLrY"
OWNER_CHAT_ID = -1002105439688  # Group या Personal Chat ID

# Flask app to keep bot alive (Render.com/uptime tools)
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

# /help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Quiz Bot Features:\n\n"
        "1. Send questions like:\n"
        "Question\nOption1\nOption2✅\nOption3\nOption4\nEx: Explanation\n\n"
        "2. Send multiple questions together using blank lines.\n"
        "3. Correct option should have ✅\n"
        "4. Optional explanation starts with 'Ex:'\n"
        "5. All quizzes will be auto-posted to group too.\n"
        "6. '@Quiz_Smart' tag is added automatically.\n\n"
        "Use /owner to see magic!"
    )

# /owner command
async def owner_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hey baby how are u..🥰")

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

    # Send to sender
    await update.message.reply_poll(
        question=question,
        options=options,
        type=Poll.QUIZ,
        correct_option_id=correct_option_id,
        explanation=explanation,
        is_anonymous=True
    )

    # Also send to group/owner
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

# Handler for text messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    blocks = update.message.text.strip().split('\n\n')
    for block in blocks:
        await process_single_question(update, context, block)

# Run the bot
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    keep_alive()

    app_bot = ApplicationBuilder().token(BOT_TOKEN).build()

    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CommandHandler("help", help_command))
    app_bot.add_handler(CommandHandler("owner", owner_command))
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app_bot.run_polling()
