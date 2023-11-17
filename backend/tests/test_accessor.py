import unittest
from datetime import date

import pytest
from psycopg2.errors import ForeignKeyViolation, UniqueViolation
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from database.accessor import PostgresClient
from database.models import Currency, Value


@pytest.mark.usefixtures('temp_db')
class TestAccessor(unittest.TestCase):
    def setUp(self) -> None:
        self.db_client = PostgresClient()
        self.db_client.connect()

        self.euro = {
            'name': 'Евро',
            'char_code': 'EUR',
            'cbr_id': 'R01239',
        }

        self.value = {
            'currency_id': 1,
            'value': 92.70,
            'date': '2023-11-16',
        }

    def test_save_currency(self):
        new_id = self.db_client.save_currency(self.euro)

        with self.db_client.session.begin() as s:
            db_currency = s.execute(
                select(Currency).where(Currency.id == new_id)
            ).scalar()

        self.assertEqual(self.euro['cbr_id'], db_currency.cbr_id)

    def test_save_existing_currency(self):
        self.db_client.save_currency(self.euro)

        with self.assertRaises((UniqueViolation, IntegrityError)):
            self.db_client.save_currency(self.euro)

    def test_get_currency_id(self):
        self.db_client.save_currency(self.euro)
        euro_id = self.db_client.get_currency_id(cbr_id='R01239')

        self.assertEqual(euro_id, 1)

    def test_save_value_no_currency(self):
        with self.assertRaises((IntegrityError, ForeignKeyViolation)):
            self.db_client.save_value(self.value)

    def test_save_value(self):
        self.db_client.save_currency(self.euro)
        value_id = self.db_client.save_value(self.value)

        with self.db_client.session.begin() as s:
            db_value = s.execute(
                select(Value).where(Value.id == value_id)
            ).scalar()

        self.assertEqual(self.value['value'], db_value.value)

    def test_save_value_exists(self):
        self.db_client.save_currency(self.euro)
        self.db_client.save_value(self.value)
        with self.assertRaises((IntegrityError, UniqueViolation)):
            self.db_client.save_value(self.value)

    def test_get_values(self):
        self.db_client.save_currency(self.euro)
        self.db_client.save_value(self.value)
        values = self.db_client.get_values(
            [self.euro['char_code']],
            self.value['date'],
        )

        self.assertEqual(
            values,
            [(self.euro['char_code'], self.value['value']),]
        )

    def test_get_values_no_data(self):
        values = self.db_client.get_values(
            ['JPY'],
            '2023-11-01',
        )
        self.assertEqual(values, [])

    def test_get_last_value_date(self):
        self.db_client.save_currency(self.euro)
        self.db_client.save_value(self.value)
        new_value = self.value.copy()
        new_value['date'] = '2023-11-01'
        self.db_client.save_value(new_value)

        last_date = self.db_client.get_last_value_date()
        value_date = date.fromisoformat(self.value['date'])
        self.assertEqual(last_date, value_date)

    def tearDown(self) -> None:
        self.db_client.disconnect()
