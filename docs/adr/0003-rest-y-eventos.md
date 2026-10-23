# ADR 0003 · REST con FastAPI y eventos con RabbitMQ

**Estado:** aceptada

## Contexto

REST, RPC, GraphQL y gRPC son estilos de interfaz, no arquitecturas completas.

| Estilo | Uso adecuado |
|---|---|
| **REST (FastAPI)** | APIs públicas, recursos HTTP, caché, fácil de probar |
| RPC | Acciones explícitas ad hoc |
| GraphQL | Consultas flexibles; complica caché y permisos |
| gRPC | Contratos fuertes y alto rendimiento interno |

## Decisión

- **REST** para la API pública y para las consultas internas que necesitan respuesta inmediata:
  bookings → users (`¿existe y está activo?`) y bookings → resources (`¿existe, está activo y
  cuánto cuesta?`). Las acciones de estado se modelan como subrecursos (`/bookings/{id}/cancel`).
- **RabbitMQ** para lo que puede pasar después: `booking.created` → pagos,
  `payment.succeeded` → confirmar reserva, `booking.confirmed` → notificar.

## Consecuencias

- Las llamadas REST crean acoplamiento temporal: si users-service cae, no se pueden crear
  reservas (`503`). Se mitigará con timeouts (ya configurables), reintentos y circuit breaker.
- Los eventos se entregan al menos una vez: los consumidores deben ser idempotentes (`event_id`).
- gRPC queda como opción futura si la comunicación interna lo exige.
