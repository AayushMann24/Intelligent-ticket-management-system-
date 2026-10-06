"""
Reports Router (Phase 2E - Checkpoint 3)

Provides Admin-only reporting endpoints with CSV export.
"""

from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.dependencies.roles import require_admin
from app.services.report_service import (
    REPORT_TYPES,
    generate_ticket_report_rows,
    get_ticket_report_summary,
    generate_sla_report_rows,
    get_sla_report_summary,
    generate_sla_breach_report_rows,
    generate_escalation_report_rows,
    get_escalation_report_summary,
    generate_technician_report_rows,
    get_technician_report_summary,
    _generate_csv_stream,
    _build_report_filename,
)
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
    dependencies=[Depends(require_admin)],  # Admin-only access
)


def _parse_date(date_str: Optional[str]) -> Optional[datetime]:
    """Parse date string to datetime."""
    if not date_str:
        return None
    try:
        # Try parsing as date only
        return datetime.fromisoformat(date_str)
    except ValueError:
        try:
            # Try parsing with time
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid date format: {date_str}. Use ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)"
            )


# ======================================================
# Helper: Build filter dict from query params
# ======================================================

def _build_filters(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    ticket_type: Optional[str] = None,
    assignee_id: Optional[int] = None,
    status: Optional[str] = None,
    breach_type: Optional[str] = None,
) -> dict:
    """Build filters dict from query parameters."""
    filters = {}
    if start_date:
        filters["start_date"] = _parse_date(start_date)
    if end_date:
        filters["end_date"] = _parse_date(end_date)
    if priority:
        filters["priority"] = priority
    if category:
        filters["category"] = category
    if ticket_type:
        filters["ticket_type"] = ticket_type
    if assignee_id:
        filters["assignee_id"] = assignee_id
    if status:
        filters["status"] = status
    if breach_type:
        filters["breach_type"] = breach_type
    return filters


# ======================================================
# Generic CSV Export Endpoint
# ======================================================

def _create_csv_response(
    report_type: str,
    headers: List[str],
    row_generator,
    filters: dict,
    summary: dict,
):
    """Create a streaming CSV response with metadata in headers."""
    filename = _build_report_filename(report_type, filters.get("start_date"), filters.get("end_date"))
    
    def generate():
        # Yield summary as first row (commented out for CSV compatibility)
        # We'll include summary in custom headers instead
        yield from _generate_csv_stream(headers, row_generator())
    
    response = StreamingResponse(
        generate(),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "X-Report-Type": report_type,
            "X-Report-Generated": datetime.now(timezone.utc).isoformat(),
            "X-Report-Summary": str(summary).replace(",", ";"),  # Simple summary in header
        },
    )
    return response


# Import timezone for timestamp
from datetime import timezone


# ======================================================
# Ticket Report Endpoints
# ======================================================

