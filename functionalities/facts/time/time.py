from datetime import (
    datetime,
    timedelta,
)


weekdays = {
    0: 'понедельник',
    1: 'вторник',
    2: 'среда',
    3: 'четверг',
    4: 'пятница',
    5: 'суббота',
    6: 'воскресенье',
}

months = {
    1: 'января',
    2: 'февраля',
    3: 'марта',
    4: 'апреля',
    5: 'мая',
    6: 'июня',
    7: 'июля',
    8: 'августа',
    9: 'сентября',
    10: 'октября',
    11: 'ноября',
    12: 'декабря',
}


def today_msk() -> datetime:
    return datetime.utcnow() + timedelta(hours=3)  # MSK = UTC + 3


def yesterday_msk() -> datetime:
    return datetime.utcnow() + timedelta(hours=3, days=-1)


def tomorrow_msk() -> datetime:
    return datetime.utcnow() + timedelta(hours=3, days=1)


def get_today_weekday_msk() -> str:
    today = today_msk()
    return f'Сегодня {weekdays[today.weekday()]}'


def get_yesterday_weekday_msk() -> str:
    yesterday = yesterday_msk()
    weekday = yesterday.weekday()
    if weekday in [0, 1, 3]:
        head = 'Вчера был'
    elif weekday in [2, 4, 5]:
        head = 'Вчера была'
    else:
        head = 'Вчера было'
    return f'{head} {weekdays[weekday]}'


def get_tomorrow_weekday_msk() -> str:
    tomorrow = tomorrow_msk()
    return f'Завтра {weekdays[tomorrow.weekday()]}'


def date_str(d: datetime) -> str:
    return f'{d.day} {months[d.month]} {d.year} года'


def get_today_date_msk() -> str:
    return f'Сегодня {date_str(today_msk())}'


def get_yesterday_date_msk() -> str:
    return f'Вчера было {date_str(yesterday_msk())}'


def get_tomorrow_date_msk() -> str:
    return f'Завтра {date_str(tomorrow_msk())}'


def get_is_leap_year() -> str:
    today = today_msk()
    last_feb_date = datetime(year=today.year, month=3, day=1) - timedelta(days=1)
    if last_feb_date.day == 28:
        return f'Идёт не високосный год'
    else:
        return f'Идёт високосный год'
