"""Phase 2C-1: Add SLA policy model and ticket SLA fields

Revision ID: phase2c1_sla_foundation
Revises: phase2b_history_enum
Create Date: 2026-09-26

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'phase2c1_sla_foundation'
down_revision: Union[str, Sequence[str], None] = 'phase2b_history_enum'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema for Phase 2C-1 SLA foundation."""
    # Create sla_policies table
    op.create_table(
        'sla_policies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('priority', sa.String(), nullable=False),
        sa.Column('ticket_type', sa.String(), nullable=True),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('response_time_minutes', sa.Integer(), nullable=False),
        sa.Column('resolution_time_minutes', sa.Integer(), nullable=False),
        sa.Column('warning_threshold_percentage', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )
    op.create_index(op.f('ix_sla_policies_id'), 'sla_policies', ['id'], unique=False)
    op.create_index(op.f('ix_sla_policies_name'), 'sla_policies', ['name'], unique=True)
    op.create_index('ix_sla_policies_priority_type', 'sla_policies', ['priority', 'ticket_type'], unique=False)
    op.create_index('ix_sla_policies_active_priority', 'sla_policies', ['is_active', 'priority'], unique=False)
    op.create_index(op.f('ix_sla_policies_priority'), 'sla_policies', ['priority'], unique=False)
    op.create_index(op.f('ix_sla_policies_ticket_type'), 'sla_policies', ['ticket_type'], unique=False)
    op.create_index(op.f('ix_sla_policies_category'), 'sla_policies', ['category'], unique=False)
    op.create_index(op.f('ix_sla_policies_is_active'), 'sla_policies', ['is_active'], unique=False)

    # Add SLA fields to tickets table
    op.add_column('tickets', sa.Column('sla_policy_id', sa.Integer(), sa.ForeignKey('sla_policies.id'), nullable=True))
    op.add_column('tickets', sa.Column('sla_response_deadline', sa.DateTime(timezone=True), nullable=True))
    op.add_column('tickets', sa.Column('sla_resolution_deadline', sa.DateTime(timezone=True), nullable=True))
    op.add_column('tickets', sa.Column('sla_response_met_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('tickets', sa.Column('sla_resolution_met_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('tickets', sa.Column('sla_response_breached', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    op.add_column('tickets', sa.Column('sla_resolution_breached', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    
    op.create_index(op.f('ix_tickets_sla_policy'), 'tickets', ['sla_policy_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_tickets_sla_policy'), table_name='tickets')
    op.drop_column('tickets', 'sla_resolution_breached')
    op.drop_column('tickets', 'sla_response_breached')
    op.drop_column('tickets', 'sla_resolution_met_at')
    op.drop_column('tickets', 'sla_response_met_at')
    op.drop_column('tickets', 'sla_resolution_deadline')
    op.drop_column('tickets', 'sla_response_deadline')
    op.drop_column('tickets', 'sla_policy_id')

    op.drop_index(op.f('ix_sla_policies_is_active'), table_name='sla_policies')
    op.drop_index(op.f('ix_sla_policies_category'), table_name='sla_policies')
    op.drop_index(op.f('ix_sla_policies_ticket_type'), table_name='sla_policies')
    op.drop_index(op.f('ix_sla_policies_priority'), table_name='sla_policies')
    op.drop_index('ix_sla_policies_active_priority', table_name='sla_policies')
    op.drop_index('ix_sla_policies_priority_type', table_name='sla_policies')
    op.drop_index(op.f('ix_sla_policies_id'), table_name='sla_policies')
    op.drop_index(op.f('ix_sla_policies_name'), table_name='sla_policies')
    op.drop_table('sla_policies')