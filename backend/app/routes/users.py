from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.dependencies import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.schemas.common import MessageResponse, PaginatedResponse
from app.utils import get_object_or_404

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")

    new_user = User(
        name=user.name,
        email=user.email
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/", response_model=PaginatedResponse[UserResponse])
def get_users(
    search: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(User)

    if search:
        query = query.filter(
            or_(
                User.name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%")
            )
        )

    total = query.count()
    items = query.order_by(User.id.desc()).offset(skip).limit(limit).all()

    return {
        "total": total,
        "items": items
    }


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    user = get_object_or_404(user, "User not found")
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    user = get_object_or_404(user, "User not found")

    existing_user = db.query(User).filter(
        User.email == user_data.email,
        User.id != user_id
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")

    user.name = user_data.name
    user.email = user_data.email

    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", response_model=MessageResponse)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    user = get_object_or_404(user, "User not found")

    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}