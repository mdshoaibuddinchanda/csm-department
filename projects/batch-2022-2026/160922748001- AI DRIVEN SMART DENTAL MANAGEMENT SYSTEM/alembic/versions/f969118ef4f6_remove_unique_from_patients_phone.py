"""remove unique from patients phone

Revision ID: f969118ef4f6
Revises: c99dfeacdffb
"""

from typing import Sequence, Union
from alembic import op


revision: str = 'f969118ef4f6'
down_revision: Union[str, Sequence[str], None] = 'c99dfeacdffb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop unique constraint if it exists
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM pg_constraint
                WHERE conname = 'patients_phone_key'
            ) THEN
                ALTER TABLE patients
                DROP CONSTRAINT patients_phone_key;
            END IF;
        END$$;
    """)


def downgrade() -> None:
    # Recreate unique constraint (rollback support)
    op.create_unique_constraint(
        "patients_phone_key",
        "patients",
        ["phone"]
    )
