"""Phase 2B: Add ticket_type, resolution, and escalation fields

Revision ID: phase2b_ticket_workflow
Revises: 25a0cea01403
Create Date: 2026-09-26

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'phase2b_ticket_workflow'
down_revision: Union[str, Sequence[str], None] = '25a0cea01403'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema for Phase 2B ticket workflow."""
    # Add ticket_type column with default for existing tickets
    op.add_column('tickets', sa.Column('ticket_type', sa.String(), nullable=True))
    op.execute("UPDATE tickets SET ticket_type = 'INCIDENT' WHERE ticket_type IS NULL")
    op.alter_column('tickets', 'ticket_type', nullable=False, existing_type=sa.String())
    op.create_index(op.f('ix_tickets_ticket_type'), 'tickets', ['ticket_type'], unique=False)

    # Add resolution fields
    op.add_column('tickets', sa.Column('resolution_summary', sa.Text(), nullable=True))
    op.add_column('tickets', sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('tickets', sa.Column('resolved_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=True))
    op.create_index(op.f('ix_tickets_resolved_by'), 'tickets', ['resolved_by'], unique=False)

    # Add escalation fields
    op.add_column('tickets', sa.Column('escalated_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=True))
    op.add_column('tickets', sa.Column('escalated_to', sa.Integer(), sa.ForeignKey('users.id'), nullable=True))
    op.add_column('tickets', sa.Column('escalation_reason', sa.Text(), nullable=True))
    op.add_column('tickets', sa.Column('escalated_at', sa.DateTime(timezone=True), nullable=True))
    op.create_index(op.f('ix_tickets_escalated_by'), 'tickets', ['escalated_by'], unique=False)
    op.create_index(op.f('ix_tickets_escalated_to'), 'tickets', ['escalated_to'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_tickets_escalated_to'), table_name='tickets')
    op.drop_index(op.f('ix_tickets_escalated_by'), table_name='tickets')
    op.drop_index(op.f('ix_tickets_resolved_by'), table_name='tickets')
    op.drop_index(op.f('ix_tickets_ticket_type'), table_name='tickets')
    op.drop_column('tickets', 'escalated_at')
    op.drop_column('tickets', 'escalation_reason')
    op.drop_column('tickets', 'escalated_to')
    op.drop_column('tickets', 'escalated_by')
    op.drop_column('tickets', 'resolved_by')
    op.drop_column('tickets', 'resolved_at')
    op.drop_column('tickets', 'resolution_summary')
    op.drop_column('tickets', 'ticket_type')