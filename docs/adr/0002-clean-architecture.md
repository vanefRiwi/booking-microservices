# ADR 0002 · Clean Architecture dentro de cada servicio

**Estado:** aceptada

## Contexto

Se compararon Layered, Hexagonal, Vertical Slice y Clean. Comparten principios; el curso usa
Clean Architecture como patrón único de referencia.

## Decisión

Cada servicio tiene `domain/`, `application/`, `infrastructure/` y `presentation/` bajo `app/src`.

- **Domain:** entidades e invariantes en Python puro (`Booking`, `TimeSlot`, `User`). No
  depende de FastAPI, SQLModel ni RabbitMQ.
- **Application:** casos de uso (`CreateBooking`, `CancelBooking`, `RegisterUser`...) y los
  puertos que necesitan (`BookingRepository`, `UserDirectory`, `ResourceCatalog`, `EventPublisher`).
- **Infrastructure:** implementaciones concretas (SQLModel, Alembic, httpx, publicadores).
- **Presentation:** routers FastAPI que solo traducen HTTP ↔ DTO ↔ caso de uso, y un
  manejador que traduce excepciones de dominio a códigos HTTP.

## Consecuencias

- El modelo `User` de SQLModel se movió de `domain/models` a `infrastructure/persistence`.
  La tabla `usr_users` no cambió (verificado con `alembic check`).
- La regla anti-conflictos se prueba sin base de datos con fakes de los puertos.
- Hay un mapeo explícito entidad ↔ modelo ORM en cada repositorio: más código, a cambio de que
  cambiar de ORM o de base no toque el dominio.
