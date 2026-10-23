from fastapi import FastAPI

app = FastAPI(
    title="notifications-service",
    description="Notificaciones tras confirmaciones y cambios de reservas.",
    version="0.1.0",
)


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": "notifications-service"}
