from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.dependencies_auth import get_current_user
from app.models.account import Account
from app.models.bill import Bill
from app.models.meter import Meter
from app.models.payment import Payment
from app.models.reading import Reading
from app.models.user import User
from app.schemas.dashboard import DashboardStatsResponse
from app.utils import get_payment_amount_column

router = APIRouter()


def _accounts_query(db: Session, current_user: User):
    query = db.query(Account)
    if current_user.role != "admin":
        query = query.filter(Account.user_id == current_user.id)
    return query


def _meters_query(db: Session, current_user: User):
    query = db.query(Meter).join(Account, Meter.account_id == Account.id)
    if current_user.role != "admin":
        query = query.filter(Account.user_id == current_user.id)
    return query


def _readings_query(db: Session, current_user: User):
    query = (
        db.query(Reading)
        .join(Meter, Reading.meter_id == Meter.id)
        .join(Account, Meter.account_id == Account.id)
    )
    if current_user.role != "admin":
        query = query.filter(Account.user_id == current_user.id)
    return query


def _bills_query(db: Session, current_user: User):
    query = db.query(Bill).join(Account, Bill.account_id == Account.id)
    if current_user.role != "admin":
        query = query.filter(Account.user_id == current_user.id)
    return query


def _payments_query(db: Session, current_user: User):
    query = (
        db.query(Payment)
        .join(Bill, Payment.bill_id == Bill.id)
        .join(Account, Bill.account_id == Account.id)
    )
    if current_user.role != "admin":
        query = query.filter(Account.user_id == current_user.id)
    return query


def _users_query_for_owned_data(db: Session, current_user: User):
    if current_user.role == "admin":
        return db.query(User)
    return db.query(User).filter(User.id == current_user.id)


def _apply_account_filters(
    query,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    account_type: Optional[str] = None,
):
    if date_from:
        query = query.filter(func.date(Account.created_at) >= date_from)
    if date_to:
        query = query.filter(func.date(Account.created_at) <= date_to)
    if account_type:
        query = query.filter(Account.account_type == account_type)
    return query


def _apply_meter_filters(
    query,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    account_type: Optional[str] = None,
    meter_type: Optional[str] = None,
):
    if date_from:
        query = query.filter(func.date(Meter.created_at) >= date_from)
    if date_to:
        query = query.filter(func.date(Meter.created_at) <= date_to)
    if account_type:
        query = query.filter(Account.account_type == account_type)
    if meter_type:
        query = query.filter(Meter.meter_type == meter_type)
    return query


def _apply_reading_filters(
    query,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    account_type: Optional[str] = None,
    meter_type: Optional[str] = None,
):
    if date_from:
        query = query.filter(Reading.reading_date >= date_from)
    if date_to:
        query = query.filter(Reading.reading_date <= date_to)
    if account_type:
        query = query.filter(Account.account_type == account_type)
    if meter_type:
        query = query.filter(Meter.meter_type == meter_type)
    return query


def _apply_bill_filters(
    query,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    account_type: Optional[str] = None,
    bill_status: Optional[str] = None,
):
    if date_from:
        query = query.filter(Bill.due_date >= date_from)
    if date_to:
        query = query.filter(Bill.due_date <= date_to)
    if account_type:
        query = query.filter(Account.account_type == account_type)
    if bill_status:
        query = query.filter(Bill.status == bill_status)
    return query


def _apply_payment_filters(
    query,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    account_type: Optional[str] = None,
    payment_method: Optional[str] = None,
):
    if date_from:
        query = query.filter(Payment.payment_date >= date_from)
    if date_to:
        query = query.filter(Payment.payment_date <= date_to)
    if account_type:
        query = query.filter(Account.account_type == account_type)
    if payment_method:
        query = query.filter(Payment.payment_method == payment_method)
    return query


def _period_expr(group_by: str, column):
    if group_by == "year":
        return func.strftime("%Y", column)
    return func.strftime("%Y-%m", column)


