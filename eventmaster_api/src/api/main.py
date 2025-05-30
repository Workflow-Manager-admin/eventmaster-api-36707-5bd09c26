from fastapi import FastAPI, HTTPException, Path, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from .models import (
    Event, EventCreate, EventUpdate, Attendee, AttendeeCreate, NotificationRequest
)
from . import logic

app = FastAPI(
    title="EventMaster API",
    description="API for managing events, attendees, notifications, and event queries.",
    version="1.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    return {"message": "Healthy"}


# --- Event CRUD ---


# PUBLIC_INTERFACE
@app.post("/events/", response_model=Event, status_code=201)
def create_event(event: EventCreate):
    """Create a new event."""
    return logic.create_event(event)


# PUBLIC_INTERFACE
@app.get("/events/", response_model=List[Event])
def list_events():
    """List all events."""
    return logic.list_events()


# PUBLIC_INTERFACE
@app.get("/events/{event_id}", response_model=Event)
def get_event(event_id: int = Path(..., gt=0)):
    """Retrieve a single event by ID."""
    event = logic.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


# PUBLIC_INTERFACE
@app.put("/events/{event_id}", response_model=Event)
def update_event(event_id: int, event_update: EventUpdate):
    """Update an event."""
    event = logic.update_event(event_id, event_update)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


# PUBLIC_INTERFACE
@app.delete("/events/{event_id}", status_code=204)
def delete_event(event_id: int):
    """Delete an event."""
    ok = logic.delete_event(event_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Event not found")
    return


# --- Event Search & Filter ---


# PUBLIC_INTERFACE
@app.get("/events/search/", response_model=List[Event])
def search_events(
    title: Optional[str] = Query(None, description="Filter by title"),
    date_from: Optional[str] = Query(None, description="Start date filter (ISO 8601)"),
    date_to: Optional[str] = Query(None, description="End date filter (ISO 8601)"),
    location: Optional[str] = Query(None, description="Location filter"),
    keyword: Optional[str] = Query(None, description="Search keyword"),
):
    """
    Search and filter events by title, date range, location, or keywords.
    """
    from datetime import datetime
    date_from_dt = datetime.fromisoformat(date_from) if date_from else None
    date_to_dt = datetime.fromisoformat(date_to) if date_to else None
    return logic.search_events(
        title, date_from_dt, date_to_dt, location, keyword
    )


# --- Attendee Management ---


# PUBLIC_INTERFACE
@app.post(
    "/events/{event_id}/attendees/", response_model=Attendee, status_code=201
)
def add_attendee(event_id: int, attendee: AttendeeCreate):
    """Add an attendee to an event."""
    result = logic.add_attendee(event_id, attendee)
    if not result:
        raise HTTPException(status_code=404, detail="Event not found")
    return result


# PUBLIC_INTERFACE
@app.get("/events/{event_id}/attendees/", response_model=List[Attendee])
def list_attendees(event_id: int):
    """List all attendees for an event."""
    result = logic.list_attendees(event_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return result


# PUBLIC_INTERFACE
@app.delete(
    "/events/{event_id}/attendees/{attendee_id}",
    status_code=204
)
def remove_attendee(event_id: int, attendee_id: int):
    """Remove an attendee from an event."""
    ok = logic.remove_attendee(event_id, attendee_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Event or Attendee not found")
    return


# PUBLIC_INTERFACE
@app.patch("/events/{event_id}/attendees/{attendee_id}/rsvp")
def set_attendee_rsvp(event_id: int, attendee_id: int, rsvp: bool):
    """Set RSVP status for an attendee."""
    ok = logic.set_rsvp(event_id, attendee_id, rsvp)
    if not ok:
        raise HTTPException(status_code=404, detail="Event or Attendee not found")
    return {"success": True}


# --- Notifications ---


# PUBLIC_INTERFACE
@app.post("/events/{event_id}/notify", status_code=200)
def notify_event_attendees(event_id: int, req: NotificationRequest):
    """Send notification to all attendees of an event."""
    ok = logic.send_event_notification(event_id, req.message)
    if not ok:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"success": True, "message": "Notification sent (simulated)."}


# PUBLIC_INTERFACE
@app.post(
    "/events/{event_id}/attendees/{attendee_id}/notify",
    status_code=200
)
def notify_attendee(event_id: int, attendee_id: int, message: str = Body(...)):
    """Send notification to an attendee."""
    ok = logic.send_attendee_notification(event_id, attendee_id, message)
    if not ok:
        raise HTTPException(status_code=404, detail="Event or Attendee not found")
    return {"success": True, "message": "Notification sent to attendee (simulated)."}
