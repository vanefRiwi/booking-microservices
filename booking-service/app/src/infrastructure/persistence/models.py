"""Modelo ORM propio de bookings-service. Nunca se comparte con otros servicios:
user_id y resource_id son solo identificadores, sin llaves foráneas hacia otras bases."""

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, Column, DateTime
from sqlmodel import Field, SQLModel

NO_OVERLAP_CONSTRAINT = "bkg_bookings_no_overlap"


class BookingModel(SQLModel, table=True):
    __tablename__ = "bkg_bookings"
    __table_args__ = (CheckConstraint("end_at > start_at", name="bkg_bookings_valid_slot"),)

    id: uuid.UUID = Field(primary_key=True)
    user_id: uuid.UUID = Field(index=True)
    resource_id: uuid.UUID = Field(index=True)
    start_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    end_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    status: str = Field(max_length=20, index=True)
    total_amount: Decimal = Field(max_digits=12, decimal_places=2)
    cancellation_reason: str | None = Field(default=None, max_length=500)
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    updated_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
