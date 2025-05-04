from datetime import datetime, timedelta, timezone
from calendar import monthrange
from typing import Literal

from sqlalchemy import select, func, extract
from sqlalchemy.ext.asyncio import AsyncSession

from . import schemas
from api import models
from api.external.quickchart import QuickChart, Chart, ChartData, Dataset

WEEKDAYS = {
    1: 'Mon',
    2: 'Tue',
    3: 'Wed',
    4: 'Thu',
    5: 'Fri',
    6: 'Sat',
    0: 'Sun',
}

MONTHS = {
    1: 'Jan',
    2: 'Feb',
    3: 'Mar',
    4: 'Apr',
    5: 'May',
    6: 'Jun',
    7: 'Jul',
    8: 'Aug',
    9: 'Sep',
    10: 'Oct',
    11: 'Nov',
    12: 'Dec',
}


async def get_stats(
        session: AsyncSession,
        user_id: int
) -> schemas.Stats:
    screams_count = await session.execute(
        select(func.count())
        .select_from(models.Scream)
        .where(models.Scream.user_id == user_id)
    )

    reactions = await session.execute(
        select(models.Reaction.reaction, func.count(models.Reaction.id))
        .join(models.Scream, models.Scream.id == models.Reaction.scream_id)
        .where(models.Scream.user_id == user_id)
        .group_by(models.Reaction.reaction)
    )

    return schemas.Stats(
        screams_count=screams_count.scalar() or 0,
        reactions_count={
            r.reaction: r.count
            for r in reactions.all()
        }
    )


async def get_graph(
        session: AsyncSession,
        user_id: int,
        period: Literal['week', 'month', 'year'],
) -> bytes:
    today = (
        datetime
        .now(tz=timezone(timedelta(hours=+3)))
        .replace(hour=0, minute=0, second=0, microsecond=0)
    )

    match period:
        case 'week':
            extract_field = 'dow'

            start = today - timedelta(days=today.weekday())
            end = start + timedelta(days=6, hours=23, minutes=59, seconds=59)

            labels = list(WEEKDAYS.values())
            to_data = lambda d: [d.get(dow, 0) for dow in WEEKDAYS.keys()]

            title = f'Screams from {start.strftime('%b %d')} to {end.strftime('%b %d')}'
        case 'month':
            extract_field = 'day'

            start = today.replace(day=1)
            days = monthrange(today.year, today.month)[1]
            end = start + timedelta(days=days) - timedelta(seconds=1)

            labels = list(map(str, range(1, days + 1)))
            to_data = lambda d: [d.get(day, 0) for day in range(1, days + 1)]

            title = f'Screams for {today.strftime('%b %Y')}'
        case 'year':
            extract_field = 'month'

            start = today.replace(month=1, day=1)
            end = today.replace(month=12, day=31)

            labels = list(MONTHS.values())
            to_data = lambda d: [d.get(month, 0) for month in MONTHS.keys()]

            title = f'Screams for {start.strftime('%Y')} year'
        case _:
            raise ValueError('Invalid period')

    screams_count = await session.execute(
        select(
            extract(extract_field, models.Scream.created_at),
            func.count(models.Scream.id),
        )
        .where(models.Scream.user_id == user_id)
        .where(models.Scream.created_at >= start)
        .where(models.Scream.created_at <= end)
        .group_by(extract(extract_field, models.Scream.created_at))
        .order_by(extract(extract_field, models.Scream.created_at))
    )

    chart = Chart(
        type='bar',
        data=ChartData(
            labels=labels,
            datasets=[
                Dataset(
                    label='posts',
                    data=to_data({d[0]: d[1] for d in screams_count.all()}),
                    backgroundColor='black',
                )
            ]
        ),
        options={
            'legend': {
                'display': False
            },
            'title': {
                'display': True,
                'text': title,
                'fontFamily': '\'Montserrat\', sans-serif',
                'fontStyle': 'italic',
            },
            'scales': {
                'yAxes': [{
                    'gridLines': {
                        'display': False,
                    },
                    'ticks': {
                        'beginAtZero': True,
                        'stepSize': 1,
                        'fontFamily': '\'Montserrat\', sans-serif',

                    }
                }],
                'xAxes': [{
                    'ticks': {
                        'fontFamily': '\'Montserrat\', sans-serif',
                    }
                }]
            },
            'plugins': {
                'roundedBars': True,
            },
        },
    )

    return await QuickChart().chart(chart)
