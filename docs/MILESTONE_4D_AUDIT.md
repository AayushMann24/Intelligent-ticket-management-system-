# Milestone 4D — Ticket Workflow UI Audit Report

**Date:** 2026-10-19  
**Scope:** Audit of ticket workflow backend APIs, frontend services/hooks, role/permission rules, and `TicketDetailsModal` to determine UI implementation requirements.

---

## 1. Existing Workflow API Contract Table

| Action | Endpoint | Method | Auth Requirement | Request Payload | Response | Status |
|--------|----------|--------|------------------|-----------------|----------|--------|
| **Assign Ticket** | `/tickets/{id}/assign` | PUT | `require_admin` | `{ assigned_to: number }` | `TicketResponse` | ✅ Implemented |
| **Reassign Ticket** | `/tickets/{id}/reassign` | PUT | `require_admin` | `{ assigned_to: number }` | `TicketResponse` | ✅ Implemented |
| **Unassign Ticket** | `/tickets/{id}/unassign` | POST | `require_admin` | `{}` (empty `TicketUnassign`) | `TicketResponse` | ✅ Implemented |
| **Start Work** | `/tickets/{id}/start-work` | POST | `require_admin_or_technician` | `{}` | `TicketResponse` | ✅ Implemented |
| **Mark Pending** | `/tickets/{id}/mark-pending` | POST | `require_admin_or_technician` | `{}` | `TicketResponse` | ✅ Implemented |
| **Resolve Ticket** | `/tickets/{id}/resolve` | POST | `require_admin_or_technician` | `{ resolution_summary: string }` | `TicketResponse` | ✅ Implemented |
| **Reopen Ticket** | `/tickets/{id}/reopen` | POST | `require_authenticated_user` | `{ reason?: string }` | `TicketResponse` | ✅ Implemented |
| **Close Ticket** | `/tickets/{id}/close` | POST | `require_admin_or_technician` | `{}` (empty `TicketClose`) | `TicketResponse` | ✅ Implemented |
| **Escalate Ticket** | `/tickets/{id}/escalate` | POST | `require_admin_or_technician` | `{ escalated_to: number, escalation_reason: string }` | `TicketResponse` | ✅ Implemented |
| **Get Workflow Actions** | `/tickets/{id}/workflow-actions` | GET | `require_authenticated_user` | — | `WorkflowActions` | ✅ Implemented |
| **Update Status (Legacy)** | `/tickets/{id}/status` | PATCH | `require_admin_or_technician` | `{ status: string }` | `TicketResponse` | ✅ Implemented |
| **Get History** | `/tickets/{id}/history` | GET | `require_authenticated_user` | `page`, `page_size` | `TicketHistoryListResponse` | ✅ Implemented |
| **Get Timeline** | `/tickets/{id}/timeline` | GET | `require_authenticated_user` | `page`, `page_size` | `TimelineResponse` | ✅ Implemented |

**Key Contract Details (Confirmed from `backend/app/routers/ticket.py` and `backend/app/schemas/ticket.py`):**

- All workflow endpoints require CSRF protection (`Depends(csrf_protect)`)
- Status values are enum: `Open`, `Assigned`, `In Progress`, `Pending`, `Resolved`, `Closed`
- `TicketAssign` payload: `{ assigned_to: int }` — target must be Admin or Technician
- `TicketResolve` payload: `{ resolution_summary: string }` — required, non-empty
- `TicketReopen` payload: `{ reason?: string }` — optional
- `TicketEscalate` payload: `{ escalated_to: int, escalation_reason: string }` — both required
- `WorkflowActions` response (from `types/ticket.ts:163-174`): 10 boolean flags + `valid_status_transitions: string[]`

---

## 2. Current Frontend Integration Status

### 2.1 Services Layer (`frontend/src/services/ticketService.ts`)
**Status: ✅ Complete** — All 13 workflow endpoints wrapped with correct signatures:
- Lines 86–189: `assignTicket`, `reassignTicket`, `unassignTicket`, `startWork`, `markPending`, `resolveTicket`, `reopenTicket`, `closeTicket`, `escalateTicket`, `getWorkflowActions`, `updateTicketStatus`
- Lines 254–268: `getHistory`, `getTimeline`
- Proper TypeScript types imported from `../types/ticket`

