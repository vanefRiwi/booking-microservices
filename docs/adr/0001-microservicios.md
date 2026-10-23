# ADR 0001 · Microservicios con comunicación por eventos

**Estado:** aceptada

## Contexto

La plataforma de reservas empieza sencilla (usuarios y reservas) pero ya se sabe que necesitará
pagos, notificaciones, seguridad y procesamiento asíncrono. Las alternativas evaluadas:

| Opción | A favor | En contra |
|---|---|---|
| Monolito | Despliegue simple, menor latencia | Despliegue global, escalado vertical, límites con equipos grandes |
| Monolito modular | Límites lógicos con menos complejidad | Exige disciplina; los límites se erosionan fácil al compartir la base |
| **Microservicios** | Despliegue independiente, propiedad de datos | Latencia de red, observabilidad distribuida, complejidad operativa |
| Event-driven puro | Desacoplamiento, escalado por consumidor | Consistencia eventual en todo, flujos difíciles de seguir |

## Decisión

Cinco microservicios alineados con capacidades del negocio (usuarios, recursos, reservas, pagos,
notificaciones), REST entre ellos cuando se necesita respuesta inmediata y eventos cuando no.

- Pagos es la parte más propensa a fallar y la que más cambiará (simulado → pasarela real).
  Aislarlo evita que una caída de pagos impida consultar o crear reservas.
- Notificaciones es naturalmente asíncrono: el usuario no debe esperar a que salga un email.
- Reservas concentra la regla crítica (conflictos) y es la que más carga recibe en horas pico;
  conviene escalarla de forma independiente.

## Consecuencias

- Cada servicio es dueño de sus datos; se integran solo por contratos explícitos.
- Una reserva `PENDING` bloquea el horario mientras se paga (consistencia eventual entre
  bookings y payments). Habrá que expirar reservas no pagadas (sesión 7).
- Se acepta el costo operativo como parte del aprendizaje del curso: límites de servicio,
  fallos distribuidos y despliegue independiente.