@router.get("/stats", response_model=DashboardStatsResponse)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
):
    users_query = _users_query_for_owned_data(db, current_user)
    accounts_query = _apply_account_filters(_accounts_query(db, current_user), date_from, date_to)
    meters_query = _apply_meter_filters(_meters_query(db, current_user), date_from, date_to)
    readings_query = _apply_reading_filters(_readings_query(db, current_user), date_from, date_to)
    bills_query = _apply_bill_filters(_bills_query(db, current_user), date_from, date_to)
    payments_query = _apply_payment_filters(_payments_query(db, current_user), date_from, date_to)

    payment_amount_col = get_payment_amount_column(Payment)

    total_billed_amount = bills_query.with_entities(
        func.coalesce(func.sum(Bill.amount), 0.0)
    ).scalar() or 0.0
    total_paid_amount = payments_query.with_entities(
        func.coalesce(func.sum(payment_amount_col), 0.0)
    ).scalar() or 0.0
    unpaid_total_amount = max(float(total_billed_amount) - float(total_paid_amount), 0.0)

    total_bills = bills_query.count()
    paid_bills = bills_query.filter(Bill.status == "paid").count()
    pending_bills = bills_query.filter(Bill.status == "pending").count()
    overdue_bills = bills_query.filter(Bill.status == "overdue").count()

    fully_paid_percentage = (paid_bills / total_bills * 100) if total_bills else 0.0
    collection_rate = (float(total_paid_amount) / float(total_billed_amount) * 100) if total_billed_amount else 0.0

    average_bill_amount = bills_query.with_entities(func.avg(Bill.amount)).scalar() or 0.0
    average_payment_amount = payments_query.with_entities(func.avg(payment_amount_col)).scalar() or 0.0

    return DashboardStatsResponse(
        total_users=users_query.count(),
        total_accounts=accounts_query.count(),
        total_meters=meters_query.count(),
        total_readings=readings_query.count(),
        total_bills=total_bills,
        total_payments=payments_query.count(),
        overdue_bills_count=overdue_bills,
        pending_bills_count=pending_bills,
        paid_bills_count=paid_bills,
        unpaid_total_amount=float(unpaid_total_amount),
        fully_paid_percentage=float(fully_paid_percentage),
        collection_rate=float(collection_rate),
        average_bill_amount=float(average_bill_amount),
        average_payment_amount=float(average_payment_amount),
    )


@router.get("/recent")
def get_recent_dashboard_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(5, ge=1, le=100),
):
    recent_users = (
        _users_query_for_owned_data(db, current_user)
        .order_by(desc(User.created_at))
        .limit(limit)
        .all()
    )

    recent_accounts = (
        _accounts_query(db, current_user)
        .order_by(desc(Account.created_at))
        .limit(limit)
        .all()
    )

    recent_meters = (
        _meters_query(db, current_user)
        .order_by(desc(Meter.created_at))
        .limit(limit)
        .all()
    )

    recent_readings = (
        _readings_query(db, current_user)
        .order_by(desc(Reading.created_at))
        .limit(limit)
        .all()
    )

    recent_bills = (
        _bills_query(db, current_user)
        .order_by(desc(Bill.created_at))
        .limit(limit)
        .all()
    )

    recent_payments = (
        _payments_query(db, current_user)
        .order_by(desc(Payment.created_at))
        .limit(limit)
        .all()
    )

    return {
        "recent_users": [
            {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "created_at": user.created_at,
            }
            for user in recent_users
        ],
        "recent_accounts": [
            {
                "id": account.id,
                "user_id": account.user_id,
                "account_number": account.account_number,
                "account_type": account.account_type,
                "address": account.address,
                "created_at": account.created_at,
            }
            for account in recent_accounts
        ],
        "recent_meters": [
            {
                "id": meter.id,
                "account_id": meter.account_id,
                "meter_number": meter.meter_number,
                "meter_type": meter.meter_type,
                "created_at": meter.created_at,
            }
            for meter in recent_meters
        ],
        "recent_readings": [
            {
                "id": reading.id,
                "meter_id": reading.meter_id,
                "reading_value": reading.reading_value,
                "reading_date": reading.reading_date,
                "created_at": reading.created_at,
            }
            for reading in recent_readings
        ],
        "recent_bills": [
            {
                "id": bill.id,
                "account_id": bill.account_id,
                "amount": bill.amount,
                "due_date": bill.due_date,
                "status": bill.status,
                "created_at": bill.created_at,
            }
            for bill in recent_bills
        ],
        "recent_payments": [
            {
                "id": payment.id,
                "bill_id": payment.bill_id,
                "amount": getattr(payment, "amount", getattr(payment, "payment_amount", 0)),
                "payment_method": payment.payment_method,
                "payment_date": payment.payment_date,
                "created_at": payment.created_at,
            }
            for payment in recent_payments
        ],
    }


