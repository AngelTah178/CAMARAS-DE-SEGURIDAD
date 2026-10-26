from fastapi import FastAPI

app = FastAPI(
    title="Cámaras de Seguridad - API",
    description="API para inventario de equipos de videovigilancia.",
    version="0.1.0",
)


@app.get("/api/health", tags=["Sistema"])
def health():
    return {"status": "ok", "service": "camaras-de-seguridad"}
