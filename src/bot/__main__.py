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
    InlineKeyboardMarkup, BufferedInputFile
)

from bot.config import settings
from bot.services.innoscream import InnoScreamAPI, Scream

subscribers = set(settings.bot.admins)

dp = Dispatcher()
bot = Bot(
    token=settings.bot.token,
    default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
)

innoscream = InnoScreamAPI(base_url=settings.innoscream.base_url)


class ReactionsCallbackFactory(CallbackData, prefix='reactions'):
    scream_id: int
    reaction: str


@dp.message(CommandStart())
async def start(message: Message) -> None:
    subscribers.add(message.from_user.id)
    await message.reply(
        '👋 Welcome to the Anonymous Scream Bot!\n'
        'Send anonymous messages with /scream [text]\n'
        'Vote on screams using reaction buttons.\n'
        'Use /stats to see your post reactions.\n'
        'Use /exit to stop receiving updates.'
    )


@dp.message(Command('exit'))
async def exit_bot(message: Message) -> None:
    subscribers.discard(message.chat.id)
    await message.reply('👋 You\'ve unsubscribed from updates. Use /start to join again anytime.')


def build_reactions_keyboard(scream: Scream) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.row(
        *[
            InlineKeyboardButton(
                text=f'{reaction} {count}',
                callback_data=ReactionsCallbackFactory(
                    scream_id=scream.scream_id,
                    reaction=reaction,
                ).pack()
            ) for reaction, count in scream.reactions.items()
        ],
        width=4,
    )

    return kb.as_markup()


def extend_reactions_with_defaults(scream: Scream) -> Scream:
    for r in settings.bot.reactions:
        scream.reactions[r] = scream.reactions.get(r, 0)

    return scream


@dp.message(Command('scream'))
async def create_scream(message: Message) -> None:
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
            text=f'📢 *Student screams:*\n\n{scream.text}' + (
                f'\n\n`{scream.scream_id}`'
                if sub in settings.bot.admins else ''
            ),
            reply_to_message_id=message.message_id if sub == message.from_user.id else None,
            reply_markup=kb
        )


@dp.callback_query(ReactionsCallbackFactory.filter())
async def create_reaction(
        callback: CallbackQuery,
        callback_data: ReactionsCallbackFactory
) -> None:
    scream = await innoscream.react_on_scream(
        callback_data.scream_id,
        callback.from_user.id,
        callback_data.reaction,
    )
    extend_reactions_with_defaults(scream)

    await callback.message.edit_reply_markup(reply_markup=build_reactions_keyboard(scream))


@dp.message(Command('stats'))
async def get_stats(message: Message) -> None:
    stats = await innoscream.get_stats(message.from_user.id)
    graph = await innoscream.get_graph(message.from_user.id, 'week')

    await message.reply_photo(
        photo=BufferedInputFile(graph, 'graph.png'),
        caption=(
                    '📊 Here\'s your scream statistics\n\n'
                    '*Total number of posts*\n'
                    f'{stats.screams_count}\n\n'
                    '*Top reactions*\n'
                ) + '\n'.join(
            f'{r} {c}' for r, c in
            sorted(
                stats.reactions_count.items(),
                key=lambda r: r[1],
                reverse=True,
            )
        )
    )


@dp.message(Command('delete'), F.from_user.id.in_(settings.bot.admins))
async def delete(message: Message) -> None:
    scream_id = message.text.removeprefix('/delete').strip()
    if not scream_id.isdigit():
        await message.reply('Usage: /delete [scream_id]')
        return

    await innoscream.delete_scream(int(scream_id))

    await message.reply('Scream deleted')


async def send_daily_top_scream():
    while True:
        now = datetime.now()
        nxt = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
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
    asyncio.create_task(send_daily_top_scream())
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