### 2.2 Hooks Layer (`frontend/src/hooks/useTickets.ts`)
**Status: ✅ Complete** — All service functions exposed with consistent pattern:
- Lines 109–244: `assignTechnician`, `reassignTechnician`, `unassignTechnician`, `startWorkOnTicket`, `markTicketPending`, `resolveTicketAction`, `reopenTicketAction`, `closeTicketAction`, `escalateTicketAction`, `fetchWorkflowActions`, `changeStatus`
- Each calls service then `loadTickets()` for refresh
- Error handling via `console.error` only (no user-facing feedback)

### 2.3 Types (`frontend/src/types/ticket.ts`)
**Status: ✅ Complete** — Full type coverage:
- `TicketStatus` (line 2): `Open | Assigned | In Progress | Pending | Resolved | Closed`
- `WorkflowActions` (lines 163–174): 10 boolean flags + transitions array
- Payload interfaces: `AssignPayload`, `ResolvePayload`, `ReopenPayload`, `ClosePayload`, `EscalatePayload`
- `TimelineItem` / `TimelineResponse` for combined history+comments+attachments view

### 2.4 Components — `TicketDetailsModal.tsx`
**Status: ⚠️ Read-Only Display Only** — Currently shows ticket details but **no workflow controls**:
- Displays: ID, status badge, title, description, AI analysis, priority, assignment, metadata, SLA, attachments
- No buttons for assign, start work, resolve, reopen, close, escalate, etc.
- No timeline/history tab — only static sections

### 2.5 Pages — `TicketsPage.tsx`
**Status: ⚠️ Basic CRUD Only** — Uses `useTickets` for list/create/edit/delete/view but:
- View opens `TicketDetailsModal` (read-only)
- No workflow action buttons in table or modal
- Toolbar filters only (search, status, priority)

---

## 3. Role/Permission and Transition Matrix

### 3.1 Valid Status Transitions (`backend/app/services/ticket_service.py:40-72`)
```python
VALID_TRANSITIONS = {
    "Open": ["Assigned", "In Progress", "Resolved", "Closed"],
    "Assigned": ["In Progress", "Open", "Resolved", "Closed"],
    "In Progress": ["Pending", "Resolved", "Open", "Assigned"],
    "Pending": ["In Progress", "Resolved", "Open"],
    "Resolved": ["Closed", "Open", "In Progress"],
    "Closed": ["Open"],
}
```

### 3.2 Role-Based Transition Permissions (`ticket_service.py:76-108`)
| From → To | Allowed Roles |
|-----------|---------------|
| Open → Assigned | Admin |
| Open → In Progress | Admin, Technician |
| Open → Resolved | Admin, Technician |
| Open → Closed | Admin |
| Assigned → In Progress | Admin, Technician |
| Assigned → Open | Admin, Technician |
| Assigned → Resolved | Admin, Technician |
| Assigned → Closed | Admin |
| In Progress → Pending | Admin, Technician |
| In Progress → Resolved | Admin, Technician |
| In Progress → Open | Admin, Technician |
| In Progress → Assigned | Admin |
| Pending → In Progress | Admin, Technician |
| Pending → Resolved | Admin, Technician |
| Pending → Open | Admin, Technician |
| Resolved → Closed | Admin, Technician |
| Resolved → Open | Admin, Technician |
| Resolved → In Progress | Admin, Technician |
| Closed → Open | Admin |

