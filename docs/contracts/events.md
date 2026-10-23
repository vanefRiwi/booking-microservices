# Contratos de eventos (RabbitMQ)

Comunicación asíncrona para lo que no necesita respuesta inmediata. Cada productor publica en
su propio *topic exchange*; la *routing key* es el `event_type`.

| Exchange | Productor | Routing keys |
|---|---|---|
| `booking.events` | bookings-service | `booking.created`, `booking.confirmed`, `booking.cancelled` |
| `payment.events` | payments-service | `payment.succeeded`, `payment.failed` |

| Cola | Consumidor | Se enlaza a |
|---|---|---|
| `payments.booking-created` | payments-service | `booking.events` / `booking.created` |
| `bookings.payment-results` | bookings-service | `payment.events` / `payment.*` |
| `notifications.booking-changes` | notifications-service | `booking.events` / `booking.confirmed`, `booking.cancelled` |

## Sobre común

```json
{
  "event_id": "5fa2ea87-1279-40f3-82bb-f3b891eaa398",
  "event_type": "booking.created",
  "event_version": 1,
  "occurred_at": "2026-10-23T12:45:02.330023+00:00",
  "producer": "bookings-service",
  "data": { }
}
```

Reglas:

- **Entrega al menos una vez.** RabbitMQ no garantiza exactamente una entrega; los consumidores
  deben ser idempotentes usando `event_id` (p. ej. notifications guarda `source_event_id`).
- **Versionado.** Cambios compatibles (agregar campos) mantienen `event_version`; cambios
  incompatibles publican `event_version: 2` en paralelo hasta migrar a los consumidores.
- **Eventos con datos suficientes.** Llevan lo que el consumidor necesita para no tener que
  consultar al productor (*event-carried state transfer*) — por ejemplo `total_amount`.

## bookings-service

Implementado en `booking-service/app/src/domain/events.py` y serializado en
`booking-service/app/src/infrastructure/messaging/event_publishers.py`.

### `booking.created`

```json
{
  "booking_id": "5be9c92d-ac3e-4ac3-83fc-31bae5901fb1",
  "user_id": "a1a9b994-1e5c-4f9c-b8e4-3af8a8f7d622",
  "resource_id": "11111111-1111-1111-1111-111111111111",
  "start_at": "2026-11-03T09:00:00-05:00",
  "end_at": "2026-11-03T11:00:00-05:00",
  "total_amount": "80000.00"
}
```

Lo consume payments-service para saber cuánto cobrar.

### `booking.confirmed`

Mismos campos sin `total_amount`. Lo consume notifications-service ("Tu reserva está confirmada").

### `booking.cancelled`

Mismos campos más `"reason": "La reunión se movió" | null`. Lo consume notifications-service.

## payments-service

### `payment.succeeded`

```json
{
  "payment_id": "0b7c2c7e-8b8f-4f1f-9b0e-2d7c6a1f5e3a",
  "booking_id": "5be9c92d-ac3e-4ac3-83fc-31bae5901fb1",
  "amount": "80000.00"
}
```

bookings-service lo consume y ejecuta `ConfirmBooking`.

### `payment.failed`

```json
{
  "payment_id": "0b7c2c7e-8b8f-4f1f-9b0e-2d7c6a1f5e3a",
  "booking_id": "5be9c92d-ac3e-4ac3-83fc-31bae5901fb1",
  "reason": "Fondos insuficientes (simulado)"
}
```

bookings-service lo consume y cancela la reserva para liberar el horario.
