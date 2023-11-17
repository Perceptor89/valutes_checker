from datetime import datetime
from logging import Logger, getLogger
from time import sleep
from typing import Union

import requests
from bs4 import BeautifulSoup
from database.accessor import PostgresClient
from database.dataclasses import CurrencyDC, ValueDC


class CurrencyLoader:
    cbr_url = 'http://www.cbr.ru/scripts/XML_daily.asp'
    request_tries = 3
    retry_pause = 10

    db_client: PostgresClient | None = None
    logger: Logger | None = None

    def __init__(self):
        self.logger = getLogger(__name__)

    def load_data(self, date: datetime = None):
        date = date if date else datetime.utcnow().date()
        date_str = date.strftime('%d.%m.%Y')
        url = f'{self.cbr_url}?date_req={date_str}'

        xml = self.make_request(url)
        if not xml:
            self.logger.error('unable to get data from cbr site')
            return

        valutes = self.parse_data(xml)

        self.db_client = PostgresClient()
        self.db_client.connect()

        for valute in valutes:
            valute['date'] = date
            self.write_data(valute)

        self.db_client.disconnect()

    def make_request(self, url: str) -> Union[str, None]:
        response = None
        for i in range(self.request_tries):
            try:
                response = requests.get(url)
                return response.text if response else None
            except Exception:
                sleep(self.retry_pause)
                continue

    def parse_data(self, xml: str) -> list:
        soup = BeautifulSoup(xml, 'lxml')
        valute_tags = soup.find_all('valute')

        valutes = []
        for valute in valute_tags:
            try:
                valutes.append(
                    {
                        'cbr_id': valute.get('id'),
                        'name': valute.find('name').get_text(strip=True),
                        'char_code': valute.find('charcode')
                        .get_text(strip=True),
                        'value': valute.find('vunitrate').get_text(strip=True),
                    }
                )
            except Exception:
                self.logger.error(f'unable to process valute tag:\n{valute}')

        return valutes

    def write_data(self, valute_data: dict) -> None:
        currency_id = self.db_client.get_currency_id(valute_data.get('cbr_id'))

        if not currency_id:
            try:
                currency = CurrencyDC(
                    id=None,
                    name=valute_data.get('name'),
                    cbr_id=valute_data.get('cbr_id'),
                    char_code=valute_data.get('char_code'),
                )
                currency_id = self.db_client.save_currency(currency.to_db())
            except Exception as e:
                self.logger.error(f'unable to save currency: {e}')
                return

        date = valute_data.get('date')
        value_id = self.db_client.get_value_id(
            date=date, currency_id=currency_id
        )
        if value_id:
            self.logger.info(f'value with currency id {currency_id},'
                             f' date {date} already in database')
        else:
            try:
                value = ValueDC(
                    id=None,
                    currency_id=currency_id,
                    value=float(valute_data.get('value').replace(',', '.')),
                    date=valute_data.get('date'),
                )
                self.db_client.save_value(value.to_db())
            except Exception as e:
                self.logger.error(f'unable to save value: {e}')
                return
