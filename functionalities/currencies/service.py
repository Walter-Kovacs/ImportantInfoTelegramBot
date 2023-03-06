import datetime
from typing import Tuple
from xml.etree import ElementTree

import requests


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
        data=create_request_content(date),
        headers=headers,
    )


def create_request_content(date: datetime.date) -> str:
    return f'''<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:xsd="http://www.w3.org/2001/XMLSchema"
    xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <GetCursOnDate xmlns="http://web.cbr.ru/">
      <On_date>{date.year}-{str(date.month).rjust(2, '0')}-{str(date.day).rjust(2, '0')}</On_date>
    </GetCursOnDate>
  </soap:Body>
</soap:Envelope>'''


def get_currency_rate_from_xml(currency_code: str, response_root: ElementTree.Element) -> Tuple[str, str]:
    """
    Returns tuple (amount of currency, currency rate)
    Args:
        currency_code: alphabetic currency code
        response_root: xml response of service

    Returns:
        (amount of currency, currency rate)
    """
    for el in response_root.iter():
        if el.tag == 'ValuteCursOnDate' and el.find('VchCode').text.lower() == currency_code.lower():
            return el.find('Vnom').text, el.find('Vcurs').text
