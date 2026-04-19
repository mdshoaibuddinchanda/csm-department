"""make clinic_email not null

Revision ID: c99dfeacdffb
Revises: 5f174f8ce52d
Create Date: 2026-02-06 13:57:22.242626

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c99dfeacdffb'
down_revision: Union[str, Sequence[str], None] = '5f174f8ce52d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.alter_column(
        "doctors",
        "clinic_email",
        existing_type=sa.String(),
        nullable=False
    )


def downgrade() -> None:
    op.alter_column(
        "doctors",
        "clinic_email",
        existing_type=sa.String(),
        nullable=True
    )
