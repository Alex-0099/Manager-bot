# Manager/callbacks.py
import asyncio
import re
from telegram import Update, InputMediaPhoto, InputMediaVideo
from telegram.ext import ContextTypes
from Manager.rules import FORWARDING_RULES
from Manager.stats import get_stats

# Caches to track media groups and their forwarded message IDs.
media_group_cache = {}       # maps media_group_id -> list of messages from private chat
forwarded_media_groups = {}  # maps media_group_id -> tuple (target_chat_id, forwarded_messages)
forwarded_single_messages = {}

async def process_media_group(media_group_id: str, context: ContextTypes.DEFAULT_TYPE, target_chat_id: str, caption: str):
    # Wait briefly to let all media group items arrive.
    await asyncio.sleep(2)
    messages = media_group_cache.get(media_group_id, [])
    if not messages:
        return

    media = []
    # Build the media group list. Only the first item will have the caption.
    for i, msg in enumerate(messages):
        if msg.photo:
            file_id = msg.photo[-1].file_id  # highest resolution photo
            media.append(InputMediaPhoto(media=file_id, caption=caption if i == 0 else None))
        elif msg.video:
            file_id = msg.video.file_id
            media.append(InputMediaVideo(media=file_id, caption=caption if i == 0 else None))
        # Extend for other media types if needed.

    if media:
        try:
            forwarded = await context.bot.send_media_group(chat_id=target_chat_id, media=media)
            # Save the forwarded messages so we can update their captions later.
            forwarded_media_groups[media_group_id] = (target_chat_id, forwarded)
            print(f"Forwarded media group {media_group_id} to {target_chat_id}")
        except Exception as e:
            print("Error forwarding media group:", e)

    # Clean up cache.
    media_group_cache.pop(media_group_id, None)

async def forward_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    if not message or message.chat.type != "private":
        return

    caption = message.caption if message.caption else ""
    
    if message.media_group_id:
        mg_id = message.media_group_id
        # Cache messages belonging to the same media group.
        media_group_cache.setdefault(mg_id, []).append(message)

        # Check if this message's caption contains a triggering hashtag.
        for hashtag, target_chat_id in FORWARDING_RULES.items():
            if caption and hashtag.lower() in caption.lower():
                # If not forwarded yet, flag and schedule forwarding.
                if mg_id not in forwarded_media_groups:
                    print(f"Media group {mg_id} flagged with hashtag '{hashtag}' from new message.")
                    context.application.create_task(process_media_group(mg_id, context, target_chat_id, caption))
                break
        return
    else:
        # For non-media-group messages, you can implement similar logic and store the forwarded message ID.
        for hashtag, target_chat_id in FORWARDING_RULES.items():
            if caption and hashtag.lower() in caption.lower():
                try:
                    fwd = await message.forward(chat_id=target_chat_id)
                    # Store fwd.message_id in a global dict if you want to update later.
                    print(f"Forwarded non-media message with hashtag '{hashtag}' to {target_chat_id}")
                except Exception as e:
                    print("Error forwarding message:", e)
                break

async def edited_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.edited_message
    if not message or message.chat.type != "private":
        return

    new_caption = message.caption if message.caption else ""
    print("DEBUG: Edited caption:", new_caption)

    # If this is part of a media group:
    if message.media_group_id:
        mg_id = message.media_group_id
        # Update cache with the edited message if not already present.
        if mg_id in media_group_cache:
            if not any(msg.message_id == message.message_id for msg in media_group_cache[mg_id]):
                media_group_cache[mg_id].append(message)
        else:
            media_group_cache[mg_id] = [message]

        # If the media group was already forwarded, update the caption in the forwarded message.
        if mg_id in forwarded_media_groups:
            target_chat_id, forwarded_msgs = forwarded_media_groups[mg_id]
            try:
                # Update the caption of the first forwarded message.
                await context.bot.edit_message_caption(
                    chat_id=target_chat_id,
                    message_id=forwarded_msgs[0].message_id,
                    caption=new_caption
                )
                print(f"Updated caption for forwarded media group {mg_id}")
            except Exception as e:
                print("Error updating caption for media group:", e)
        else:
            # If not forwarded yet, check if the edited caption now contains a hashtag.
            for hashtag, target_chat_id in FORWARDING_RULES.items():
                if new_caption and hashtag.lower() in new_caption.lower():
                    print(f"Media group {mg_id} flagged via edited message with hashtag '{hashtag}'.")
                    context.application.create_task(process_media_group(mg_id, context, target_chat_id, new_caption))
                    break
    else:
        # For non-media-group messages, similar logic applies (update forwarded message's caption).
        # You would need to store the forwarded message ID when initially forwarding.
        for hashtag, target_chat_id in FORWARDING_RULES.items():
            if new_caption and hashtag.lower() in new_caption.lower():
                # Assume you have a dict `forwarded_single_messages` mapping original message_id to (target_chat_id, forwarded_message_id)
                if message.message_id in forwarded_single_messages:
                    target, fwd_msg_id = forwarded_single_messages[message.message_id]
                    try:
                        await context.bot.edit_message_caption(chat_id=target, message_id=fwd_msg_id, caption=new_caption)
                        print(f"Updated caption for forwarded message {message.message_id}")
                    except Exception as e:
                        print("Error updating caption for forwarded message:", e)
                break



#async def debug_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
#       print("Chat ID:", update.effective_chat.id)


async def debug_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("DEBUG update received:", update)



async def increment_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message:
        return  # Skip updates without a message

    # Use the chat ID to update the correct stats
    chat_id = message.chat.id
    current_stats = get_stats(chat_id)

    print(f"DEBUG: Received message: {message.text or 'Non-text'}")

    # Debug: print message type
    print("Received a message update with message ID:", message.message_id)

    if message.text:
        current_stats["text"] += 1
        print("Incremented text count:", current_stats["text"])
    if message.photo:
        current_stats["photo"] += 1
        print("Incremented photo count:", current_stats["photo"])
    if message.video:
        current_stats["video"] += 1
        print("Incremented video count:", current_stats["video"])
    if message.document:
        current_stats["document"] += 1
        print("Incremented document count:", current_stats["document"])
    if message.audio:
        current_stats["audio"] += 1
        print("Incremented audio count:", current_stats["audio"])
    if message.voice:
        current_stats["voice"] += 1
        print("Incremented voice count:", current_stats["voice"])
