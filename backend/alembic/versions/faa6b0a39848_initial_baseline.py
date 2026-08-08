"""Initial baseline

Revision ID: faa6b0a39848
Revises: 
Create Date: 2026-06-09 11:39:56.065303

"""
from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = 'faa6b0a39848'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
