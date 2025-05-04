import logging
import asyncio
import sys
import requests
from os import getenv
from datetime import datetime, timedelta

from aiogram import F
from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import BufferedInputFile, Message, CallbackQuery
from aiogram.utils import markdown as md
from aiogram.utils.keyboard import InlineKeyboardBuilder

from api.screams.schemas import Scream
from api.config import settings

TOKEN = getenv("BOT_TOKEN")
ADMIN_IDS = {int(x) for x in getenv("ADMIN_IDS", "").split(",") if x}

chat_ids = set()

dp = Dispatcher()
router = Router()
emojis = ["🤡", "🔥", "💀"];
scream_messages: dict[int, list[tuple[int, int]]] = {}


def build_url(endpoint: str) -> str:
    return f"http://{settings.host}:{settings.port}/{endpoint}"

@dp.message(CommandStart())
async def start(message: Message) -> None:
    chat_ids.add(message.chat.id)
    await message.reply(
        "👋 Welcome to the Anonymous Scream Bot!\n"
        "Send anonymous messages with /scream [text]\n"
        "Vote on screams using reaction buttons.\n"
        "Use /stats to see your post reactions.\n"
        "Use /exit to stop receiving updates."
    )

@dp.message(Command("exit"))
async def exit_bot(message: Message) -> None:
    chat_ids.discard(message.chat.id)
    await message.reply("👋 You've unsubscribed from updates. Use /start to join again anytime.")

@dp.message(Command("scream"))
async def scream(message: Message) -> None:
    if not message.text or not message.from_user or not message.from_user.id or not message.bot:
        print("Error while processing the message")
        await message.reply("something went wrong")
        return
    text = message.text.removeprefix("/scream").strip()
    if not text:
        await message.reply("Usage: /scream [your anonymous message]")
        return

    scream_response = requests.post(build_url("screams"), json={
        "user_id": message.from_user.id,
        "text": text
    })
    scream_response.raise_for_status()
    scream_response = Scream.model_validate(scream_response.json())

    kb = InlineKeyboardBuilder()
    for emoji in emojis:
        kb.button(text=f"0 {emoji}", callback_data=f"upvote:{scream_response.scream_id}:{emoji}")
               
    scream_messages[scream_response.scream_id] = []
    for cid in chat_ids:
        sent_message = await message.bot.send_message(
            chat_id=cid,
            text=md.text(
                md.hbold("📢 Student screams:"), "\n",
                md.text(scream_response.text)
            ),
            reply_markup=kb.as_markup()
        )
        scream_messages[scream_response.scream_id].append((cid, sent_message.message_id))

@dp.callback_query(F.data.startswith("upvote:"))
async def handle_upvote(callback: CallbackQuery):
    data = callback.data
    if not data or not callback.bot:
        print(f"error with callback handler")
        return
    _, scream_id, emoji = data.split(":")
    user_id = callback.from_user.id

    upvote_response = requests.post(build_url(f"screams/{scream_id}/react"), json={
        "scream_id": scream_id,
        "user_id": user_id,
        "reaction": emoji
    })
    upvote_response.raise_for_status()

    stats_response = requests.get(build_url(f"screams/{scream_id}"))
    stats_response.raise_for_status()
    stats_response = stats_response.json()

    kb = InlineKeyboardBuilder()
    for emoji in emojis:
        count = stats_response["reactions"].get(emoji, 0)
        kb.button(text=f"{count} {emoji}", callback_data=f"upvote:{scream_id}:{emoji}")
    kb.adjust(len(emojis))

    for cid, mid in scream_messages.get(int(scream_id), []):
        try:
            await callback.bot.edit_message_reply_markup(chat_id=cid, message_id=mid, reply_markup=kb.as_markup())
        except Exception:
            pass

@dp.message(Command("stats"))
async def stats(message: Message) -> None:
    if not message.from_user or not message.from_user.id:
        print("Error while processing the message")
        await message.reply("something went wrong")
        return
    user_id = message.from_user.id

    grapth_response = requests.get(build_url(f"analytics/{user_id}/graph"), params={"period": "week"})
    grapth_response.raise_for_status()

    input_file = BufferedInputFile(file=grapth_response.content, filename="stats.jpg")

    stats_response = requests.get(build_url(f"analytics/{user_id}/stats"))
    stats_response.raise_for_status()
    reactions = stats_response.json().get("reactions_count", dict)

    lines = ["📊 Here's your top reactions to your posts:\n"]
    for emoji, count in sorted(reactions.items(), key=lambda x: x[1], reverse=True):
        lines.append(f"{emoji} – {count} vote{'s' if count != 1 else ''}")
    caption = "\n".join(lines)

    await message.reply_photo(photo=input_file, caption=caption)

@dp.message(Command("delete"))
async def delete(message: Message) -> None:
    if not message.from_user or message.from_user.id not in ADMIN_IDS:
        await message.reply("You are not authorized to delete posts")
        return

    if not message.text:
        await message.reply("Usage: /delete [post_id]")
        return

    scream_id = message.text.removeprefix("/delete").strip()
    if not scream_id.isdigit():
        await message.reply("Usage: /delete [post_id]")
        return

    delete_response = requests.delete(build_url(f"screams/{scream_id}"))
    delete_response.raise_for_status()
    await message.reply("Post deleted")

async def send_daily_top_scream(bot: Bot):
    while True:
        now = datetime.now()
        nxt = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        await asyncio.sleep((nxt - now).total_seconds())

        response = requests.get(build_url("screams/getMostVoted"), params={"period": "week"})
        response.raise_for_status()
        top_screams = response.json()

        for cid in chat_ids:
            try:
                await bot.send_message(
                    chat_id=cid,
                    text=md.text(md.hbold("🌟 Top Scream of the Day:"), "\n", md.text(top_screams["text"]))
                )
            except Exception:
                pass

async def main() -> None:
    if TOKEN == None:
        print("Please set the BOT_TOKEN env variable")
        return

    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    asyncio.create_task(send_daily_top_scream(bot))
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
