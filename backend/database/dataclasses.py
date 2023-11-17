from typing import Optional
from pydantic import BaseModel, confloat
from datetime import date


class CurrencyDC(BaseModel):
    id: Optional[int]
    name: Optional[str]
    cbr_id: str
    char_code: str

    def to_db(self):
        return self.model_dump(exclude_none=True)


class ValueDC(BaseModel):
    id: Optional[int]
    currency_id: int
    value: confloat(gt=0)
    date: date

    def to_db(self):
        return self.model_dump(exclude_none=True)
