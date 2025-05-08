from datetime import datetime

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
