# Business logic and in-memory storage for EventMaster API
from typing import List, Optional
from threading import Lock
from datetime import datetime


from .models import Event, EventCreate, EventUpdate, Attendee, AttendeeCreate


class Storage:
    event_id_seq = 1
    attendee_id_seq = 1
    events = {}     # event_id: Event
    attendees = {}  # attendee_id: Attendee
    lock = Lock()


storage = Storage()


# PUBLIC_INTERFACE
def create_event(obj: EventCreate) -> Event:
    """Create an event and add to storage."""
    with storage.lock:
        event_id = storage.event_id_seq
        storage.event_id_seq += 1
        event = Event(id=event_id, attendees=[], **obj.model_dump())
        storage.events[event_id] = event
        return event


# PUBLIC_INTERFACE
def get_event(event_id: int) -> Optional[Event]:
    """Return a single event or None."""
    return storage.events.get(event_id)


# PUBLIC_INTERFACE
def update_event(event_id: int, obj: EventUpdate) -> Optional[Event]:
    """Update event details."""
    with storage.lock:
        event = storage.events.get(event_id)
        if not event:
            return None
        data = obj.model_dump(exclude_unset=True)
        for k, v in data.items():
            setattr(event, k, v)
        return event


# PUBLIC_INTERFACE
def delete_event(event_id: int) -> bool:
    """Delete an event by ID."""
    with storage.lock:
        if event_id in storage.events:
            del storage.events[event_id]
            return True
        return False


# PUBLIC_INTERFACE
def list_events() -> List[Event]:
    """List all events."""
    return list(storage.events.values())


# PUBLIC_INTERFACE
def search_events(
    title: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    location: Optional[str] = None,
    keyword: Optional[str] = None,
) -> List[Event]:
    """Search and filter events by various fields."""
    results = []
    for event in storage.events.values():
        if title and title.lower() not in event.title.lower():
            continue
        if location and location.lower() not in event.location.lower():
            continue
        desc = str(event.description or "")
        search_blob = event.title.lower() + desc.lower() + event.location.lower()
        if keyword and (keyword.lower() not in search_blob):
            continue
        if date_from and event.date < date_from:
            continue
        if date_to and event.date > date_to:
            continue
        results.append(event)
    return results


# --- Attendees ---


# PUBLIC_INTERFACE
def add_attendee(event_id: int, obj: AttendeeCreate) -> Optional[Attendee]:
    """Add an attendee to an event."""
    with storage.lock:
        event = storage.events.get(event_id)
        if not event:
            return None
        attendee_id = storage.attendee_id_seq
        storage.attendee_id_seq += 1
        attendee = Attendee(id=attendee_id, rsvp=None, **obj.model_dump())
        event.attendees.append(attendee)
        storage.attendees[attendee_id] = attendee
        return attendee


# PUBLIC_INTERFACE
def remove_attendee(event_id: int, attendee_id: int) -> bool:
    """Remove an attendee from event."""
    with storage.lock:
        event = storage.events.get(event_id)
        if not event:
            return False
        before = len(event.attendees)
        event.attendees = [a for a in event.attendees if a.id != attendee_id]
        if before == len(event.attendees):
            return False
        storage.attendees.pop(attendee_id, None)
        return True


# PUBLIC_INTERFACE
def list_attendees(event_id: int) -> Optional[List[Attendee]]:
    """List all attendees for an event."""
    event = storage.events.get(event_id)
    if event:
        return event.attendees
    return None


# PUBLIC_INTERFACE
def set_rsvp(event_id: int, attendee_id: int, rsvp: bool) -> bool:
    """Set RSVP for an attendee."""
    with storage.lock:
        event = storage.events.get(event_id)
        if not event:
            return False
        for attendee in event.attendees:
            if attendee.id == attendee_id:
                attendee.rsvp = rsvp
                return True
        return False


# --- Notifications ---


# PUBLIC_INTERFACE
def send_event_notification(event_id: int, message: str) -> bool:
    """Stub: This would send a notification to all event attendees. Here, we just simulate."""
    return event_id in storage.events


# PUBLIC_INTERFACE
def send_attendee_notification(event_id: int, attendee_id: int, message: str) -> bool:
    """Stub: Simulate sending notification to one attendee."""
    event = storage.events.get(event_id)
    if not event:
        return False
    for attendee in event.attendees:
        if attendee.id == attendee_id:
            return True
    return False
