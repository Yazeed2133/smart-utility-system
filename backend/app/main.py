from fastapi import FastAPI

from app.config import settings
from app.database import Base, engine
from app.routes.api_router import api_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    contact={
        "name": settings.CONTACT_NAME,
        "email": settings.CONTACT_EMAIL,
    },
)

app.include_router(api_router)


@app.get("/", tags=["Root"])
def root():
    return {"message": f"{settings.APP_NAME} is running"}


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}