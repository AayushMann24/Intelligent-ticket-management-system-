"""Phase 2D-4: seed default escalation rules

Revision ID: phase2d4_escalation_defaults
Revises: d635192
Create Date: 2026-10-17

Seeds a conservative set of default escalation rules so the escalation
pipeline (added in Phase 2D-3B) has sensible behaviour out of the box:

  * RESPONSE_BREACH   + Critical -> Admin
  * RESPONSE_BREACH   + High     -> Admin
  * RESOLUTION_BREACH + Critical -> Admin
  * RESOLUTION_BREACH + High     -> Admin

Lower-severity (Medium/Low) breaches intentionally have no default rule, so
existing "no escalation" semantics for those priorities are preserved.

The seeding is idempotent: it inserts a rule only when no rule with the same
unique name already exists. This makes the migration safe to re-run and avoids
duplicating rules on installations that already defined some of them.

This migration is fully reversible - downgrade() removes only the default rules
it created (matched by name) and leaves any operator-defined rules untouched.
"""

from datetime import datetime, timezone
from typing import List, Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'phase2d4_escalation_defaults'
down_revision: Union[str, Sequence[str], None] = 'd635192'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Default rules. Names are stable and used for idempotency + rollback.
DEFAULT_RULES: List[dict] = [
    {
        "name": "Default: Critical Response SLA Breach",
        "description": "Escalate Critical tickets that breach their response SLA to an Admin.",
        "event_type": "RESPONSE_BREACH",
        "priority": "Critical",
        "target_role": "Admin",
        "notify_enabled": True,
        "email_enabled": True,
        "is_active": True,
        "precedence": 2,  # event_type + priority
    },
    {
        "name": "Default: High Response SLA Breach",
        "description": "Escalate High priority tickets that breach their response SLA to an Admin.",
        "event_type": "RESPONSE_BREACH",
        "priority": "High",
        "target_role": "Admin",
        "notify_enabled": True,
        "email_enabled": True,
        "is_active": True,
        "precedence": 2,
    },
    {
        "name": "Default: Critical Resolution SLA Breach",
        "description": "Escalate Critical tickets that breach their resolution SLA to an Admin.",
        "event_type": "RESOLUTION_BREACH",
        "priority": "Critical",
        "target_role": "Admin",
        "notify_enabled": True,
        "email_enabled": True,
        "is_active": True,
        "precedence": 2,
    },
    {
        "name": "Default: High Resolution SLA Breach",
        "description": "Escalate High priority tickets that breach their resolution SLA to an Admin.",
        "event_type": "RESOLUTION_BREACH",
        "priority": "High",
        "target_role": "Admin",
        "notify_enabled": True,
        "email_enabled": True,
        "is_active": True,
        "precedence": 2,
    },
]


_INSERT_SQL = sa.text(
    """
    INSERT INTO escalation_rules
        (name, description, event_type, priority, ticket_type, category,
         target_role, notify_enabled, email_enabled, is_active, precedence,
         created_at, updated_at)
    VALUES
        (:name, :description, CAST(:event_type AS escalationeventtype), :priority,
         NULL, NULL, :target_role, :notify_enabled, :email_enabled, :is_active,
         :precedence, :created_at, :updated_at)
    """
)

_EXISTS_SQL = sa.text("SELECT 1 FROM escalation_rules WHERE name = :name")

_DELETE_SQL = sa.text(
    "DELETE FROM escalation_rules WHERE name IN :names"
).bindparams(sa.bindparam("names", expanding=True))


def _seed_default_rules(bind) -> int:
    """Insert missing default rules. Returns the number inserted."""
    now = datetime.now(timezone.utc)
    inserted = 0
    for rule in DEFAULT_RULES:
        already_exists = bind.execute(_EXISTS_SQL, {"name": rule["name"]}).fetchone()
        if already_exists:
            continue
        bind.execute(
            _INSERT_SQL,
            {
                "name": rule["name"],
                "description": rule["description"],
                "event_type": rule["event_type"],
                "priority": rule["priority"],
                "target_role": rule["target_role"],
                "notify_enabled": rule["notify_enabled"],
                "email_enabled": rule["email_enabled"],
                "is_active": rule["is_active"],
                "precedence": rule["precedence"],
                "created_at": now,
                "updated_at": now,
            },
        )
        inserted += 1
    return inserted


def _remove_default_rules(bind) -> int:
    """Delete the default rules (by name). Returns the number deleted."""
    names = [rule["name"] for rule in DEFAULT_RULES]
    result = bind.execute(_DELETE_SQL, {"names": names})
    return result.rowcount if result.rowcount is not None else 0


def upgrade() -> None:
    """Seed default escalation rules (idempotent)."""
    _seed_default_rules(op.get_bind())


def downgrade() -> None:
    """Remove the seeded default escalation rules."""
    _remove_default_rules(op.get_bind())
