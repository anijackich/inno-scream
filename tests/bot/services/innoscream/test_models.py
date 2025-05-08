from datetime import datetime, timezone

from src.bot.services.innoscream.models import Scream, Stats


def test_scream_model():
    data = {
        'scream_id': 1,
        'user_id': 123,
        'text': 'Test scream',
        'created_at': datetime.now(),
        'reactions': {'👍': 5, '👎': 2},
    }

    scream = Scream(**data)

    assert scream.scream_id == data['scream_id']
    assert scream.user_id == data['user_id']
    assert scream.text == data['text']
    assert scream.created_at == data['created_at']
    assert scream.reactions == data['reactions']


def test_scream_model_with_string_datetime():
    now = datetime.now()
    data = {
        'scream_id': 1,
        'user_id': 123,
        'text': 'Test scream',
        'created_at': now.isoformat(),
        'reactions': {'👍': 5, '👎': 2},
    }

    scream = Scream(**data)

    assert scream.scream_id == data['scream_id']
    assert scream.user_id == data['user_id']
    assert scream.text == data['text']
    assert isinstance(scream.created_at, datetime)
    assert scream.reactions == data['reactions']


def test_scream_model_with_different_datetime_formats():
    formats = [
        datetime.now(timezone.utc),
        '2025-05-08T12:34:56.789012',
        '2025-05-08T12:34:56Z',
        '2025-05-08T12:34:56+00:00',
    ]

    for dt_format in formats:
        data = {
            'scream_id': 1,
            'user_id': 123,
            'text': 'Test scream',
            'created_at': dt_format,
            'reactions': {'👍': 5, '👎': 2},
        }

        scream = Scream(**data)
        assert isinstance(scream.created_at, datetime)


def test_scream_model_with_empty_reactions():
    data = {
        'scream_id': 1,
        'user_id': 123,
        'text': 'Test scream',
        'created_at': datetime.now(),
        'reactions': {},
    }

    scream = Scream(**data)
    assert scream.reactions == {}


def test_scream_model_with_integer_values():
    data = {
        'scream_id': 2147483647,
        'user_id': 9223372036854775807,
        'text': 'Test scream',
        'created_at': datetime.now(),
        'reactions': {'👍': 0, '👎': 0},
    }

    scream = Scream(**data)
    assert scream.scream_id == 2147483647
    assert scream.user_id == 9223372036854775807


def test_scream_model_with_long_text():
    long_text = 'A' * 10000
    data = {
        'scream_id': 1,
        'user_id': 123,
        'text': long_text,
        'created_at': datetime.now(),
        'reactions': {'👍': 5, '👎': 2},
    }

    scream = Scream(**data)
    assert scream.text == long_text
    assert len(scream.text) == 10000


def test_stats_model():
    data = {'screams_count': 10, 'reactions_count': {'👍': 15, '👎': 5}}

    stats = Stats(**data)

    assert stats.screams_count == data['screams_count']
    assert stats.reactions_count == data['reactions_count']


def test_stats_model_empty_reactions():
    data = {'screams_count': 0, 'reactions_count': {}}

    stats = Stats(**data)

    assert stats.screams_count == 0
    assert stats.reactions_count == {}


def test_stats_model_with_many_reactions():
    reactions = {
        '👍': 10,
        '👎': 5,
        '❤️': 20,
        '😂': 15,
        '😡': 3,
        '🎉': 7,
        '🔥': 12,
        '👀': 8,
        '🤔': 4,
        '👏': 9,
    }
    data = {'screams_count': 100, 'reactions_count': reactions}

    stats = Stats(**data)

    assert stats.screams_count == 100
    assert stats.reactions_count == reactions
    assert len(stats.reactions_count) == 10
    assert sum(stats.reactions_count.values()) == 93


def test_stats_model_with_extreme_values():
    data = {
        'screams_count': 2147483647,  # Max 32-bit integer
        'reactions_count': {'👍': 2147483647, '👎': 2147483647},
    }

    stats = Stats(**data)

    assert stats.screams_count == 2147483647
    assert stats.reactions_count['👍'] == 2147483647
    assert stats.reactions_count['👎'] == 2147483647
