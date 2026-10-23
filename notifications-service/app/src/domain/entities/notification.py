"""Entidad Notification en Python puro. Se crea al consumir eventos de reservas
(booking.confirmed, booking.cancelled); no consulta la base de otros servicios."""

import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class Channel(StrEnum):
    EMAIL = "EMAIL"


class NotificationStatus(StrEnum):
    PENDING = "PENDING"
    SENT = "SENT"
    FAILED = "FAILED"


@dataclass
class Notification:
    id: uuid.UUID
    user_id: uuid.UUID
    channel: Channel
    template: str  # p. ej. "booking_confirmed"
    source_event_id: uuid.UUID  # para no notificar dos veces el mismo evento
    status: NotificationStatus
    created_at: datetime

    def mark_sent(self) -> None:
        self.status = NotificationStatus.SENT

    def mark_failed(self) -> None:
        self.status = NotificationStatus.FAILED
