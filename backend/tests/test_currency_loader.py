import unittest
from unittest.mock import MagicMock, patch

import pytest
from freezegun import freeze_time
from sqlalchemy import select

from cbr_client.currency_loader import CurrencyLoader
from database.accessor import PostgresClient
from database.models import Currency, Value


@pytest.mark.usefixtures('temp_db')
class TestCurrencyLoader(unittest.TestCase):
    def setUp(self) -> None:
        self.db_client = PostgresClient()
        self.db_client.connect()
        self.currency_loader = CurrencyLoader()

        with open('tests/fixtures/cbr_data.xml', 'r') as f:
            self.mock_data = f.read()

    @patch('requests.get')
    @freeze_time('2023-10-10')
    def test_load_data(self, mock_request):
        with self.db_client.session.begin() as s:
            currencies = s.execute(select(Currency)).fetchall()
            values = s.execute(select(Value)).fetchall()

        self.assertEqual(len(currencies), 0)
        self.assertEqual(len(values), 0)

        mock_response = MagicMock()
        mock_response.text = self.mock_data
        mock_request.return_value = mock_response

        self.currency_loader.load_data()

        mock_request.assert_called_once_with(
            'http://www.cbr.ru/scripts/XML_daily.asp?date_req=10.10.2023'
        )

        with self.db_client.session.begin() as s:
            currencies = s.execute(select(Currency)).fetchall()
            values = s.execute(select(Value)).fetchall()

        self.assertEqual(len(currencies), 43)
        self.assertEqual(len(values), 43)

    def tearDown(self) -> None:
        self.db_client.disconnect()
