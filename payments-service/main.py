from fastapi import FastAPI

app = FastAPI(
    title="payments-service",
    description="Pagos simulados de reservas e integridad de las transacciones.",
    version="0.1.0",
)


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": "payments-service"}
