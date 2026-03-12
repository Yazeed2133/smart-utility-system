from fastapi import APIRouter

from app.config import settings

router = APIRouter(
    prefix="/info",
    tags=["Info"]
)


@router.get("/")
def get_info():
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database_url": settings.DATABASE_URL
    }