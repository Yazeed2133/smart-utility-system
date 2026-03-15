from fastapi import APIRouter

from app.config import settings

router = APIRouter()


@router.get("/")
def get_info():
    return {
        "app_name": settings.app_name,
        "version": settings.app_version,
        "description": settings.app_description,
        "contact": {
            "name": settings.contact_name,
            "email": str(settings.contact_email),
        },
    }