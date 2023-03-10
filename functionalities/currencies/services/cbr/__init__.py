import datetime
import logging
from typing import Dict, Tuple
from xml.etree import ElementTree

from . import service
from . import currencies


logger = logging.getLogger(__name__)


def get_currencies_rates(date: datetime.date, *codes: str) -> Dict[str, Tuple[str, str]]:
    """
    Requests currencies rates with codes from cbr.ru web-service for date.
    Args:
        date: date for currencies rates
        *codes: currencies codes

    Returns:
        Dictionary {'currency code in upper case': ('amount of currency for rate', 'rate')}
    """
    res = dict()
    service_response = service.send_request(date)
    if service_response.status_code == 200:
        xml_root = ElementTree.fromstring(service_response.text)
        for code in codes:
            try:
                rate = service.get_currency_rate_from_xml(code, xml_root)
                if rate is not None:
                    res[code.upper()] = rate
            except service.ServiceChanged as e:
                logger.warning(e)
                break
    else:
        logger.warning(f'Service response: {service_response.status_code}, {service_response.text}')

    return res
