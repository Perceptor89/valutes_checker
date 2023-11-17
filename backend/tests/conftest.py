import os

import pytest
from tests.fixtures.db_data import CURRENCIES, VALUES

os.environ['TESTING'] = 'True'

from alembic import command
from alembic.config import Config
from database.accessor import TEST_DB_URI, PostgresClient
from sqlalchemy_utils import create_database, drop_database


@pytest.fixture(scope='function')
def temp_db():
    create_database(TEST_DB_URI)
    base_dir = os.path.dirname(os.path.dirname(__file__))
    alembic_cfg = Config(os.path.join(base_dir, 'alembic.ini'))
    command.upgrade(alembic_cfg, 'head')

    try:
        yield TEST_DB_URI
    finally:
        drop_database(TEST_DB_URI)


@pytest.fixture(scope='function')
def write_data():
    db_client = PostgresClient()
    db_client.connect()

    for currency in CURRENCIES:
        db_client.save_currency(currency)

    for value in VALUES:
        db_client.save_value(value)

    db_client.disconnect()
