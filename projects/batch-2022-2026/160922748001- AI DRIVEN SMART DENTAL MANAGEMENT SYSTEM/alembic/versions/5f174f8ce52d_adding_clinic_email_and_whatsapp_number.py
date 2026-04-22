"""adding clinic_email and whatsapp_number

Revision ID: 5f174f8ce52d
Revises: c9b50ce32155
Create Date: 2026-02-02 11:18:20.836657

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5f174f8ce52d'
down_revision: Union[str, Sequence[str], None] = 'c9b50ce32155'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "doctors",
        sa.Column("clinic_email", sa.String(), nullable=True)
    )
    op.add_column(
        "doctors",
        sa.Column("whatsapp_number", sa.String(), nullable=True)
    )


def downgrade():
    op.drop_column("doctors", "whatsapp_number")
    op.drop_column("doctors", "clinic_email")

