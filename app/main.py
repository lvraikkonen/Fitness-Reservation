from fastapi import FastAPI
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import user, auth, venue, reservation
from app.scripts.init_db import init_db, create_sample_data, recreate_db
from app.core.config import settings
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan_context(app: FastAPI):
    # 在应用启动时同步初始化数据库
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, recreate_db)
    await loop.run_in_executor(None, create_sample_data)
    yield
    # 在应用关闭时执行清理操作（如果需要）

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    lifespan=lifespan_context,
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 可以根据需要设置允许的源 # allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含路由
# app.include_router(user.router, prefix="/api/v1/users", tags=["users"])
# app.include_router(venue.router, prefix="/api/v1/venues", tags=["venues"])
# app.include_router(reservation.router, prefix="/api/v1/reservations", tags=["reservations"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])


@app.get("/")
def read_root():
    return {"message": "Welcome to the API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
