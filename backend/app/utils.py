from fastapi import HTTPException, status
from sqlalchemy.inspection import inspect


def get_object_or_404(db, model, object_id: int):
    obj = db.query(model).filter(model.id == object_id).first()
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{model.__name__} not found",
        )
    return obj


def get_payment_amount_column(payment_model):
    mapper = inspect(payment_model)
    if "amount" in mapper.columns:
        return payment_model.amount
    if "payment_amount" in mapper.columns:
        return payment_model.payment_amount

    raise AttributeError("Payment model must have either 'amount' or 'payment_amount' column")


def is_admin(user) -> bool:
    return getattr(user, "role", None) == "admin"


def is_account_owner(user, account) -> bool:
    return getattr(account, "user_id", None) == getattr(user, "id", None)


def ensure_admin_or_account_owner(user, account):
    if not is_admin(user) and not is_account_owner(user, account):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to access this resource",
        )