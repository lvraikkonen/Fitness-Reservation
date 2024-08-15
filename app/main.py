from fastapi import FastAPI
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import user, sport_venue, venue, facility, venue_available_time_slots
from app.api.v1.feedback import feedback
from app.api.v1.stats import stats
from app.api.v1.endpoints import reservation
from app.scripts.init_db import init_db, create_sample_data, recreate_db
from app.core.config import settings, get_logger
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles


@asynccontextmanager
async def lifespan_context(app: FastAPI):
    # 在应用启动时同步初始化数据库
    loop = asyncio.get_event_loop()
    # await loop.run_in_executor(None, recreate_db)
    # await loop.run_in_executor(None, create_sample_data)
    yield
    # 在应用关闭时执行清理操作（如果需要）

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    lifespan=lifespan_context,
)

logger = get_logger(__name__)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 可以根据需要设置允许的源 # allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含路由
app.include_router(user.router, prefix="/api/v1/users", tags=["users"])
app.include_router(sport_venue.router, prefix="/api/v1/sport_venues", tags=["sport_venues"])
app.include_router(venue.router, prefix="/api/v1/venues", tags=["venues"])
app.include_router(venue_available_time_slots.router, prefix="/api/v1/venues", tags=["venues"])
app.include_router(facility.router, prefix="/api/v1/facilities", tags=["facilities"])
app.include_router(feedback.router, prefix="/feedback", tags=["feedback"])
app.include_router(reservation.router, prefix="/api/v1/reservations", tags=["reservations"])
app.include_router(stats.router, prefix="/stats", tags=["statistics"])

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/")
def read_root():
    logger.info("Hello World endpoint")
    return {"message": "Welcome to the API"}


if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting application with log level: {settings.LOG_LEVEL}")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
