from fastapi import APIRouter

from app.routes import users
from app.routes import accounts
from app.routes import meters
from app.routes import readings
from app.routes import bills
from app.routes import payments
from app.routes import info
from app.routes import dashboard

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(users.router)
api_router.include_router(accounts.router)
api_router.include_router(meters.router)
api_router.include_router(readings.router)
api_router.include_router(bills.router)
api_router.include_router(payments.router)
api_router.include_router(info.router)
api_router.include_router(dashboard.router)