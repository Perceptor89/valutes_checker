import unittest
from datetime import datetime

import pytest
from database.accessor import PostgresClient
from fastapi.testclient import TestClient
from freezegun import freeze_time
from main import app


@pytest.mark.usefixtures('temp_db', 'write_data')
class TestAPI(unittest.TestCase):
    def setUp(self) -> None:
        self.db_client = PostgresClient()
        self.db_client.connect()

    @freeze_time('2023-10-10')
    def test_root_today(self):
        self.assertEqual(datetime.utcnow(), datetime(2023, 10, 10, 0, 0))

        with TestClient(app) as client:
            response = client.get('/')

        with open('tests/fixtures/today.html', 'rb') as f:
            today_html = f.read()

        self.assertEqual(response.content, today_html)

    @freeze_time('2023-10-10')
    def test_root_yesterday(self):
        self.assertEqual(datetime.utcnow(), datetime(2023, 10, 10, 0, 0))

        with TestClient(app) as client:
            response = client.get('/?days_back=yesterday')

        with open('tests/fixtures/yesterday.html', 'rb') as f:
            yesterday_html = f.read()

        self.assertEqual(response.content, yesterday_html)

    @freeze_time('2023-10-10')
    def test_root_two_days_ago(self):
        self.assertEqual(datetime.utcnow(), datetime(2023, 10, 10, 0, 0))

        with TestClient(app) as client:
            response = client.get('/?days_back=2%20days%20ago')

        with open('tests/fixtures/two_days.html', 'rb') as f:
            two_days_html = f.read()

        self.assertEqual(response.content, two_days_html)

    # no data case

    def tearDown(self) -> None:
        self.db_client.disconnect()
