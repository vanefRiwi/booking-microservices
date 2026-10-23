from fastapi import FastAPI

app = FastAPI(
    title="resources-service",
    description="Definición de recursos (salas, equipos), características y horarios de disponibilidad.",
    version="0.1.0",
)


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": "resources-service"}