@router.get("/trends")
def get_dashboard_trends(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    group_by: str = Query("month", pattern="^(month|year)$"),
    limit: int = Query(12, ge=1, le=60),
):
    account_period = _period_expr(group_by, Account.created_at)
    meter_period = _period_expr(group_by, Meter.created_at)
    bill_period = _period_expr(group_by, Bill.created_at)
    payment_period = _period_expr(group_by, Payment.payment_date)

    accounts = (
        _accounts_query(db, current_user)
        .with_entities(account_period.label("period"), func.count(Account.id).label("count"))
        .group_by("period")
        .order_by(desc("period"))
        .limit(limit)
        .all()
    )

    meters = (
        _meters_query(db, current_user)
        .with_entities(meter_period.label("period"), func.count(Meter.id).label("count"))
        .group_by("period")
        .order_by(desc("period"))
        .limit(limit)
        .all()
    )

    bills = (
        _bills_query(db, current_user)
        .with_entities(
            bill_period.label("period"),
            func.count(Bill.id).label("count"),
            func.coalesce(func.sum(Bill.amount), 0.0).label("amount"),
        )
        .group_by("period")
        .order_by(desc("period"))
        .limit(limit)
        .all()
    )

    payment_amount_col = get_payment_amount_column(Payment)
    payments = (
        _payments_query(db, current_user)
        .with_entities(
            payment_period.label("period"),
            func.count(Payment.id).label("count"),
            func.coalesce(func.sum(payment_amount_col), 0.0).label("amount"),
        )
        .group_by("period")
        .order_by(desc("period"))
        .limit(limit)
        .all()
    )

    return {
        "accounts": [{"period": row.period, "count": row.count} for row in accounts],
        "meters": [{"period": row.period, "count": row.count} for row in meters],
        "bills": [{"period": row.period, "count": row.count, "amount": float(row.amount or 0)} for row in bills],
        "payments": [{"period": row.period, "count": row.count, "amount": float(row.amount or 0)} for row in payments],
    }


@router.get("/yearly-trends")
def get_dashboard_yearly_trends(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(5, ge=1, le=20),
):
    bill_period = func.strftime("%Y", Bill.due_date)
    payment_period = func.strftime("%Y", Payment.payment_date)
    payment_amount_col = get_payment_amount_column(Payment)

    yearly_bills = (
        _bills_query(db, current_user)
        .with_entities(
            bill_period.label("year"),
            func.count(Bill.id).label("count"),
            func.coalesce(func.sum(Bill.amount), 0.0).label("amount"),
        )
        .group_by("year")
        .order_by(desc("year"))
        .limit(limit)
        .all()
    )

    yearly_payments = (
        _payments_query(db, current_user)
        .with_entities(
            payment_period.label("year"),
            func.count(Payment.id).label("count"),
            func.coalesce(func.sum(payment_amount_col), 0.0).label("amount"),
        )
        .group_by("year")
        .order_by(desc("year"))
        .limit(limit)
        .all()
    )

    return {
        "yearly_bills": [
            {"year": row.year, "count": row.count, "amount": float(row.amount or 0)}
            for row in yearly_bills
        ],
        "yearly_payments": [
            {"year": row.year, "count": row.count, "amount": float(row.amount or 0)}
            for row in yearly_payments
        ],
    }


