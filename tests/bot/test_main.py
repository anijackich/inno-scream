import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch, MagicMock

from aiogram.types import Message, User, Chat, CallbackQuery

from src.bot.services.innoscream.models import Scream, Stats


patch('aiogram.client.bot.Bot.__init__', return_value=None).start()
patch(
    'src.bot.config.settings.bot.token', 'valid:test_token_for_testing'
).start()


@pytest.fixture
def mock_message():
    message = MagicMock(spec=Message)
    message.from_user = MagicMock(spec=User)
    message.from_user.id = 123
    message.chat = MagicMock(spec=Chat)
    message.chat.id = 123
    message.text = ''
    message.reply = AsyncMock()
    message.answer = AsyncMock()
    message.answer_photo = AsyncMock()
    message.bot = MagicMock()
    message.bot.send_message = AsyncMock()
    message.bot.send_photo = AsyncMock()
    message.message_id = 456
    return message


@pytest.fixture
def mock_callback_query():
    callback = MagicMock(spec=CallbackQuery)
    callback.from_user = MagicMock(spec=User)
    callback.from_user.id = 123
    callback.message = MagicMock(spec=Message)
    callback.message.edit_reply_markup = AsyncMock()
    return callback


@pytest.fixture
def mock_innoscream_api():
    with patch('src.bot.__main__.innoscream') as mock_api:
        mock_api.create_scream = AsyncMock()
        mock_api.get_scream = AsyncMock()
        mock_api.delete_scream = AsyncMock()
        mock_api.react_on_scream = AsyncMock()
        mock_api.get_stats = AsyncMock()
        mock_api.get_graph = AsyncMock()
        mock_api.get_most_voted_scream = AsyncMock()
        mock_api.generate_meme = AsyncMock()
        yield mock_api


@pytest.fixture
def sample_scream():
    return Scream(
        scream_id=1,
        user_id=123,
        text='Test scream',
        created_at=datetime.now(),
        reactions={'👍': 5, '👎': 2},
    )


@pytest.fixture
def sample_stats():
    return Stats(screams_count=10, reactions_count={'👍': 15, '👎': 5})


@pytest.mark.asyncio
async def test_start_command(mock_message):
    from src.bot.__main__ import start, subscribers

    subscribers.clear()

    await start(mock_message)

    assert mock_message.from_user.id in subscribers
    mock_message.answer.assert_called_once()
    assert (
        'Welcome to the Anonymous Scream Bot'
        in mock_message.answer.call_args[0][0]
    )


@pytest.mark.asyncio
async def test_exit_command(mock_message):
    from src.bot.__main__ import stop_updates, subscribers

    subscribers.add(mock_message.chat.id)

    await stop_updates(mock_message)

    assert mock_message.chat.id not in subscribers
    mock_message.answer.assert_called_once()
    assert 'unsubscribed' in mock_message.answer.call_args[0][0]


@pytest.mark.asyncio
async def test_build_reactions_keyboard(sample_scream):
    from src.bot.__main__ import build_reactions_keyboard

    keyboard = build_reactions_keyboard(sample_scream)

    assert keyboard is not None
    assert len(keyboard.inline_keyboard) > 0
    assert len(keyboard.inline_keyboard[0]) == len(sample_scream.reactions)


@pytest.mark.asyncio
async def test_extend_reactions_with_defaults(sample_scream):
    with patch('src.bot.__main__.settings') as mock_settings:
        mock_settings.bot.reactions = ['👍', '👎', '❤️', '😂']

        from src.bot.__main__ import extend_reactions_with_defaults

        result = extend_reactions_with_defaults(sample_scream)

        assert '👍' in result.reactions
        assert '👎' in result.reactions
        assert '❤️' in result.reactions
        assert '😂' in result.reactions
        assert result.reactions['👍'] == 5
        assert result.reactions['👎'] == 2
        assert result.reactions['❤️'] == 0
        assert result.reactions['😂'] == 0


@pytest.mark.asyncio
async def test_create_scream_no_text(mock_message):
    mock_message.text = '/scream'

    from src.bot.__main__ import create_scream

    await create_scream(mock_message)

    mock_message.reply.assert_called_once()
    assert 'Usage:' in mock_message.reply.call_args[0][0]


