# Manager/main.py
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from Manager.bot_token import BOT_TOKEN
from Manager.callbacks import forward_file, edited_message_handler, increment_stats
from Manager.commands import start_command, count_command
from Manager.custom_filters import edited_message_filter, non_edited_message_filter

def main():
    application = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .build()
    )
    
    # 1) Command Handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("count", count_command))
    
    # 2) Specialized Handler for files (new messages)
    file_handler = MessageHandler(filters.Document.ALL | filters.PHOTO | filters.VIDEO, forward_file)
    application.add_handler(file_handler)
    
    # 3) Catch-all Handler for non-edited (new) messages (group=0)
    application.add_handler(MessageHandler(non_edited_message_filter, increment_stats), group=0)
    
    # 4) Handler for edited messages (group=1)
    application.add_handler(MessageHandler(edited_message_filter, edited_message_handler), group=1)
    
    print("Bot Running")
    # Allow updates for both new and edited messages
    application.run_polling(allowed_updates=["message", "edited_message"])
    print("Exiting!!")

if __name__ == "__main__":
    main()
