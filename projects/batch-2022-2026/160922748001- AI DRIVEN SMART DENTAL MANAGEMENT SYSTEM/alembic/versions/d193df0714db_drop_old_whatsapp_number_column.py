"""drop old whatsapp_number column

Revision ID: d193df0714db
Revises: f0efde79b0bb
Create Date: 2026-02-19 16:40:08.725477

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd193df0714db'
down_revision: Union[str, Sequence[str], None] = 'f0efde79b0bb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None




def upgrade() -> None:
    op.drop_column('doctors', 'whatsapp_number')


def downgrade() -> None:
    op.add_column(
        'doctors',
        sa.Column('whatsapp_number', sa.String(), nullable=True)
    )
