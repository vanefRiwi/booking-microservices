# bookings-service

Reglas de reserva, **detección de conflictos de disponibilidad** y estados de las reservas.
Dueño de la tabla `bkg_bookings`. Puerto por defecto: `8003`.

```text
app/src/
├── domain/
│   ├── entities/booking.py        # Booking: invariantes y transiciones de estado
│   ├── value_objects.py           # TimeSlot [inicio, fin) y BookingStatus
│   ├── services/availability.py   # Regla clave: ensure_slot_is_available()
│   ├── events.py                  # booking.created / confirmed / cancelled
│   └── exceptions.py
├── application/
│   ├── ports.py                   # BookingRepository, UserDirectory, ResourceCatalog, EventPublisher
│   ├── dto.py
│   └── use_cases/                 # CreateBooking, ConfirmBooking, CancelBooking, Get/ListBookings
├── infrastructure/
│   ├── persistence/               # BookingModel (SQLModel) + repositorio
│   ├── clients/http_clients.py    # REST hacia users-service y resources-service
│   ├── messaging/                 # Publicador de eventos (log hoy, RabbitMQ después)
│   ├── config.py
│   └── database.py
└── presentation/api/              # Router /api/v1/bookings y traducción de errores a HTTP
```

```bash
cp .env.example .env
uv sync
uv run alembic upgrade head
uv run fastapi dev main.py --port 8003
uv run pytest
```

Contratos: [REST](../docs/contracts/rest.md#bookings-service-8003--implementado) ·
[eventos](../docs/contracts/events.md#bookings-service).
