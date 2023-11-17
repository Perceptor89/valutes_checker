from typing import List

from sqlalchemy import (DATE, BigInteger, Column, Float, ForeignKey, String,
                        UniqueConstraint)
from sqlalchemy.orm import Mapped, relationship, declarative_base


DB = declarative_base()


class Currency(DB):
    __tablename__ = 'currencies'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(50))
    cbr_id = Column(String(10), unique=True, nullable=False)
    char_code = Column(String(10), unique=True, nullable=False)
    values: Mapped[List['Value']] = relationship(back_populates='currency')


class Value(DB):
    __tablename__ = 'currency_values'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    currency_id = Column(BigInteger, ForeignKey('currencies.id'))
    value = Column(Float, nullable=False)
    date = Column(DATE, nullable=False)
    currency: Mapped['Currency'] = relationship(back_populates='values',
                                                lazy='joined')
    __table_args__ = (
        UniqueConstraint('currency_id', 'date', name='_currency_id_date_uc'),
    )
