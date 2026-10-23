# payments-service

Pagos **simulados** de reservas e integridad de las transacciones (un pago se resuelve una sola
vez; `Idempotency-Key` evita cobros duplicados). Dueño de las tablas `pay_*`. Puerto: `8004`.

Estado: estructura Clean Architecture con la entidad `Payment` y los puertos `PaymentRepository`,
`PaymentGateway` (simulador) y `EventPublisher`. Consume `booking.created` y publica
`payment.succeeded` / `payment.failed` ([contratos](../docs/contracts/events.md)).
