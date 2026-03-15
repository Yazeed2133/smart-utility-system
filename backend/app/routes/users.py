from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, func, or_
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.dependencies_auth import require_admin
from app.models.user import User
from app.schemas import MessageResponse, PaginatedResponse
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.security import hash_password
from app.utils import get_object_or_404

router = APIRouter()


@router.get("/summary", dependencies=[Depends(require_admin)])
def get_users_summary(db: Session = Depends(get_db)):
    total_users = db.query(func.count(User.id)).scalar() or 0
    total_admins = db.query(func.count(User.id)).filter(User.role == "admin").scalar() or 0
    total_normal_users = db.query(func.count(User.id)).filter(User.role == "user").scalar() or 0

    return {
        "total_users": total_users,
        "total_admins": total_admins,
        "total_normal_users": total_normal_users,
    }


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    new_user = User(
        name=user_in.name,
        email=user_in.email,
        password_hash=hash_password(user_in.password),
        role="user",
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get(
    "/",
    response_model=PaginatedResponse[UserResponse],
    dependencies=[Depends(require_admin)],
)
def list_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = Query(10, le=100),
    search: str | None = None,
):
    query = db.query(User)

    if search:
        query = query.filter(
            or_(
                User.name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                User.role.ilike(f"%{search}%"),
            )
        )

    total = query.with_entities(func.count(User.id)).scalar() or 0
    items = query.order_by(desc(User.created_at)).offset(skip).limit(limit).all()

    return PaginatedResponse[UserResponse](
        total=total,
        skip=skip,
        limit=limit,
        items=items,
    )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    dependencies=[Depends(require_admin)],
)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = get_object_or_404(db, User, user_id)
    return user


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    dependencies=[Depends(require_admin)],
)
def update_user(user_id: int, user_in: UserUpdate, db: Session = Depends(get_db)):
    user = get_object_or_404(db, User, user_id)

    if user_in.email and user_in.email != user.email:
        existing_user = db.query(User).filter(User.email == user_in.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

    if user_in.name is not None:
        user.name = user_in.name

    if user_in.email is not None:
        user.email = user_in.email

    if user_in.password is not None:
        user.password_hash = hash_password(user_in.password)

    if user_in.role is not None:
        if user_in.role not in ["admin", "user"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role must be admin or user",
            )
        user.role = user_in.role

    db.commit()
    db.refresh(user)
    return user


@router.delete(
    "/{user_id}",
    response_model=MessageResponse,
    dependencies=[Depends(require_admin)],
)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = get_object_or_404(db, User, user_id)
    db.delete(user)
    db.commit()
    return MessageResponse(message="User deleted successfully")