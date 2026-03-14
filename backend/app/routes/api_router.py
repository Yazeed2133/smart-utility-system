from fastapi import APIRouter, Depends

from app.dependencies_auth import get_current_user
from app.routes import accounts
from app.routes import auth
from app.routes import bills
from app.routes import dashboard
from app.routes import info
from app.routes import meters
from app.routes import payments
from app.routes import readings
from app.routes import users

api_router = APIRouter(prefix="/api/v1")

# Public routes
api_router.include_router(info.router, tags=["Info"])
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])

# Protected routes
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"],
    dependencies=[Depends(get_current_user)],
)

api_router.include_router(
    accounts.router,
    prefix="/accounts",
    tags=["Accounts"],
    dependencies=[Depends(get_current_user)],
)

api_router.include_router(
    meters.router,
    prefix="/meters",
    tags=["Meters"],
    dependencies=[Depends(get_current_user)],
)

api_router.include_router(
    readings.router,
    prefix="/readings",
    tags=["Readings"],
    dependencies=[Depends(get_current_user)],
)

api_router.include_router(
    bills.router,
    prefix="/bills",
    tags=["Bills"],
    dependencies=[Depends(get_current_user)],
)

api_router.include_router(
    payments.router,
    prefix="/payments",
    tags=["Payments"],
    dependencies=[Depends(get_current_user)],
)

api_router.include_router(
    dashboard.router,
    prefix="/dashboard",
    tags=["Dashboard"],
    dependencies=[Depends(get_current_user)],
)