# resources-service

Definición de recursos reservables (salas, equipos, puestos), sus características y sus
**horarios de disponibilidad** operativa. Dueño de las tablas `res_*`. Puerto: `8002`.

Estado: estructura Clean Architecture con la entidad `Resource` y el puerto
`ResourceRepository`. El contrato que consume bookings-service está en
[docs/contracts/rest.md](../docs/contracts/rest.md#resources-service-8002--contrato-definido).

No guarda reservas: saber qué horario está *ocupado* es responsabilidad de bookings-service.