@router.get(
    "/tickets",
    summary="Get ticket report (JSON summary)",
    description="Get ticket report summary with filters. Use /tickets/export for CSV download.",
)
def tickets_report(
    start_date: Optional[str] = Query(None, description="Filter start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Filter end date (YYYY-MM-DD)"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    category: Optional[str] = Query(None, description="Filter by category"),
    ticket_type: Optional[str] = Query(None, description="Filter by ticket type"),
    assignee_id: Optional[int] = Query(None, description="Filter by assignee ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
):
    """Get ticket report summary."""
    logger.info("Admin requested ticket report summary")
    filters = _build_filters(start_date, end_date, priority, category, ticket_type, assignee_id, status)
    summary = get_ticket_report_summary(db, **filters)
    return {
        "report_type": "tickets",
        "filters": {k: v.isoformat() if isinstance(v, datetime) else v for k, v in filters.items()},
        "summary": summary,
    }


@router.get(
    "/tickets/export",
    summary="Export ticket report as CSV",
    description="Download ticket report as CSV file with all ticket details.",
)
def export_tickets_report(
    start_date: Optional[str] = Query(None, description="Filter start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Filter end date (YYYY-MM-DD)"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    category: Optional[str] = Query(None, description="Filter by category"),
    ticket_type: Optional[str] = Query(None, description="Filter by ticket type"),
    assignee_id: Optional[int] = Query(None, description="Filter by assignee ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
):
    """Export ticket report as CSV."""
    logger.info("Admin requested ticket report CSV export")
    filters = _build_filters(start_date, end_date, priority, category, ticket_type, assignee_id, status)
    summary = get_ticket_report_summary(db, **filters)
    
    def row_gen():
        yield from generate_ticket_report_rows(db, **filters)
    
    return _create_csv_response("tickets", REPORT_TYPES["tickets"]["headers"], row_gen, filters, summary)


# ======================================================
# SLA Compliance Report Endpoints
# ======================================================

@router.get(
    "/sla",
    summary="Get SLA compliance report (JSON summary)",
    description="Get SLA compliance report summary with filters. Use /sla/export for CSV download.",
)
def sla_report(
    start_date: Optional[str] = Query(None, description="Filter start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Filter end date (YYYY-MM-DD)"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    category: Optional[str] = Query(None, description="Filter by category"),
    ticket_type: Optional[str] = Query(None, description="Filter by ticket type"),
    assignee_id: Optional[int] = Query(None, description="Filter by assignee ID"),
    db: Session = Depends(get_db),
):
    """Get SLA compliance report summary."""
    logger.info("Admin requested SLA compliance report summary")
    filters = _build_filters(start_date, end_date, priority, category, ticket_type, assignee_id)
    summary = get_sla_report_summary(db, **filters)
    return {
        "report_type": "sla",
        "filters": {k: v.isoformat() if isinstance(v, datetime) else v for k, v in filters.items()},
        "summary": summary,
    }


@router.get(
    "/sla/export",
    summary="Export SLA compliance report as CSV",
    description="Download SLA compliance report as CSV file.",
)
def export_sla_report(
    start_date: Optional[str] = Query(None, description="Filter start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Filter end date (YYYY-MM-DD)"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    category: Optional[str] = Query(None, description="Filter by category"),
    ticket_type: Optional[str] = Query(None, description="Filter by ticket type"),
    assignee_id: Optional[int] = Query(None, description="Filter by assignee ID"),
    db: Session = Depends(get_db),
):
    """Export SLA compliance report as CSV."""
    logger.info("Admin requested SLA compliance report CSV export")
    filters = _build_filters(start_date, end_date, priority, category, ticket_type, assignee_id)
    summary = get_sla_report_summary(db, **filters)
    
    def row_gen():
        yield from generate_sla_report_rows(db, **filters)
    
    return _create_csv_response("sla", REPORT_TYPES["sla"]["headers"], row_gen, filters, summary)


# ======================================================
# SLA Breach Report Endpoints
# ======================================================

@router.get(
    "/sla/breaches",
    summary="Get SLA breach report (JSON summary)",
    description="Get SLA breach report summary with filters. Use /sla/breaches/export for CSV download.",
)
def sla_breaches_report(
    start_date: Optional[str] = Query(None, description="Filter start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Filter end date (YYYY-MM-DD)"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    category: Optional[str] = Query(None, description="Filter by category"),
    ticket_type: Optional[str] = Query(None, description="Filter by ticket type"),
    assignee_id: Optional[int] = Query(None, description="Filter by assignee ID"),
    breach_type: Optional[str] = Query(None, description="Filter by breach type: response, resolution, or all"),
    db: Session = Depends(get_db),
):
    """Get SLA breach report summary."""
    logger.info("Admin requested SLA breach report summary")
    filters = _build_filters(start_date, end_date, priority, category, ticket_type, assignee_id, breach_type=breach_type)
    # Reuse SLA summary for breaches
    summary = get_sla_report_summary(db, **{k: v for k, v in filters.items() if k != "breach_type"})
    return {
        "report_type": "sla_breaches",
        "filters": {k: v.isoformat() if isinstance(v, datetime) else v for k, v in filters.items()},
        "summary": summary,
    }


@router.get(
    "/sla/breaches/export",
    summary="Export SLA breach report as CSV",
    description="Download SLA breach report as CSV file.",
)
def export_sla_breaches_report(
    start_date: Optional[str] = Query(None, description="Filter start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Filter end date (YYYY-MM-DD)"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    category: Optional[str] = Query(None, description="Filter by category"),
    ticket_type: Optional[str] = Query(None, description="Filter by ticket type"),
    assignee_id: Optional[int] = Query(None, description="Filter by assignee ID"),
    breach_type: Optional[str] = Query(None, description="Filter by breach type: response, resolution, or all"),
    db: Session = Depends(get_db),
):
    """Export SLA breach report as CSV."""
    logger.info("Admin requested SLA breach report CSV export")
    filters = _build_filters(start_date, end_date, priority, category, ticket_type, assignee_id, breach_type=breach_type)
    summary = get_sla_report_summary(db, **{k: v for k, v in filters.items() if k != "breach_type"})
    
    def row_gen():
        yield from generate_sla_breach_report_rows(db, **filters)
    
    return _create_csv_response("sla_breaches", REPORT_TYPES["sla_breaches"]["headers"], row_gen, filters, summary)


# ======================================================
# Escalation Report Endpoints
# ======================================================

@router.get(
    "/escalations",
    summary="Get escalation report (JSON summary)",
    description="Get escalation report summary with filters. Use /escalations/export for CSV download.",
)
def escalations_report(
    start_date: Optional[str] = Query(None, description="Filter start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Filter end date (YYYY-MM-DD)"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    category: Optional[str] = Query(None, description="Filter by category"),
    ticket_type: Optional[str] = Query(None, description="Filter by ticket type"),
    assignee_id: Optional[int] = Query(None, description="Filter by assignee ID"),
    db: Session = Depends(get_db),
):
    """Get escalation report summary."""
    logger.info("Admin requested escalation report summary")
    filters = _build_filters(start_date, end_date, priority, category, ticket_type, assignee_id)
    summary = get_escalation_report_summary(db, **filters)
    return {
        "report_type": "escalations",
        "filters": {k: v.isoformat() if isinstance(v, datetime) else v for k, v in filters.items()},
        "summary": summary,
    }


@router.get(
    "/escalations/export",
    summary="Export escalation report as CSV",
    description="Download escalation report as CSV file.",
)
def export_escalations_report(
    start_date: Optional[str] = Query(None, description="Filter start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Filter end date (YYYY-MM-DD)"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    category: Optional[str] = Query(None, description="Filter by category"),
    ticket_type: Optional[str] = Query(None, description="Filter by ticket type"),
    assignee_id: Optional[int] = Query(None, description="Filter by assignee ID"),
    db: Session = Depends(get_db),
):
    """Export escalation report as CSV."""
    logger.info("Admin requested escalation report CSV export")
    filters = _build_filters(start_date, end_date, priority, category, ticket_type, assignee_id)
    summary = get_escalation_report_summary(db, **filters)
    
    def row_gen():
        yield from generate_escalation_report_rows(db, **filters)
    
    return _create_csv_response("escalations", REPORT_TYPES["escalations"]["headers"], row_gen, filters, summary)


# ======================================================
# Technician Workload Report Endpoints
# ======================================================

@router.get(
    "/technicians",
    summary="Get technician workload report (JSON summary)",
    description="Get technician workload report summary with filters. Use /technicians/export for CSV download.",
)
def technicians_report(
    start_date: Optional[str] = Query(None, description="Filter start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Filter end date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
):
    """Get technician workload report summary."""
    logger.info("Admin requested technician workload report summary")
    filters = _build_filters(start_date, end_date)
    summary = get_technician_report_summary(db, **filters)
    return {
        "report_type": "technicians",
        "filters": {k: v.isoformat() if isinstance(v, datetime) else v for k, v in filters.items()},
        "summary": summary,
    }


@router.get(
    "/technicians/export",
    summary="Export technician workload report as CSV",
    description="Download technician workload report as CSV file.",
)
def export_technicians_report(
    start_date: Optional[str] = Query(None, description="Filter start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Filter end date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
):
    """Export technician workload report as CSV."""
    logger.info("Admin requested technician workload report CSV export")
    filters = _build_filters(start_date, end_date)
    summary = get_technician_report_summary(db, **filters)
    
    def row_gen():
        yield from generate_technician_report_rows(db, **filters)
    
    return _create_csv_response("technicians", REPORT_TYPES["technicians"]["headers"], row_gen, filters, summary)


# ======================================================
# Report Metadata Endpoint
# ======================================================

@router.get(
    "/",
    summary="List available report types",
    description="Get metadata about all available report types and their filters.",
)
def list_reports():
    """List all available report types."""
    return {
        "reports": [
            {
                "type": key,
                "name": value["name"],
                "description": value["description"],
                "filters": value["filters"],
                "endpoints": {
                    "json": f"/reports/{key}",
                    "csv": f"/reports/{key}/export",
                },
            }
            for key, value in REPORT_TYPES.items()
        ]
    }