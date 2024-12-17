"""merge heads

Revision ID: 2024_03_merge_heads
Revises: 2024_02_update_loan, 6f547ff3049c
Create Date: 2024-03-01

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2024_03_merge_heads'
down_revision = ('2024_02_update_loan', '6f547ff3049c')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
