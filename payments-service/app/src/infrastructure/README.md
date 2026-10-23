# Infrastructure

Aquí van las implementaciones concretas de los puertos de `application/ports.py`:
modelos SQLModel (tablas con prefijo `pay_`), repositorios, clientes HTTP y
adaptadores de RabbitMQ. Alembic usará la tabla de versiones `alembic_version_payments`.
