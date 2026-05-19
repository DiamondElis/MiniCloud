from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.auth import Caller, audit_success, require_cloudwatch_auth
from app.core.errors import conflict, not_found
from app.core.time import ensure_utc
from app.db.session import get_db
from app.models.event import Event, EventBus
from app.repositories.events_repo import get_event_bus
from app.schemas.requests import CreateEventBusRequest, PutEventRequest
from app.schemas.responses import EventBusResponse, EventResponse

router = APIRouter(prefix="/cloudwatch", tags=["events"])


@router.post("/event-buses", response_model=EventBusResponse)
def create_event_bus(
    payload: CreateEventBusRequest,
    request: Request,
    _: Caller = Depends(require_cloudwatch_auth("cloudwatch:PutEvents", "event-bus/*")),
    db: Session = Depends(get_db),
) -> EventBus:
    bus = EventBus(name=payload.name)
    db.add(bus)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise conflict("Duplicate event bus") from exc
    db.refresh(bus)
    audit_success(request, db, {"event_bus": bus.name})
    return bus


@router.get("/event-buses", response_model=list[EventBusResponse])
def list_event_buses(
    request: Request,
    _: Caller = Depends(require_cloudwatch_auth("cloudwatch:GetEvents", "event-bus/*")),
    db: Session = Depends(get_db),
) -> list[EventBus]:
    buses = list(db.execute(select(EventBus).order_by(EventBus.name)).scalars())
    audit_success(request, db)
    return buses


@router.post("/events", response_model=EventResponse)
def put_event(
    payload: PutEventRequest,
    request: Request,
    _: Caller = Depends(require_cloudwatch_auth("cloudwatch:PutEvents", "event-bus/*")),
    db: Session = Depends(get_db),
) -> Event:
    bus = get_event_bus(db, payload.event_bus)
    if not bus:
        raise not_found("Event bus not found")
    event = Event(
        event_bus_id=bus.id,
        source=payload.source,
        detail_type=payload.detail_type,
        detail=payload.detail,
        resources=payload.resources,
        timestamp=ensure_utc(payload.timestamp),
        request_id=payload.request_id,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    audit_success(request, db, {"event_bus": payload.event_bus, "source": payload.source})
    return event


@router.get("/events", response_model=list[EventResponse])
def list_events(
    request: Request,
    source: str | None = None,
    detail_type: str | None = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    _: Caller = Depends(require_cloudwatch_auth("cloudwatch:GetEvents", "event-bus/*")),
    db: Session = Depends(get_db),
) -> list[Event]:
    stmt = select(Event)
    if source:
        stmt = stmt.where(Event.source == source)
    if detail_type:
        stmt = stmt.where(Event.detail_type == detail_type)
    events = list(db.execute(stmt.order_by(Event.timestamp.desc()).limit(limit).offset(offset)).scalars())
    audit_success(request, db)
    return events