### 3.3 Workflow Action Permissions (`get_workflow_actions` in `ticket_service.py:1215-1284`)
| Action | Required Role | Additional Conditions |
|--------|---------------|----------------------|
| `can_assign` | Admin | Ticket unassigned, status = Open |
| `can_reassign` | Admin | Ticket assigned |
| `can_unassign` | Admin | Ticket assigned |
| `can_start_work` | Admin or Assignee | Ticket assigned, status ∈ {Open, Assigned}, `In Progress` in valid transitions |
| `can_mark_pending` | Admin or Assignee | Ticket assigned, status = In Progress, `Pending` in valid transitions |
| `can_resolve` | Admin or Assignee | Ticket assigned, `Resolved` in valid transitions |
| `can_reopen` | Admin, Creator, or Assignee | Status ∈ {Resolved, Closed} |
| `can_close` | Admin or Technician (own) | Status = Resolved, `Closed` in valid transitions |
| `can_escalate` | Admin or Technician (own) | Always if authorized |

### 3.4 Resource-Level Authorization (`ticket_utils.py`)
- **View**: Admin, Creator, Assignee
- **Modify (basic fields)**: Admin, Creator, Assignee
- **Delete**: Admin only
- **Comments**: Admin, Creator, Assignee (internal notes: Admin/Technician only)
- **History/Timeline**: Same as view

---

## 4. Missing UI Capabilities

