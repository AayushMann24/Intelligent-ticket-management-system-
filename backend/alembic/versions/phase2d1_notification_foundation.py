"""Phase 2D-1: Add Notification model

Revision ID: phase2d1_notification_foundation
Revises: phase2c2_sla_breach_events
Create Date: 2026-10-05

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'phase2d1_notification_foundation'
down_revision: Union[str, Sequence[str], None] = 'phase2c2_sla_breach_events'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Enum values for notification_type
NOTIFICATION_TYPES = [
    'TICKET_ASSIGNED',
    'TICKET_REASSIGNED',
    'SLA_RESPONSE_WARNING',
    'SLA_RESPONSE_BREACHED',
    'SLA_RESOLUTION_WARNING',
    'SLA_RESOLUTION_BREACHED',
    'TICKET_ESCALATED',
    'SYSTEM',
]


def upgrade() -> None:
    """Upgrade schema for Phase 2D-1 Notification foundation."""
    # Create notifications table with enum (SQLAlchemy will create the enum type automatically)
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('recipient_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('notification_type', sa.Enum(*NOTIFICATION_TYPES, name='notificationtype'), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('ticket_id', sa.Integer(), sa.ForeignKey('tickets.id', ondelete='SET NULL'), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    
    # Create indexes
    op.create_index(op.f('ix_notifications_id'), 'notifications', ['id'], unique=False)
    op.create_index(op.f('ix_notifications_recipient_id'), 'notifications', ['recipient_id'], unique=False)
    op.create_index(op.f('ix_notifications_notification_type'), 'notifications', ['notification_type'], unique=False)
    op.create_index(op.f('ix_notifications_ticket_id'), 'notifications', ['ticket_id'], unique=False)
    op.create_index(op.f('ix_notifications_is_read'), 'notifications', ['is_read'], unique=False)
    op.create_index(op.f('ix_notifications_created_at'), 'notifications', ['created_at'], unique=False)
    
    # Composite indexes for common query patterns
    op.create_index('ix_notifications_recipient_unread', 'notifications', ['recipient_id', 'is_read'], unique=False)
    op.create_index('ix_notifications_recipient_created', 'notifications', ['recipient_id', 'created_at'], unique=False)
    op.create_index('ix_notifications_ticket_recipient', 'notifications', ['ticket_id', 'recipient_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes
    op.drop_index('ix_notifications_ticket_recipient', table_name='notifications')
    op.drop_index('ix_notifications_recipient_created', table_name='notifications')
    op.drop_index('ix_notifications_recipient_unread', table_name='notifications')
    op.drop_index(op.f('ix_notifications_created_at'), table_name='notifications')
    op.drop_index(op.f('ix_notifications_is_read'), table_name='notifications')
    op.drop_index(op.f('ix_notifications_ticket_id'), table_name='notifications')
    op.drop_index(op.f('ix_notifications_notification_type'), table_name='notifications')
    op.drop_index(op.f('ix_notifications_recipient_id'), table_name='notifications')
    op.drop_index(op.f('ix_notifications_id'), table_name='notifications')
    
    # Drop table
    op.drop_table('notifications')
    
    # Drop enum type
    op.execute('DROP TYPE IF EXISTS notificationtype')