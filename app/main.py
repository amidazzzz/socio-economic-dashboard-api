from fastapi import FastAPI
from app.api.router import region, indicator, value, analytics


app = FastAPI(title="Socio-Economic Platform API")


@app.get("/health")
async def health():
    return {"status": "ok"}


app.include_router(region.router, prefix="/api")
app.include_router(indicator.router, prefix="/api")
app.include_router(value.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")