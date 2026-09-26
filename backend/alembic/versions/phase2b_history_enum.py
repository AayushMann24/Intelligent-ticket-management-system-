"""Phase 2B: Add new HistoryEventType enum values

Revision ID: phase2b_history_enum
Revises: phase2b_ticket_workflow
Create Date: 2026-09-26

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'phase2b_history_enum'
down_revision: Union[str, Sequence[str], None] = 'phase2b_ticket_workflow'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add new enum values to historyeventtype."""
    # PostgreSQL: Add new enum values
    op.execute("ALTER TYPE historyeventtype ADD VALUE IF NOT EXISTS 'REASSIGNED'")
    op.execute("ALTER TYPE historyeventtype ADD VALUE IF NOT EXISTS 'TYPE_CHANGED'")
    op.execute("ALTER TYPE historyeventtype ADD VALUE IF NOT EXISTS 'ESCALATED'")


def downgrade() -> None:
    """Cannot easily remove enum values in PostgreSQL."""
    pass