@pytest.mark.asyncio
async def test_create_scream_with_text(
    mock_message, mock_innoscream_api, sample_scream
):
    mock_message.text = '/scream Test message'
    mock_innoscream_api.create_scream.return_value = sample_scream

    with patch('src.bot.__main__.subscribers', {123, 456}):
        with patch('src.bot.__main__.settings') as mock_settings:
            mock_settings.bot.admins = [456]
            mock_settings.bot.reactions = ['👍', '👎']

            from src.bot.__main__ import create_scream

            await create_scream(mock_message)

            mock_innoscream_api.create_scream.assert_called_once_with(
                123, 'Test message'
            )
            assert mock_message.bot.send_message.call_count == 2


@pytest.mark.asyncio
async def test_create_reaction(
    mock_callback_query, mock_innoscream_api, sample_scream
):
    mock_innoscream_api.react_on_scream.return_value = sample_scream

    from src.bot.__main__ import ReactionsCallbackFactory, create_reaction

    callback_data = ReactionsCallbackFactory(scream_id=1, reaction='👍')

    await create_reaction(mock_callback_query, callback_data)

    mock_innoscream_api.react_on_scream.assert_called_once_with(1, 123, '👍')
    mock_callback_query.message.edit_reply_markup.assert_called_once()


@pytest.mark.asyncio
async def test_get_stats(mock_message, mock_innoscream_api, sample_stats):
    mock_innoscream_api.get_stats.return_value = sample_stats
    mock_innoscream_api.get_graph.return_value = b'graph_image_bytes'

    from src.bot.__main__ import get_stats

    await get_stats(mock_message)

    mock_innoscream_api.get_stats.assert_called_once_with(123)
    mock_innoscream_api.get_graph.assert_called_once_with(123, 'week')
    mock_message.answer_photo.assert_called_once()


@pytest.mark.asyncio
async def test_delete_no_id(mock_message, mock_innoscream_api):
    mock_message.text = '/delete'

    from src.bot.__main__ import delete

    await delete(mock_message)

    mock_message.reply.assert_called_once()
    assert 'Usage:' in mock_message.reply.call_args[0][0]
    mock_innoscream_api.delete_scream.assert_not_called()


@pytest.mark.asyncio
async def test_delete_with_id(mock_message, mock_innoscream_api):
    mock_message.text = '/delete 1'

    from src.bot.__main__ import delete

    await delete(mock_message)

    mock_innoscream_api.delete_scream.assert_called_once_with(1)
    mock_message.reply.assert_called_once_with('Scream deleted')


@pytest.mark.asyncio
async def test_send_daily_top_scream(mock_innoscream_api, sample_scream):
    mock_innoscream_api.get_most_voted_scream.return_value = sample_scream
    mock_innoscream_api.generate_meme.return_value = b'meme_image_bytes'

    with patch('src.bot.__main__.subscribers', {123, 456}):
        with patch('src.bot.__main__.bot') as mock_bot:
            mock_bot.send_photo = AsyncMock()
            with patch('src.bot.__main__.asyncio.sleep', AsyncMock()):

                async def run_once():
                    scream = await mock_innoscream_api.get_most_voted_scream(
                        'day'
                    )
                    if not scream:
                        return

                    meme = await mock_innoscream_api.generate_meme(
                        scream.scream_id
                    )

                    for sub in {123, 456}:
                        await mock_bot.send_photo(
                            chat_id=sub,
                            photo=meme,
                            caption=(
                                f'🌟 *Top Scream of the Day*\n\n{scream.text}'
                            ),
                        )

                await run_once()

                mock_innoscream_api.get_most_voted_scream.assert_called_once_with('day')  # noqa: E501 # fmt: skip
                mock_innoscream_api.generate_meme.assert_called_once_with(1)
                assert mock_bot.send_photo.call_count == 2


@pytest.mark.asyncio
async def test_send_daily_top_scream_no_scream(mock_innoscream_api):
    mock_innoscream_api.get_most_voted_scream.return_value = None

    with patch('src.bot.__main__.bot') as mock_bot:
        mock_bot.send_photo = AsyncMock()
        with patch('src.bot.__main__.asyncio.sleep', AsyncMock()):

            async def run_once():
                scream = await mock_innoscream_api.get_most_voted_scream('day')
                if not scream:
                    return

                meme = await mock_innoscream_api.generate_meme(
                    scream.scream_id
                )

                for sub in {123, 456}:
                    await mock_bot.send_photo(
                        chat_id=sub,
                        photo=meme,
                        caption=f'🌟 *Top Scream of the Day*\n\n{scream.text}',
                    )

            await run_once()

            mock_innoscream_api.get_most_voted_scream.assert_called_once_with(
                'day'
            )
            mock_innoscream_api.generate_meme.assert_not_called()
            mock_bot.send_photo.assert_not_called()
