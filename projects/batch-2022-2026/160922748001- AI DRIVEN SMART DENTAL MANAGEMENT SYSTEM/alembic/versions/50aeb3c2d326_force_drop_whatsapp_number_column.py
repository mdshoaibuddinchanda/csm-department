"""force drop whatsapp_number column

Revision ID: 50aeb3c2d326
Revises: d193df0714db
Create Date: 2026-02-19 17:11:24.085799

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '50aeb3c2d326'
down_revision: Union[str, Sequence[str], None] = 'd193df0714db'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE doctors DROP COLUMN IF EXISTS whatsapp_number;"
    )


def downgrade() -> None:
    op.add_column(
        'doctors',
        sa.Column('whatsapp_number', sa.String(), nullable=True)
    )
