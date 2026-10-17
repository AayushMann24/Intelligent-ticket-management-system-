# ITMS API Design

This document describes the ITMS backend HTTP API. It currently focuses on the
**Escalation Administration** API added in the escalation-administration
milestone (Phase 2D-4). It is intended to grow as additional surfaces are
documented.

All endpoints are served by the FastAPI application in
`backend/app/main.py` (`uvicorn app.main:app`).

## Conventions

- **Authentication**: `Authorization: Bearer <access_token>` or the
  `access_token` cookie.
- **Authorization**: role checks use the shared dependencies in
  `backend/app/dependencies/roles.py` (`require_admin`, etc.).
- **CSRF**: state-changing requests authenticated by cookie require the
  `X-CSRF-Token` header (see `backend/app/dependencies/csrf.py`). Requests using
  a Bearer token are exempt, matching the existing SLA policy API.
- **Errors**: `400` validation/business rule, `401` unauthenticated,
  `403` forbidden, `404` not found, `422` request-body validation.

---

## Escalation Administration

Base path: `/escalations` (router: `backend/app/routers/escalation.py`).

**All escalation administration endpoints require the `Admin` role.**

### Escalation rules

An escalation rule defines when an SLA breach escalates and to whom. Matching is
performed by `get_best_matching_rule` in
`backend/app/services/escalation_service.py`; the most specific rule wins
(`event_type + priority + ticket_type + category`). The stored `precedence`
mirrors this specificity.

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/escalations/rules` | Create a rule. `201`. Duplicate `name` -> `400`. |
| `GET` | `/escalations/rules` | List rules (paginated, ordered by precedence). |
| `GET` | `/escalations/rules/{rule_id}` | Retrieve one rule. |
| `PUT` | `/escalations/rules/{rule_id}` | Update a rule (partial). |
| `DELETE` | `/escalations/rules/{rule_id}` | Deactivate (soft-delete) a rule. |

**Create / update body**

```json
{
  "name": "High priority incident escalation",
  "description": "Escalate High priority incident breaches to a technician",
  "event_type": "RESPONSE_BREACH",
  "priority": "High",
  "ticket_type": "INCIDENT",
  "category": "Network",
  "target_role": "Technician",
  "notify_enabled": true,
  "email_enabled": true,
  "is_active": true
}
```

- `event_type`: `RESPONSE_BREACH` | `RESOLUTION_BREACH`
- `priority`: `Low` | `Medium` | `High` | `Critical`
- `ticket_type`: `INCIDENT` | `SERVICE_REQUEST` | `null`
- `target_role`: `Admin` | `Technician` (Employees are never escalation recipients)
- `precedence` is **derived** (2/3/4) and cannot be set directly.

`PUT` accepts any subset of the create fields (partial update). Changing
`ticket_type`/`category` recomputes `precedence`.

**List query parameters**: `page` (>=1), `page_size` (1–100), `is_active`,
`event_type`, `priority`.

**Rule response**

```json
{
  "id": 12,
  "name": "High priority incident escalation",
  "description": null,
  "event_type": "RESPONSE_BREACH",
  "priority": "High",
  "ticket_type": "INCIDENT",
  "category": "Network",
  "target_role": "Technician",
  "notify_enabled": true,
  "email_enabled": true,
  "is_active": true,
  "precedence": 4,
  "created_at": "2026-10-17T10:00:00Z",
  "updated_at": "2026-10-17T10:00:00Z"
}
```

`DELETE /escalations/rules/{rule_id}` returns:

```json
{ "message": "Escalation rule deactivated successfully", "rule_id": 12, "is_active": false }
```

Rules are never hard-deleted so historical escalation records keep their
`rule_id` references.

### Escalation records (read-only)

Escalation records are created by the automatic escalation pipeline when an SLA
breach is processed. These endpoints expose them (with delivery status) to
Admins.

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/escalations/records` | List records (paginated, newest first). |
| `GET` | `/escalations/records/{record_id}` | Retrieve one record. |

**List query parameters**: `page`, `page_size`, `event_type`, `ticket_id`,
`rule_id`, `email_sent`.

**Record response**

```json
{
  "id": 5,
  "ticket_id": 42,
  "event_type": "RESPONSE_BREACH",
  "rule_id": 12,
  "recipient_id": 3,
  "notification_created": true,
  "notification_id": 88,
  "email_sent": false,
  "email_error": "SMTPException: relay refused",
  "delivery_status": "failed",
  "history_recorded": true,
  "ticket_title": "VPN down for HQ",
  "recipient_name": "Tech User",
  "recipient_role": "Technician",
  "rule_name": "High priority incident escalation",
  "created_at": "2026-10-17T10:05:00Z",
  "updated_at": "2026-10-17T10:05:00Z"
}
```

`delivery_status` is derived (never asserted optimistically):

| Value | Meaning |
|-------|---------|
| `delivered` | The email provider confirmed success (`email_sent == true`). |
| `failed` | An attempt was made and an error was recorded. |
| `not_attempted` | No email attempt was made (e.g. `email_enabled` was false). |

---

## Related existing endpoints

These were added in earlier phases and are **not modified** by this milestone,
but are relevant to escalation visibility:

- `GET /analytics/escalations` (Admin) — escalation metrics used by the frontend
  `EscalationOverview` component.
- `GET /reports/escalations` and `GET /reports/escalations/export` (Admin) —
  escalation report summary and CSV export.
