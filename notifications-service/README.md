# notifications-service

Envía notificaciones (email) cuando una reserva se confirma o cambia. Dueño de las tablas
`ntf_*`. Puerto: `8005`. No expone API pública: reacciona a eventos.

Estado: estructura Clean Architecture con la entidad `Notification` y los puertos
`NotificationRepository`, `RecipientDirectory` (REST a users-service) y `NotificationSender`.
Consume `booking.confirmed` y `booking.cancelled`, deduplicando por `event_id`
([contratos](../docs/contracts/events.md)).
