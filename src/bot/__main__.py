"""
Anonymous Scream Bot.

Allows users to send anonymous messages ("screams"), react to them,
view stats, and receive daily top screams.

Admins can delete screams. Interaction is via commands and inline buttons.
"""

import sys
import logging
import asyncio
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.filters.callback_data import CallbackData
from aiogram.client.default import DefaultBotProperties
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    BufferedInputFile,
    BotCommand,
)

from bot.config import settings
from bot.services.innoscream import InnoScreamAPI, Scream

subscribers = set(settings.bot.admins)

dp = Dispatcher()
bot = Bot(
    token=settings.bot.token,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)

innoscream = InnoScreamAPI(base_url=settings.innoscream.base_url)


async def set_bot_commands():
    await bot.set_my_commands(
        commands=[
            BotCommand(
                command='start',
                description='Restart bot and subscribe to new screams',
            ),
            BotCommand(
                command='stop',
                description='Stop receiving new screams',
            ),
            BotCommand(
                command='scream',
                description='Post scream',
            ),
            BotCommand(
                command='stats',
                description='Show my statistics',
            ),
            BotCommand(
                command='help',
                description='Show help message',
            ),
        ]
    )


dp.startup.register(set_bot_commands)


class ReactionsCallbackFactory(CallbackData, prefix='reactions'):
    """
    Factory for building and parsing
    reaction callback data in inline keyboards.
    """

    scream_id: int
    reaction: str


@dp.message(Command('help'))
async def show_help(message: Message) -> None:
    """
    Handle /help command.
    Show help message to user.
    """

    subscribers.add(message.from_user.id)
    await message.reply(
        '/start — restart bot and subscribe to new screams\n'
        '/scream [text] — post new scream\n'
        '/stats — see your personal statistics\n'
        '/stop — stop receiving new screams'
    )


@dp.message(CommandStart())
async def start(message: Message) -> None:
    """
    Handle /start command.
    Adds the user to the subscriber list and displays usage help.
    """

    subscribers.add(message.from_user.id)
    await message.answer(
        '👋 Welcome to the Anonymous Scream Bot!\n\n'
        'Send anonymous posts with /scream [text]\n'
        'Use /stats to see your personal statistics.\n'
        'Use /stop to stop receiving updates.'
    )


@dp.message(Command('stop'))
async def stop_updates(message: Message) -> None:
    """
    Handle /stop command.
    Removes the user from the subscriber list.
    """

    subscribers.discard(message.from_user.id)
    await message.answer(
        "👋 You've unsubscribed from updates. "
        'Use /start to join again anytime.'
    )


def build_reactions_keyboard(scream: Scream) -> InlineKeyboardMarkup:
    """
    Construct an inline keyboard with reaction buttons for a given scream.

    Args:
        scream (Scream): The scream object containing reaction data.

    Returns:
        InlineKeyboardMarkup: The keyboard markup.
    """
    kb = InlineKeyboardBuilder()

    kb.row(
        *[
            InlineKeyboardButton(
                text=f'{reaction} {count}',
                callback_data=ReactionsCallbackFactory(
                    scream_id=scream.scream_id,
                    reaction=reaction,
                ).pack(),
            )
            for reaction, count in scream.reactions.items()
        ],
        width=4,
    )

    return kb.as_markup()


def extend_reactions_with_defaults(scream: Scream) -> Scream:
    """
    Ensure all expected reactions exist in the scream,
    initializing with 0 if missing.

    Args:
        scream (Scream): The scream to normalize.

    Returns:
        Scream: The updated scream with default reactions.
    """
    for r in settings.bot.reactions:
        scream.reactions[r] = scream.reactions.get(r, 0)

    return scream


@dp.message(Command('scream'))
async def create_scream(message: Message) -> None:
    """
    Handle /scream command.
    Posts an anonymous message and sends it to all subscribers.
    """

    subscribers.add(message.from_user.id)

    text = message.text.removeprefix('/scream').strip()
    if not text:
        await message.reply('Usage: /scream [your anonymous message]')
        return

    scream = await innoscream.create_scream(message.from_user.id, text)
    extend_reactions_with_defaults(scream)

    kb = build_reactions_keyboard(scream)

    for sub in subscribers:
        await message.bot.send_message(
            chat_id=sub,
            text=f'📢 *Student screams:*\n\n{scream.text}'
            + (
                f'\n\n<code>{scream.scream_id}</code>'
                if sub in settings.bot.admins
                else ''
            ),
            reply_to_message_id=(
                message.message_id if sub == message.from_user.id else None
            ),
            reply_markup=kb,
        )


@dp.callback_query(ReactionsCallbackFactory.filter())
async def create_reaction(
    callback: CallbackQuery,
    callback_data: ReactionsCallbackFactory,
) -> None:
    """
    Handle reaction button press.
    Updates reaction count and refreshes the inline keyboard.
    """

    scream = await innoscream.react_on_scream(
        callback_data.scream_id,
        callback.from_user.id,
        callback_data.reaction,
    )
    extend_reactions_with_defaults(scream)

    await callback.message.edit_reply_markup(
        reply_markup=build_reactions_keyboard(scream)
    )


@dp.message(Command('stats'))
async def get_stats(message: Message) -> None:
    """Handle /stats command.

    Sends the user a summary of their scream statistics,
    including a reaction graph.

    Args:
        message (Message): Incoming message object from the user.
    """
    stats = await innoscream.get_stats(message.from_user.id)
    graph = await innoscream.get_graph(message.from_user.id, 'week')

    await message.answer_photo(
        photo=BufferedInputFile(graph, 'graph.png'),
        caption=(
            "📊 Here's your scream statistics\n\n"
            '*Total number of posts*\n'
            f'{stats.screams_count}\n\n'
            '*Top reactions*\n'
        )
        + '\n'.join(
            f'{r} {c}'
            for r, c in sorted(
                stats.reactions_count.items(),
                key=lambda r: r[1],
                reverse=True,
            )
        ),
    )


@dp.message(Command('delete'), F.from_user.id.in_(settings.bot.admins))
async def delete(message: Message) -> None:
    """
    Handle /delete command.

    Deletes a scream with the given ID. Only accessible to admins.

    Args:
        message (Message): Incoming message object containing the scream ID.
    """
    scream_id = message.text.removeprefix('/delete').strip()
    if not scream_id.isdigit():
        await message.reply('Usage: /delete [scream_id]')
        return

    await innoscream.delete_scream(int(scream_id))

    await message.reply('Scream deleted')


async def send_daily_top_scream():
    """
    Send the top voted scream of the day to all subscribers.

    This function runs in a background loop and triggers once daily
    at midnight.
    """
    while True:
        now = datetime.now()
        nxt = now.replace(
            hour=0, minute=0, second=0, microsecond=0
        ) + timedelta(days=1)
        await asyncio.sleep((nxt - now).total_seconds())

        scream = await innoscream.get_most_voted_scream('day')
        if not scream:
            continue

        meme = await innoscream.generate_meme(scream.scream_id)

        for sub in subscribers:
            await bot.send_photo(
                chat_id=sub,
                photo=BufferedInputFile(meme, 'meme.png'),
                caption=f'🌟 *Top Scream of the Day*\n\n{scream.text}',
            )


async def main() -> None:
    """Start the bot.

    Starts the background task for daily top scream and begins polling.
    """
    asyncio.create_task(send_daily_top_scream())
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
