# Manager/commands.py
from telegram import Update
from telegram.ext import ContextTypes
from Manager.stats import get_stats


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hello! I'm your Manager Bot.")

async def count_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat.id
    current_stats = get_stats(chat_id)
    
    reply_text = (
        f"**Message Counts for this chat**\n"
        f"Texts: {current_stats['text']}\n"
        f"Photos: {current_stats['photo']}\n"
        f"Videos: {current_stats['video']}\n"
        f"Documents: {current_stats['document']}\n"
        f"Audios: {current_stats['audio']}\n"
        f"Voices: {current_stats['voice']}\n"
    )
    await update.message.reply_text(reply_text, parse_mode="Markdown")
