import datetime
from typing import Tuple, Optional
from xml.etree import ElementTree

import requests


class _RequestContent:
    def __init__(self):
        self.root = ElementTree.Element(
            'soap:Envelope',
            attrib={
                'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
                'xmlns:xsd': 'http://www.w3.org/2001/XMLSchema',
                'xmlns:soap': 'http://schemas.xmlsoap.org/soap/envelope/',
            }
        )
        body = ElementTree.Element('soap:Body')
        get_curs_on_date = ElementTree.Element(
            'GetCursOnDate',
            attrib={
                'xmlns': 'http://web.cbr.ru/',
            }
        )
        self.on_date = ElementTree.Element('On_date')

        self.root.append(body)
        body.append(get_curs_on_date)
        get_curs_on_date.append(self.on_date)

    def get(self, date: datetime.date) -> bytes:
        self.on_date.text = f"{date.year}-{str(date.month).rjust(2, '0')}-{str(date.day).rjust(2, '0')}"
        return ElementTree.tostring(
            self.root,
            encoding='utf-8',
            xml_declaration=True,
        )


_request_content = _RequestContent()


def send_request(date: datetime.date) -> requests.Response:
    """
    Send request GetCursOnDate to web-service https://cbr.ru/DailyInfoWebServ/DailyInfo.asmx
    Description: https://cbr.ru/DailyInfoWebServ/DailyInfo.asmx?op=GetCursOnDate
    Args:
        date: currency rate date

    Returns:
        web-service response
    """
    url = 'https://cbr.ru/DailyInfoWebServ/DailyInfo.asmx'
    headers = {
        'Content-Type': 'text/xml; charset=utf-8',
        'SOAPAction': 'http://web.cbr.ru/GetCursOnDate',
    }
    return requests.post(
        url,
        data=_request_content.get(date),
        headers=headers,
    )


class ServiceChanged(Exception):
    pass


def get_currency_rate_from_xml(currency_code: str, response_root: ElementTree.Element) -> Optional[Tuple[str, str]]:
    """
    Returns tuple (amount of currency, currency rate)
    Args:
        currency_code: alphabetic currency code
        response_root: xml response of service

    Returns:
        (amount of currency, currency rate)
    """
    for el in response_root.iter():
        try:
            if el.tag == 'ValuteCursOnDate' and el.find('VchCode').text.lower() == currency_code.lower():
                return el.find('Vnom').text, el.find('Vcurs').text
        except AttributeError:
            raise ServiceChanged('Perhaps the structure of cbr.ru service response has been changed')