### 4.1 TicketDetailsModal — Critical Gaps
| Capability | Status | Required Input | Notes |
|------------|--------|----------------|-------|
| **Assign/Reassign** | ❌ Missing | User selector (Admin/Technician list) | Only Admin; need `getAvailableTechnicians` endpoint |
| **Unassign** | ❌ Missing | Confirmation only | Admin only |
| **Start Work** | ❌ Missing | None (single button) | Assignee/Admin; status must be Open/Assigned |
| **Mark Pending** | ❌ Missing | **Pending reason** (API doesn't require but UX should) | Assignee/Admin; status must be In Progress |
| **Resolve** | ❌ Missing | **Resolution summary** (required by API) | Assignee/Admin; multi-line input |
| **Reopen** | ❌ Missing | **Reopen reason** (optional) | Creator/Assignee/Admin; status Resolved/Closed |
| **Close** | ❌ Missing | Confirmation only | Assignee/Admin; status must be Resolved |
| **Escalate** | ❌ Missing | Target user selector + **Escalation reason** (required) | Assignee/Admin; target must be Admin/Technician |
| **View History/Timeline** | ❌ Missing | Tabbed view | Already have `/timeline` endpoint returning combined events |
| **Refresh after action** | ❌ Missing | Auto-reload ticket | `useTickets` hook has `reloadTickets` but not used in modal |

### 4.2 Supporting Features Needed
| Feature | Status | Notes |
|---------|--------|-------|
| Technician/User picker for assign/reassign/escalate | ❌ Missing | Need new service: `getAvailableTechnicians` (exists in backend `ticket_service.py:163` but no router) |
| Loading states per action | ❌ Missing | Button-level `disabled` + spinner |
| Error handling with user feedback | ❌ Missing | Toast/notification integration (`useNotifications` exists) |
| Success feedback | ❌ Missing | Toast + auto-close modal or refresh |
| Workflow action buttons conditionally rendered | ❌ Missing | Must call `fetchWorkflowActions` and render based on flags |
| Timeline/History tab in modal | ❌ Missing | Use `getTimeline` for combined chronological view |

---

## 5. Recommended Implementation Sequence

### Phase 1: Core Workflow Controls in TicketDetailsModal
1. **Add `fetchWorkflowActions` call** when modal opens (effect with `ticket.id`)
2. **Render action buttons conditionally** based on `WorkflowActions` flags
3. **Implement Assign/Reassign/Unassign** (Admin only):
   - Add technician picker (fetch from new `/users/technicians` endpoint or reuse `/users`)
   - Modal dialog for user selection
4. **Implement Start Work / Mark Pending** (Assignee/Admin):
   - Simple button with confirmation
5. **Implement Resolve** (Assignee/Admin):
   - Dialog with required `resolution_summary` textarea
6. **Implement Reopen** (Creator/Assignee/Admin):
   - Dialog with optional reason
7. **Implement Close** (Assignee/Admin):
   - Confirmation dialog
8. **Implement Escalate** (Assignee/Admin):
   - Dialog with technician picker + required reason

### Phase 2: History/Timeline Display
9. **Add tabbed interface** in `TicketDetailsModal`: Details | Timeline
10. **Fetch timeline** via `getTimeline` on tab activation
11. **Render timeline items** by type (history, comment, internal note, attachment)
12. **Style event types** with icons/colors matching `HistoryEventType` enum

### Phase 3: Polish & Integration
13. **Add loading/error/success states** per action (integrate `useNotifications`)
14. **Auto-refresh ticket** after successful action (call `reloadTickets` or re-fetch single ticket)
15. **Add keyboard shortcuts** (Escape to close dialogs, Enter to submit)
16. **Responsive layout** for mobile (action buttons in dropdown/menu)

---

## 6. Files Expected to Change

| File | Change Type | Description |
|------|-------------|-------------|
| `frontend/src/components/tickets/TicketDetailsModal.tsx` | **Major** | Add workflow action buttons, dialogs, timeline tab, state management |
| `frontend/src/hooks/useTickets.ts` | **Minor** | Add `fetchTechnicians` (new), expose `reloadTicket` (single) |
| `frontend/src/services/ticketService.ts` | **Minor** | Add `getTechnicians` / `getAvailableTechnicians` wrapper |
| `backend/app/routers/ticket.py` | **Minor** | Add `GET /tickets/technicians` endpoint (or reuse `/users` with role filter) |
| `frontend/src/types/ticket.ts` | **None** | Types already complete |
| `frontend/src/pages/TicketsPage.tsx` | **Minor** | Pass `reloadTickets` to modal or add single-ticket refresh |

**New Files (Potential):**
- `frontend/src/components/tickets/WorkflowActionButtons.tsx` — extracted action button group
- `frontend/src/components/tickets/TechnicianPicker.tsx` — reusable user selector
- `frontend/src/components/tickets/TimelineTab.tsx` — timeline rendering component

---

## 7. Regression Risks and Required Tests

### 7.1 Backend Regression Risks (Must Preserve)
| Risk | Mitigation |
|------|------------|
| Workflow-history persistence (fixed in previous milestone) | Run `backend/tests/test_tickets.py::TestTicketHistory` and `::TestTicketTimeline` |
| Status transition validation | Run `backend/tests/test_tickets.py` workflow tests |
| Role-based authorization | Run `TestTicketAuthorization` class |
| SLA breach detection on status changes | Run `TestSLABreach` class |
| Notification creation on workflow events | Verify `create_notification` calls in service layer |

### 7.2 Frontend Regression Risks
| Risk | Mitigation |
|------|------------|
| `TicketDetailsModal` existing display logic | Snapshot tests for modal rendering with various ticket states |
| `useTickets` hook `loadTickets` behavior | Ensure new actions call `reloadTickets` correctly |
| `TicketTable` view/edit/delete actions | Verify props unchanged |

### 7.3 Required New Tests
| Test | Location | Type |
|------|----------|------|
| Workflow action buttons render per `WorkflowActions` flags | `TicketDetailsModal.test.tsx` | Unit |
| Each action calls correct service and refreshes | `useTickets.test.ts` | Unit |
| Technician picker fetches and filters correctly | `TechnicianPicker.test.tsx` | Unit |
| Timeline tab displays history + comments + attachments chronologically | `TimelineTab.test.tsx` | Unit |
| Error toasts appear on API failure | Integration | E2E |
| Role-based button visibility (Admin vs Technician vs Employee) | E2E | E2E |

---

## 8. Contract Gaps / Ambiguities Requiring Resolution

| # | Gap / Ambiguity | Impact | Resolution Needed |
|---|-----------------|--------|-------------------|
| **1** | **No `/users/technicians` endpoint** — Frontend needs list of assignable users (Admin/Technician). Backend has `get_available_technicians` in service but no router. | Blocks Assign/Reassign/Escalate UI | **Decision:** Add `GET /users/technicians` router or extend `/users` with `role` filter. |
| **2** | **Mark Pending requires no reason in API** — But UX should capture reason. | UX inconsistency if not captured | **Decision:** Add optional `reason` to `mark-pending` payload (backend change) or capture client-side only (frontend note). |
| **3** | **Escalation target validation** — API validates target is Admin/Technician. UI should pre-filter picker. | UX: prevent invalid selection | Use `/users/technicians` endpoint (same as #1). |
| **4** | **WorkflowActions `valid_status_transitions` includes statuses user cannot trigger** (e.g., Admin sees `Open→Closed` but Technician doesn't). Frontend must not show legacy status dropdown. | Avoid duplicate controls | Use only explicit workflow endpoints; hide legacy status selector in modal. |
| **5** | **Reopen from Closed → Open** vs **Resolved → Open** — API uses different history event types (`TICKET_REOPENED_AFTER_CLOSURE` vs `TICKET_REOPENED`). | Timeline display should distinguish | Timeline already includes `event_type`; render accordingly. |
| **6** | **No single-ticket refresh endpoint** — `useTickets.reloadTickets` refetches all. Acceptable for now but inefficient. | Performance | Defer; add `GET /tickets/{id}` refresh if needed. |
| **7** | **`TicketDetailsModal` receives `ticket` prop** — After workflow action, parent must update this prop. Current `TicketsPage` uses `selectedTicket` state. | State synchronization | Parent (`TicketsPage`) should call `reloadTickets` and re-select ticket, or modal exposes `onRefresh` callback. |
| **8** | **CSRF tokens** — All mutating endpoints require CSRF. Frontend `api` client must include header. | Already handled by `api` interceptor? | Verify `frontend/src/services/api.ts` includes CSRF. |

---

## Summary Classification

| Finding | Classification | Evidence |
|---------|----------------|----------|
| All 10 workflow endpoints exist and validated | **Confirmed** | `backend/app/routers/ticket.py:205-395`, `ticket_service.py:612-1110` |
| `WorkflowActions` endpoint returns correct permissions per role/status | **Confirmed** | `ticket_service.py:1215-1284`, `types/ticket.ts:163-174` |
| Frontend services/hooks fully wrap all endpoints | **Confirmed** | `ticketService.ts:86-199`, `useTickets.ts:109-269` |
| `TicketDetailsModal` has zero workflow controls | **Confirmed** | `TicketDetailsModal.tsx` — read-only display only |
| Technician picker endpoint missing from backend router | **Confirmed** | `get_available_technicians` in service (`ticket_service.py:163`) but no route |
| Mark Pending API lacks reason field | **Confirmed** | `TicketUnassign`/`mark_pending` take empty payload (`schemas/ticket.py:65-66`, `ticket_service.py:848-875`) |
| Timeline endpoint returns combined history+comments+attachments | **Confirmed** | `ticket_history_service.py:154-281`, `TimelineResponse` type |
| Role-based view/modify/delete authorization consistent | **Confirmed** | `ticket_utils.py:18-65`, router dependencies |
| Status transition matrix matches `VALID_TRANSITIONS` + `TRANSITION_PERMISSIONS` | **Confirmed** | `ticket_service.py:40-108` |
| Legacy status update endpoint exists but should be deprecated in UI | **Needs Verification** | `updateTicketStatus` in service/hook — keep for API compat, hide from UI |

---

## Next Steps (Awaiting Approval)

1. **Resolve Gap #1**: Add `GET /users/technicians` router (or decide on `/users?role=Admin,Technician`)
2. **Resolve Gap #2**: Decide if `mark-pending` needs `reason` in API (backend change) or frontend-only capture
3. **Begin Phase 1 Implementation**: Modify `TicketDetailsModal.tsx` to fetch `WorkflowActions` and render conditional action buttons
4. **Create reusable sub-components**: `TechnicianPicker`, `WorkflowActionButtons`, `TimelineTab`
5. **Integrate notifications**: Use existing `useNotifications` for success/error feedback

**Do not begin implementation until gaps #1 and #2 are resolved and this audit is approved.**