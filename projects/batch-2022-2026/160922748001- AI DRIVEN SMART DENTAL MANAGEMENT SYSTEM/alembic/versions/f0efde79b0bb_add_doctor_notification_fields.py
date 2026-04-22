"""add doctor notification fields

Revision ID: f0efde79b0bb
Revises: 5bf9ad7c5dd8
Create Date: 2026-02-19 15:55:05.824125

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f0efde79b0bb'
down_revision: Union[str, Sequence[str], None] = '5bf9ad7c5dd8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'doctors',
        sa.Column('doctor_whatsapp_number', sa.String(), nullable=True)
    )

    op.add_column(
        'doctors',
        sa.Column('clinic_phone_number', sa.String(), nullable=True)
    )

    op.add_column(
        'doctors',
        sa.Column(
            'notifications_enabled',
            sa.Boolean(),
            server_default=sa.text('false'),
            nullable=False
        )
    )

    # DO NOT DROP old column yet


def downgrade() -> None:
    op.drop_column('doctors', 'notifications_enabled')
    op.drop_column('doctors', 'clinic_phone_number')
    op.drop_column('doctors', 'doctor_whatsapp_number')

    # ### end Alembic commands ###
