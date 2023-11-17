
import os
from datetime import date
from typing import Optional

from database.models import Currency, Value
from sqlalchemy import Engine, create_engine, select, text
from sqlalchemy.orm import Session, sessionmaker


DB_NAME = os.getenv('POSTGRES_DB')
TEST_DB_NAME = f'{DB_NAME}_TEST'
USER = os.getenv('POSTGRES_USER')
PASSWORD = os.getenv('POSTGRES_PASSWORD')
HOST = os.getenv('POSTGRES_HOST')
PORT = os.getenv('POSTGRES_PORT')
DB_URI = f'postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}'
TEST_DB_URI = (
    f'postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{TEST_DB_NAME}'
)
TESTING = os.getenv('TESTING')


class PostgresClient:
    def __init__(self):
        self.uri = DB_URI if not TESTING else TEST_DB_URI
        self.engine: Optional[Engine] = None
        self.session: Optional[Session] = None

    def connect(self):
        self.engine = create_engine(self.uri, future=True)
        self.session = sessionmaker(bind=self.engine, expire_on_commit=False,
                                    class_=Session)

    def disconnect(self):
        self.engine.dispose()

    def save_currency(self, raw_currency: dict) -> int:
        with self.session.begin() as s:
            currency = Currency(**raw_currency)
            currency = s.merge(currency)

        return currency.id

    def get_currency_id(self, cbr_id: str) -> int | None:
        with self.session.begin() as s:
            return s.execute(
                select(Currency.id).where(Currency.cbr_id == cbr_id)
            ).scalar()

    def save_value(self, raw_value: dict) -> int:
        with self.session.begin() as s:
            value = Value(**raw_value)
            value = s.merge(value)

        return value.id

    def get_value_id(self, date: date, currency_id: int) -> int | None:
        with self.session.begin() as s:
            return s.execute(
                select(Value.id)
                .where(Value.date == date)
                .where(Value.currency_id == currency_id)
            ).scalar()

    def get_values(self, char_codes: list, date: date) -> list:
        with self.session.begin() as s:
            values = s.execute(
                select(Currency.char_code, Value.value)
                .join(Currency)
                .where(Currency.char_code.in_(char_codes))
                .where(Value.date == date)
            ).fetchall()

            return values

    def get_last_value_date(self) -> date | None:
        with self.session.begin() as s:
            return s.execute(
                text('SELECT MAX(cv.date) FROM currency_values cv;')
            ).scalar()
