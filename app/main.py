from fastapi import FastAPI
from app.api.routes import router
from app.api.auth import router as auth_router
from app.db import Base, engine
from app.api.rate_limit import RateLimitMiddleware

app = FastAPI()
app.include_router(router)
app.include_router(auth_router)
app.add_middleware(RateLimitMiddleware)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

