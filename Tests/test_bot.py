from telegram.ext import ApplicationBuilder, MessageHandler, filters, CommandHandler
from telegram import Update
from telegram.ext import ContextTypes

BOT_TOKEN = "7882397371:AAGfki935M6D6lVZ6JlanCRVmmTwAKzg7FY"

counts = {"text": 0}

async def increment_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if message and message.text:
        counts["text"] += 1
        print("Text count:", counts["text"])

async def count_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Texts so far: {counts['text']}")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("count", count_command))
    app.add_handler(MessageHandler(filters.ALL, increment_stats))
    app.run_polling()

if __name__ == "__main__":
    main()
