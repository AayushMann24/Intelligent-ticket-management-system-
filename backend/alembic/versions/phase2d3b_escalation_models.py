"""Phase 2D-3B: Add Escalation models

Revision ID: phase2d3b_escalation_models
Revises: phase2d1_notification_foundation
Create Date: 2026-10-05

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'phase2d3b_escalation_models'
down_revision: Union[str, Sequence[str], None] = 'phase2d1_notification_foundation'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Enum values for escalation_event_type
ESCALATION_EVENT_TYPES = [
    'RESPONSE_BREACH',
    'RESOLUTION_BREACH',
]


def upgrade() -> None:
    """Upgrade schema for Phase 2D-3B Escalation models."""
    
    # Create escalation_rules table
    op.create_table(
        'escalation_rules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('event_type', sa.Enum(*ESCALATION_EVENT_TYPES, name='escalationeventtype'), nullable=False),
        sa.Column('priority', sa.String(), nullable=False),
        sa.Column('ticket_type', sa.String(), nullable=True),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('target_role', sa.String(), nullable=False, server_default='Admin'),
        sa.Column('notify_enabled', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('email_enabled', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('precedence', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    
    # Create indexes for escalation_rules
    op.create_index(op.f('ix_escalation_rules_id'), 'escalation_rules', ['id'], unique=False)
    op.create_index(op.f('ix_escalation_rules_name'), 'escalation_rules', ['name'], unique=True)
    op.create_index(op.f('ix_escalation_rules_event_type'), 'escalation_rules', ['event_type'], unique=False)
    op.create_index(op.f('ix_escalation_rules_priority'), 'escalation_rules', ['priority'], unique=False)
    op.create_index(op.f('ix_escalation_rules_ticket_type'), 'escalation_rules', ['ticket_type'], unique=False)
    op.create_index(op.f('ix_escalation_rules_category'), 'escalation_rules', ['category'], unique=False)
    op.create_index(op.f('ix_escalation_rules_is_active'), 'escalation_rules', ['is_active'], unique=False)
    op.create_index('ix_escalation_rules_active_priority', 'escalation_rules', ['is_active', 'priority'], unique=False)
    op.create_index('ix_escalation_rules_active_event', 'escalation_rules', ['is_active', 'event_type'], unique=False)
    
    # Create escalation_records table
    op.create_table(
        'escalation_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ticket_id', sa.Integer(), sa.ForeignKey('tickets.id', ondelete='CASCADE'), nullable=False),
        sa.Column('event_type', sa.Enum(*ESCALATION_EVENT_TYPES, name='escalationeventtype'), nullable=False),
        sa.Column('rule_id', sa.Integer(), sa.ForeignKey('escalation_rules.id', ondelete='SET NULL'), nullable=True),
        sa.Column('recipient_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('notification_created', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('notification_id', sa.Integer(), sa.ForeignKey('notifications.id', ondelete='SET NULL'), nullable=True),
        sa.Column('email_sent', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('email_error', sa.Text(), nullable=True),
        sa.Column('history_recorded', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('metadata_json', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    
    # Create indexes for escalation_records
    op.create_index(op.f('ix_escalation_records_id'), 'escalation_records', ['id'], unique=False)
    op.create_index(op.f('ix_escalation_records_ticket_id'), 'escalation_records', ['ticket_id'], unique=False)
    op.create_index(op.f('ix_escalation_records_event_type'), 'escalation_records', ['event_type'], unique=False)
    op.create_index(op.f('ix_escalation_records_rule_id'), 'escalation_records', ['rule_id'], unique=False)
    op.create_index(op.f('ix_escalation_records_recipient_id'), 'escalation_records', ['recipient_id'], unique=False)
    op.create_index('ix_escalation_records_ticket_event', 'escalation_records', ['ticket_id', 'event_type'], unique=False)
    
    # Unique constraint for idempotency
    op.create_unique_constraint('uq_escalation_ticket_event_rule', 'escalation_records', ['ticket_id', 'event_type', 'rule_id'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop unique constraint
    op.drop_constraint('uq_escalation_ticket_event_rule', 'escalation_records', type_='unique')
    
    # Drop indexes for escalation_records
    op.drop_index('ix_escalation_records_ticket_event', table_name='escalation_records')
    op.drop_index(op.f('ix_escalation_records_recipient_id'), table_name='escalation_records')
    op.drop_index(op.f('ix_escalation_records_rule_id'), table_name='escalation_records')
    op.drop_index(op.f('ix_escalation_records_event_type'), table_name='escalation_records')
    op.drop_index(op.f('ix_escalation_records_ticket_id'), table_name='escalation_records')
    op.drop_index(op.f('ix_escalation_records_id'), table_name='escalation_records')
    
    # Drop escalation_records table
    op.drop_table('escalation_records')
    
    # Drop indexes for escalation_rules
    op.drop_index('ix_escalation_rules_active_event', table_name='escalation_rules')
    op.drop_index('ix_escalation_rules_active_priority', table_name='escalation_rules')
    op.drop_index(op.f('ix_escalation_rules_is_active'), table_name='escalation_rules')
    op.drop_index(op.f('ix_escalation_rules_category'), table_name='escalation_rules')
    op.drop_index(op.f('ix_escalation_rules_ticket_type'), table_name='escalation_rules')
    op.drop_index(op.f('ix_escalation_rules_priority'), table_name='escalation_rules')
    op.drop_index(op.f('ix_escalation_rules_event_type'), table_name='escalation_rules')
    op.drop_index(op.f('ix_escalation_rules_name'), table_name='escalation_rules')
    op.drop_index(op.f('ix_escalation_rules_id'), table_name='escalation_rules')
    
    # Drop escalation_rules table
    op.drop_table('escalation_rules')
    
    # Drop enum type
    op.execute('DROP TYPE IF EXISTS escalationeventtype')