"""Phase 2C-2: Add SLA breach history event types

Revision ID: phase2c2_sla_breach_events
Revises: phase2c1_sla_foundation
Create Date: 2026-09-26

"""
from typing import Sequence, Union
from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'phase2c2_sla_breach_events'
down_revision: Union[str, Sequence[str], None] = 'phase2c1_sla_foundation'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add new enum values to historyeventtype."""
    # PostgreSQL: Add new enum values
    op.execute("ALTER TYPE historyeventtype ADD VALUE IF NOT EXISTS 'SLA_RESPONSE_BREACHED'")
    op.execute("ALTER TYPE historyeventtype ADD VALUE IF NOT EXISTS 'SLA_RESOLUTION_BREACHED'")


def downgrade() -> None:
    """Cannot easily remove enum values in PostgreSQL."""
    pass