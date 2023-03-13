import logging
from typing import Union

from binance.error import ClientError

from .service import client, ServiceError

_logger = logging.getLogger(__name__)


def get_btc_busd_rate() -> float:
    try:
        response = client.avg_price(symbol='BTCBUSD')
        return float(response['price'])
    except (ClientError, KeyError, ValueError) as e:
        _logger.warning(e)
        raise ServiceError(f'Perhaps the binance.com service has been changed: {e}')