@router.get("/bill-status-trends")
def get_bill_status_trends(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = (
        _bills_query(db, current_user)
        .with_entities(
            Bill.status.label("status"),
            func.count(Bill.id).label("count"),
            func.coalesce(func.sum(Bill.amount), 0.0).label("amount"),
        )
        .group_by(Bill.status)
        .order_by(Bill.status)
        .all()
    )

    return [
        {
            "status": row.status,
            "count": row.count,
            "amount": float(row.amount or 0),
        }
        for row in rows
    ]


@router.get("/payment-method-trends")
def get_payment_method_trends(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    payment_amount_col = get_payment_amount_column(Payment)

    rows = (
        _payments_query(db, current_user)
        .with_entities(
            Payment.payment_method.label("payment_method"),
            func.count(Payment.id).label("count"),
            func.coalesce(func.sum(payment_amount_col), 0.0).label("amount"),
        )
        .group_by(Payment.payment_method)
        .order_by(Payment.payment_method)
        .all()
    )

    return [
        {
            "payment_method": row.payment_method,
            "count": row.count,
            "amount": float(row.amount or 0),
        }
        for row in rows
    ]


@router.get("/top-outstanding-accounts")
def get_top_outstanding_accounts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=100),
):
    payment_amount_col = get_payment_amount_column(Payment)

    rows = (
        _accounts_query(db, current_user)
        .outerjoin(Bill, Bill.account_id == Account.id)
        .outerjoin(Payment, Payment.bill_id == Bill.id)
        .with_entities(
            Account.id.label("account_id"),
            Account.account_number,
            Account.account_type,
            func.coalesce(func.sum(Bill.amount), 0.0).label("billed_amount"),
            func.coalesce(func.sum(payment_amount_col), 0.0).label("paid_amount"),
        )
        .group_by(Account.id, Account.account_number, Account.account_type)
        .all()
    )

    result = []
    for row in rows:
        outstanding_balance = float(row.billed_amount or 0) - float(row.paid_amount or 0)
        result.append(
            {
                "account_id": row.account_id,
                "account_number": row.account_number,
                "account_type": row.account_type,
                "billed_amount": float(row.billed_amount or 0),
                "paid_amount": float(row.paid_amount or 0),
                "outstanding_balance": max(outstanding_balance, 0.0),
            }
        )

    result.sort(key=lambda x: x["outstanding_balance"], reverse=True)
    return result[:limit]


@router.get("/top-users-by-accounts")
def get_top_users_by_accounts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=100),
):
    rows = (
        _users_query_for_owned_data(db, current_user)
        .outerjoin(Account, Account.user_id == User.id)
        .with_entities(
            User.id.label("user_id"),
            User.name,
            User.email,
            func.count(Account.id).label("accounts_count"),
        )
        .group_by(User.id, User.name, User.email)
        .order_by(desc("accounts_count"))
        .limit(limit)
        .all()
    )

    return [
        {
            "user_id": row.user_id,
            "name": row.name,
            "email": row.email,
            "accounts_count": row.accounts_count,
        }
        for row in rows
    ]


@router.get("/top-accounts-by-meters")
def get_top_accounts_by_meters(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=100),
):
    rows = (
        _accounts_query(db, current_user)
        .outerjoin(Meter, Meter.account_id == Account.id)
        .with_entities(
            Account.id.label("account_id"),
            Account.account_number,
            Account.account_type,
            func.count(Meter.id).label("meters_count"),
        )
        .group_by(Account.id, Account.account_number, Account.account_type)
        .order_by(desc("meters_count"))
        .limit(limit)
        .all()
    )

    return [
        {
            "account_id": row.account_id,
            "account_number": row.account_number,
            "account_type": row.account_type,
            "meters_count": row.meters_count,
        }
        for row in rows
    ]


@router.get("/top-meters-by-readings")
def get_top_meters_by_readings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=100),
):
    rows = (
        _meters_query(db, current_user)
        .outerjoin(Reading, Reading.meter_id == Meter.id)
        .with_entities(
            Meter.id.label("meter_id"),
            Meter.meter_number,
            Meter.meter_type,
            func.count(Reading.id).label("readings_count"),
        )
        .group_by(Meter.id, Meter.meter_number, Meter.meter_type)
        .order_by(desc("readings_count"))
        .limit(limit)
        .all()
    )

    return [
        {
            "meter_id": row.meter_id,
            "meter_number": row.meter_number,
            "meter_type": row.meter_type,
            "readings_count": row.readings_count,
        }
        for row in rows
    ]


