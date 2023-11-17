"""add constraint

Revision ID: 21f79f4a0527
Revises: 63a9c7558952
Create Date: 2023-11-16 18:03:10.117564

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '21f79f4a0527'
down_revision: Union[str, None] = '63a9c7558952'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'currencies', ['cbr_id'])
    op.create_unique_constraint(None, 'currencies', ['char_code'])
    op.create_unique_constraint('_currency_id_date_uc', 'currency_values', ['currency_id', 'date'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('_currency_id_date_uc', 'currency_values', type_='unique')
    op.drop_constraint(None, 'currencies', type_='unique')
    op.drop_constraint(None, 'currencies', type_='unique')
    # ### end Alembic commands ###
