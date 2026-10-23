from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class CreateBookingCommand:
    user_id: UUID
    resource_id: UUID
    start_at: datetime
    end_at: datetime


@dataclass(frozen=True)
class CancelBookingCommand:
    booking_id: UUID
    reason: str | None = None