@router.get("/top-accounts-by-bills")
def get_top_accounts_by_bills(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=100),
):
    rows = (
        _accounts_query(db, current_user)
        .outerjoin(Bill, Bill.account_id == Account.id)
        .with_entities(
            Account.id.label("account_id"),
            Account.account_number,
            func.count(Bill.id).label("bills_count"),
        )
        .group_by(Account.id, Account.account_number)
        .order_by(desc("bills_count"))
        .limit(limit)
        .all()
    )

    return [
        {
            "account_id": row.account_id,
            "account_number": row.account_number,
            "bills_count": row.bills_count,
        }
        for row in rows
    ]


@router.get("/top-users-by-bills")
def get_top_users_by_bills(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=100),
):
    rows = (
        _users_query_for_owned_data(db, current_user)
        .outerjoin(Account, Account.user_id == User.id)
        .outerjoin(Bill, Bill.account_id == Account.id)
        .with_entities(
            User.id.label("user_id"),
            User.name,
            User.email,
            func.count(Bill.id).label("bills_count"),
        )
        .group_by(User.id, User.name, User.email)
        .order_by(desc("bills_count"))
        .limit(limit)
        .all()
    )

    return [
        {
            "user_id": row.user_id,
            "name": row.name,
            "email": row.email,
            "bills_count": row.bills_count,
        }
        for row in rows
    ]


@router.get("/top-accounts-by-payments")
def get_top_accounts_by_payments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=100),
):
    rows = (
        _accounts_query(db, current_user)
        .outerjoin(Bill, Bill.account_id == Account.id)
        .outerjoin(Payment, Payment.bill_id == Bill.id)
        .with_entities(
            Account.id.label("account_id"),
            Account.account_number,
            func.count(Payment.id).label("payments_count"),
        )
        .group_by(Account.id, Account.account_number)
        .order_by(desc("payments_count"))
        .limit(limit)
        .all()
    )

    return [
        {
            "account_id": row.account_id,
            "account_number": row.account_number,
            "payments_count": row.payments_count,
        }
        for row in rows
    ]


@router.get("/top-users-by-payments")
def get_top_users_by_payments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=100),
):
    rows = (
        _users_query_for_owned_data(db, current_user)
        .outerjoin(Account, Account.user_id == User.id)
        .outerjoin(Bill, Bill.account_id == Account.id)
        .outerjoin(Payment, Payment.bill_id == Bill.id)
        .with_entities(
            User.id.label("user_id"),
            User.name,
            User.email,
            func.count(Payment.id).label("payments_count"),
        )
        .group_by(User.id, User.name, User.email)
        .order_by(desc("payments_count"))
        .limit(limit)
        .all()
    )

    return [
        {
            "user_id": row.user_id,
            "name": row.name,
            "email": row.email,
            "payments_count": row.payments_count,
        }
        for row in rows
    ]


@router.get("/top-accounts-by-billed-amount")
def get_top_accounts_by_billed_amount(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=100),
):
    rows = (
        _accounts_query(db, current_user)
        .outerjoin(Bill, Bill.account_id == Account.id)
        .with_entities(
            Account.id.label("account_id"),
            Account.account_number,
            func.coalesce(func.sum(Bill.amount), 0.0).label("billed_amount"),
        )
        .group_by(Account.id, Account.account_number)
        .order_by(desc("billed_amount"))
        .limit(limit)
        .all()
    )

    return [
        {
            "account_id": row.account_id,
            "account_number": row.account_number,
            "billed_amount": float(row.billed_amount or 0),
        }
        for row in rows
    ]


@router.get("/top-users-by-billed-amount")
def get_top_users_by_billed_amount(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=100),
):
    rows = (
        _users_query_for_owned_data(db, current_user)
        .outerjoin(Account, Account.user_id == User.id)
        .outerjoin(Bill, Bill.account_id == Account.id)
        .with_entities(
            User.id.label("user_id"),
            User.name,
            User.email,
            func.coalesce(func.sum(Bill.amount), 0.0).label("billed_amount"),
        )
        .group_by(User.id, User.name, User.email)
        .order_by(desc("billed_amount"))
        .limit(limit)
        .all()
    )

    return [
        {
            "user_id": row.user_id,
            "name": row.name,
            "email": row.email,
            "billed_amount": float(row.billed_amount or 0),
        }
        for row in rows
    ]


