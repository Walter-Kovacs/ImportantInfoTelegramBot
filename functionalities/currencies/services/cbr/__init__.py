import datetime
from typing import Dict, Tuple


def get_currencies_rates(date: datetime.date, *codes) -> Dict[str, Tuple[str, str]]:
    """
    Requests currencies rates with codes from cbr.ru web-service for date.
    Args:
        date: date for currencies rates
        *codes: currencies codes

    Returns:
        Dictionary {'currency code': ('amount of currency for rate', 'rate')}
    """
    pass
