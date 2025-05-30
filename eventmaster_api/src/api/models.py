# Models for EventMaster API
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


# PUBLIC_INTERFACE
class AttendeeBase(BaseModel):
    """Base model for an attendee."""
    name: str = Field(..., example="Jane Doe")
    email: str = Field(..., example="jane@example.com")

# PUBLIC_INTERFACE
class AttendeeCreate(AttendeeBase):
    """Model to create a new attendee."""
    pass

# PUBLIC_INTERFACE
class Attendee(AttendeeBase):
    """Attendee model with RSVP status."""
    id: int
    rsvp: Optional[bool] = None

    class Config:
        orm_mode = True

# PUBLIC_INTERFACE
class EventBase(BaseModel):
    """Base model for an event."""
    title: str = Field(..., example="Annual Meeting")
    description: Optional[str] = Field(None, example="Company-wide annual meeting")
    location: str = Field(..., example="Conference Room A")
    date: datetime = Field(..., example="2024-07-16T09:00:00")

# PUBLIC_INTERFACE
class EventCreate(EventBase):
    """Model to create a new event."""
    pass

# PUBLIC_INTERFACE
class EventUpdate(BaseModel):
    """Model to update an event. All fields optional."""
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    date: Optional[datetime] = None

# PUBLIC_INTERFACE
class Event(EventBase):
    """Event model with ID and attendees."""
    id: int
    attendees: List[Attendee] = []

    class Config:
        orm_mode = True

# PUBLIC_INTERFACE
class NotificationRequest(BaseModel):
    """Model to trigger notifications for an event or attendees."""
    event_id: int
    message: str

# PUBLIC_INTERFACE
class EventSearchFilter(BaseModel):
    """Model for event search and filtering."""
    title: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    location: Optional[str] = None
    keyword: Optional[str] = None
