# Manager/stats.py

# Global dictionary for chat-specific stats.
stats = {}

def get_stats(chat_id):
    """Retrieve the stats dictionary for a specific chat, initializing it if necessary."""
    if chat_id not in stats:
        stats[chat_id] = {
            "text": 0,
            "photo": 0,
            "video": 0,
            "document": 0,
            "audio": 0,
            "voice": 0,
        }
    return stats[chat_id]

def reset_stats(chat_id):
    """Reset stats for a specific chat."""
    stats[chat_id] = {
        "text": 0,
        "photo": 0,
        "video": 0,
        "document": 0,
        "audio": 0,
        "voice": 0,
    }