@router.get("/top-accounts-by-paid-amount")
def get_top_accounts_by_paid_amount(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=100),
):
    payment_amount_col = get_payment_amount_column(Payment)

    rows = (
        _accounts_query(db, current_user)
        .outerjoin(Bill, Bill.account_id == Account.id)
        .outerjoin(Payment, Payment.bill_id == Bill.id)
        .with_entities(
            Account.id.label("account_id"),
            Account.account_number,
            func.coalesce(func.sum(payment_amount_col), 0.0).label("paid_amount"),
        )
        .group_by(Account.id, Account.account_number)
        .order_by(desc("paid_amount"))
        .limit(limit)
        .all()
    )

    return [
        {
            "account_id": row.account_id,
            "account_number": row.account_number,
            "paid_amount": float(row.paid_amount or 0),
        }
        for row in rows
    ]


@router.get("/top-users-by-paid-amount")
def get_top_users_by_paid_amount(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=100),
):
    payment_amount_col = get_payment_amount_column(Payment)

    rows = (
        _users_query_for_owned_data(db, current_user)
        .outerjoin(Account, Account.user_id == User.id)
        .outerjoin(Bill, Bill.account_id == Account.id)
        .outerjoin(Payment, Payment.bill_id == Bill.id)
        .with_entities(
            User.id.label("user_id"),
            User.name,
            User.email,
            func.coalesce(func.sum(payment_amount_col), 0.0).label("paid_amount"),
        )
        .group_by(User.id, User.name, User.email)
        .order_by(desc("paid_amount"))
        .limit(limit)
        .all()
    )

    return [
        {
            "user_id": row.user_id,
            "name": row.name,
            "email": row.email,
            "paid_amount": float(row.paid_amount or 0),
        }
        for row in rows
    ]


@router.get("/top-users-by-meters")
def get_top_users_by_meters(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=100),
):
    rows = (
        _users_query_for_owned_data(db, current_user)
        .outerjoin(Account, Account.user_id == User.id)
        .outerjoin(Meter, Meter.account_id == Account.id)
        .with_entities(
            User.id.label("user_id"),
            User.name,
            User.email,
            func.count(Meter.id).label("meters_count"),
        )
        .group_by(User.id, User.name, User.email)
        .order_by(desc("meters_count"))
        .limit(limit)
        .all()
    )

    return [
        {
            "user_id": row.user_id,
            "name": row.name,
            "email": row.email,
            "meters_count": row.meters_count,
        }
        for row in rows
    ]


@router.get("/top-users-by-readings")
def get_top_users_by_readings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=100),
):
    rows = (
        _users_query_for_owned_data(db, current_user)
        .outerjoin(Account, Account.user_id == User.id)
        .outerjoin(Meter, Meter.account_id == Account.id)
        .outerjoin(Reading, Reading.meter_id == Meter.id)
        .with_entities(
            User.id.label("user_id"),
            User.name,
            User.email,
            func.count(Reading.id).label("readings_count"),
        )
        .group_by(User.id, User.name, User.email)
        .order_by(desc("readings_count"))
        .limit(limit)
        .all()
    )

    return [
        {
            "user_id": row.user_id,
            "name": row.name,
            "email": row.email,
            "readings_count": row.readings_count,
        }
        for row in rows
    ]


@router.get("/top-accounts-by-readings")
def get_top_accounts_by_readings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=100),
):
    rows = (
        _accounts_query(db, current_user)
        .outerjoin(Meter, Meter.account_id == Account.id)
        .outerjoin(Reading, Reading.meter_id == Meter.id)
        .with_entities(
            Account.id.label("account_id"),
            Account.account_number,
            func.count(Reading.id).label("readings_count"),
        )
        .group_by(Account.id, Account.account_number)
        .order_by(desc("readings_count"))
        .limit(limit)
        .all()
    )

    return [
        {
            "account_id": row.account_id,
            "account_number": row.account_number,
            "readings_count": row.readings_count,
        }
        for row in rows
    ]


