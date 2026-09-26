"""
SLA Background Scheduler (Phase 2C-2)

Uses APScheduler for lightweight background job execution.
APScheduler is used instead of Celery/Redis because:
- No existing task queue infrastructure
- Simple interval-based scheduling needs
- Can run in-process with FastAPI lifespan
- Lightweight and no external dependencies beyond the scheduler itself
"""

import logging
from contextlib import asynccontextmanager
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.config import settings
from app.database.connection import SessionLocal
from app.services.sla_breach_service import check_all_sla_breaches

logger = logging.getLogger(__name__)

# Global scheduler instance
_scheduler: Optional[AsyncIOScheduler] = None


async def sla_breach_check_job() -> None:
    """
    Scheduled job to check for SLA breaches.
    Runs in its own database session.
    """
    logger.info("Starting scheduled SLA breach check")

    db = SessionLocal()
    try:
        results = check_all_sla_breaches(db)

        logger.info(
            "SLA breach check completed",
            extra={
                "response_candidates": results["response_candidates"],
                "response_breaches_processed": results["response_breaches_processed"],
                "resolution_candidates": results["resolution_candidates"],
                "resolution_breaches_processed": results["resolution_breaches_processed"],
                "errors_count": len(results["errors"]),
            },
        )

        if results["errors"]:
            for error in results["errors"]:
                logger.error("SLA breach check error", extra={"error": error})

    except Exception as e:
        logger.exception("SLA breach check job failed", extra={"error": str(e)})
    finally:
        db.close()


def get_scheduler() -> AsyncIOScheduler:
    """Get or create the global scheduler instance."""
    global _scheduler
    if _scheduler is None:
        _scheduler = AsyncIOScheduler()
    return _scheduler


def start_sla_scheduler() -> None:
    """Start the SLA breach monitoring scheduler."""
    if not settings.sla_monitor_enabled:
        logger.info("SLA monitor is disabled via configuration")
        return

    global _scheduler
    scheduler = get_scheduler()

    if scheduler.running:
        logger.warning("SLA scheduler already running")
        return

    # Add the periodic job
    interval = settings.sla_check_interval_seconds
    scheduler.add_job(
        sla_breach_check_job,
        trigger=IntervalTrigger(seconds=interval),
        id="sla_breach_check",
        name="SLA Breach Detection",
        replace_existing=True,
        max_instances=1,  # Prevent overlapping executions
        coalesce=True,    # If multiple intervals pass, run once
        misfire_grace_time=30,  # Allow up to 30s grace for misfires
    )

    scheduler.start()
    logger.info(
        "SLA scheduler started",
        extra={"interval_seconds": interval},
    )


def stop_sla_scheduler() -> None:
    """Stop the SLA breach monitoring scheduler."""
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=True)
        _scheduler = None
        logger.info("SLA scheduler stopped")
    elif _scheduler:
        _scheduler = None


@asynccontextmanager
async def sla_scheduler_lifespan(app):
    """
    FastAPI lifespan context manager for SLA scheduler.
    Ensures scheduler starts on startup and stops on shutdown.
    """
    # Startup
    start_sla_scheduler()
    try:
        yield
    finally:
        # Shutdown
        stop_sla_scheduler()


def is_scheduler_running() -> bool:
    """Check if scheduler is running (for health checks)."""
    global _scheduler
    return _scheduler is not None and _scheduler.running


def get_scheduler_status() -> dict:
    """Get scheduler status for admin/debug endpoints."""
    global _scheduler
    if _scheduler is None:
        return {
            "running": False,
            "enabled": settings.sla_monitor_enabled,
            "interval_seconds": settings.sla_check_interval_seconds,
            "jobs": [],
        }

    jobs = []
    for job in _scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
            "trigger": str(job.trigger),
        })

    return {
        "running": _scheduler.running,
        "enabled": settings.sla_monitor_enabled,
        "interval_seconds": settings.sla_check_interval_seconds,
        "jobs": jobs,
    }