@router.get("/top-users-by-outstanding-balance")
def get_top_users_by_outstanding_balance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=100),
):
    payment_amount_col = get_payment_amount_column(Payment)

    rows = (
        _users_query_for_owned_data(db, current_user)
        .outerjoin(Account, Account.user_id == User.id)
        .outerjoin(Bill, Bill.account_id == Account.id)
        .outerjoin(Payment, Payment.bill_id == Bill.id)
        .with_entities(
            User.id.label("user_id"),
            User.name,
            User.email,
            func.coalesce(func.sum(Bill.amount), 0.0).label("billed_amount"),
            func.coalesce(func.sum(payment_amount_col), 0.0).label("paid_amount"),
        )
        .group_by(User.id, User.name, User.email)
        .all()
    )

    result = []
    for row in rows:
        outstanding_balance = float(row.billed_amount or 0) - float(row.paid_amount or 0)
        result.append(
            {
                "user_id": row.user_id,
                "name": row.name,
                "email": row.email,
                "billed_amount": float(row.billed_amount or 0),
                "paid_amount": float(row.paid_amount or 0),
                "outstanding_balance": max(outstanding_balance, 0.0),
            }
        )

    result.sort(key=lambda x: x["outstanding_balance"], reverse=True)
    return result[:limit]


@router.get("/top-accounts-by-average-bill-amount")
def get_top_accounts_by_average_bill_amount(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=100),
):
    rows = (
        _accounts_query(db, current_user)
        .outerjoin(Bill, Bill.account_id == Account.id)
        .with_entities(
            Account.id.label("account_id"),
            Account.account_number,
            func.coalesce(func.avg(Bill.amount), 0.0).label("average_bill_amount"),
        )
        .group_by(Account.id, Account.account_number)
        .order_by(desc("average_bill_amount"))
        .limit(limit)
        .all()
    )

    return [
        {
            "account_id": row.account_id,
            "account_number": row.account_number,
            "average_bill_amount": float(row.average_bill_amount or 0),
        }
        for row in rows
    ]


@router.get("/top-users-by-average-bill-amount")
def get_top_users_by_average_bill_amount(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=100),
):
    rows = (
        _users_query_for_owned_data(db, current_user)
        .outerjoin(Account, Account.user_id == User.id)
        .outerjoin(Bill, Bill.account_id == Account.id)
        .with_entities(
            User.id.label("user_id"),
            User.name,
            User.email,
            func.coalesce(func.avg(Bill.amount), 0.0).label("average_bill_amount"),
        )
        .group_by(User.id, User.name, User.email)
        .order_by(desc("average_bill_amount"))
        .limit(limit)
        .all()
    )

    return [
        {
            "user_id": row.user_id,
            "name": row.name,
            "email": row.email,
            "average_bill_amount": float(row.average_bill_amount or 0),
        }
        for row in rows
    ]


@router.get("/top-accounts-by-average-payment-amount")
def get_top_accounts_by_average_payment_amount(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=100),
):
    payment_amount_col = get_payment_amount_column(Payment)

    rows = (
        _accounts_query(db, current_user)
        .outerjoin(Bill, Bill.account_id == Account.id)
        .outerjoin(Payment, Payment.bill_id == Bill.id)
        .with_entities(
            Account.id.label("account_id"),
            Account.account_number,
            func.coalesce(func.avg(payment_amount_col), 0.0).label("average_payment_amount"),
        )
        .group_by(Account.id, Account.account_number)
        .order_by(desc("average_payment_amount"))
        .limit(limit)
        .all()
    )

    return [
        {
            "account_id": row.account_id,
            "account_number": row.account_number,
            "average_payment_amount": float(row.average_payment_amount or 0),
        }
        for row in rows
    ]


@router.get("/top-users-by-average-payment-amount")
def get_top_users_by_average_payment_amount(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=100),
):
    payment_amount_col = get_payment_amount_column(Payment)

    rows = (
        _users_query_for_owned_data(db, current_user)
        .outerjoin(Account, Account.user_id == User.id)
        .outerjoin(Bill, Bill.account_id == Account.id)
        .outerjoin(Payment, Payment.bill_id == Bill.id)
        .with_entities(
            User.id.label("user_id"),
            User.name,
            User.email,
            func.coalesce(func.avg(payment_amount_col), 0.0).label("average_payment_amount"),
        )
        .group_by(User.id, User.name, User.email)
        .order_by(desc("average_payment_amount"))
        .limit(limit)
        .all()
    )

    return [
        {
            "user_id": row.user_id,
            "name": row.name,
            "email": row.email,
            "average_payment_amount": float(row.average_payment_amount or 0),
        }
        for row in rows
    ]