from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.account import Account
from app.models.bill import Bill
from app.models.meter import Meter
from app.models.payment import Payment
from app.models.reading import Reading
from app.models.user import User

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def get_payment_amount_column():
    if hasattr(Payment, "amount"):
        return Payment.amount
    if hasattr(Payment, "payment_amount"):
        return Payment.payment_amount
    if hasattr(Payment, "paid_amount"):
        return Payment.paid_amount
    raise AttributeError(
        "Payment model must have one of these fields: amount, payment_amount, paid_amount"
    )


@router.get("/summary")
def dashboard_summary(db: Session = Depends(get_db)):
    today = date.today()
    month_start = date(today.year, today.month, 1)

    payment_amount_column = get_payment_amount_column()

    total_users = db.query(User).count()
    total_accounts = db.query(Account).count()
    total_meters = db.query(Meter).count()
    total_bills = db.query(Bill).count()
    total_payments = db.query(Payment).count()

    monthly_new_users_count = (
        db.query(User)
        .filter(User.created_at >= month_start)
        .count()
    )

    monthly_new_accounts_count = (
        db.query(Account)
        .filter(Account.created_at >= month_start)
        .count()
    )

    overdue_bills_count = db.query(Bill).filter(Bill.status == "overdue").count()
    pending_bills_count = db.query(Bill).filter(Bill.status == "pending").count()
    paid_bills_count = db.query(Bill).filter(Bill.status == "paid").count()

    total_billed_amount = db.query(func.coalesce(func.sum(Bill.amount), 0)).scalar()
    total_paid_amount = db.query(
        func.coalesce(func.sum(payment_amount_column), 0)
    ).scalar()

    unpaid_total_amount = (
        db.query(func.coalesce(func.sum(Bill.amount), 0))
        .filter(Bill.status.in_(["pending", "overdue"]))
        .scalar()
    )

    average_bill_amount = db.query(func.coalesce(func.avg(Bill.amount), 0)).scalar()
    average_payment_amount = db.query(
        func.coalesce(func.avg(payment_amount_column), 0)
    ).scalar()

    monthly_bills_total = (
        db.query(func.coalesce(func.sum(Bill.amount), 0))
        .filter(Bill.created_at >= month_start)
        .scalar()
    )

    monthly_payments_total = (
        db.query(func.coalesce(func.sum(payment_amount_column), 0))
        .filter(Payment.created_at >= month_start)
        .scalar()
    )

    if total_bills > 0:
        fully_paid_percentage = round((paid_bills_count / total_bills) * 100, 2)
    else:
        fully_paid_percentage = 0.0

    if float(total_billed_amount) > 0:
        collection_rate = round(
            (float(total_paid_amount) / float(total_billed_amount)) * 100, 2
        )
    else:
        collection_rate = 0.0

    bill_status_counts_query = (
        db.query(Bill.status, func.count(Bill.id))
        .group_by(Bill.status)
        .all()
    )
    bill_status_counts = {
        status: count for status, count in bill_status_counts_query
    }

    payment_method_counts_query = (
        db.query(Payment.payment_method, func.count(Payment.id))
        .group_by(Payment.payment_method)
        .all()
    )
    payment_method_counts = {
        method: count for method, count in payment_method_counts_query
    }

    account_type_counts_query = (
        db.query(Account.account_type, func.count(Account.id))
        .group_by(Account.account_type)
        .all()
    )
    account_type_counts = {
        account_type: count for account_type, count in account_type_counts_query
    }

    meter_type_counts_query = (
        db.query(Meter.meter_type, func.count(Meter.id))
        .group_by(Meter.meter_type)
        .all()
    )
    meter_type_counts = {
        meter_type: count for meter_type, count in meter_type_counts_query
    }

    latest_bill = db.query(Bill).order_by(desc(Bill.created_at)).first()

    if latest_bill:
        latest_bill_status_summary = {
            "bill_id": latest_bill.id,
            "account_id": latest_bill.account_id,
            "status": latest_bill.status,
            "amount": latest_bill.amount,
            "due_date": latest_bill.due_date,
            "created_at": latest_bill.created_at,
        }
    else:
        latest_bill_status_summary = None

    latest_payment = db.query(Payment).order_by(desc(Payment.created_at)).first()

    if latest_payment:
        latest_payment_summary = {
            "payment_id": latest_payment.id,
            "bill_id": latest_payment.bill_id,
            "amount": getattr(latest_payment, payment_amount_column.key),
            "payment_method": latest_payment.payment_method,
            "payment_date": latest_payment.payment_date,
            "created_at": latest_payment.created_at,
        }
    else:
        latest_payment_summary = None

    recent_activity_summary = {
        "latest_user_created_at": (
            db.query(User.created_at).order_by(desc(User.created_at)).scalar()
        ),
        "latest_account_created_at": (
            db.query(Account.created_at).order_by(desc(Account.created_at)).scalar()
        ),
        "latest_meter_created_at": (
            db.query(Meter.created_at).order_by(desc(Meter.created_at)).scalar()
        ),
        "latest_reading_created_at": (
            db.query(Reading.created_at).order_by(desc(Reading.created_at)).scalar()
        ),
        "latest_bill_created_at": (
            db.query(Bill.created_at).order_by(desc(Bill.created_at)).scalar()
        ),
        "latest_payment_created_at": (
            db.query(Payment.created_at).order_by(desc(Payment.created_at)).scalar()
        ),
    }

    recent_users_query = (
        db.query(User)
        .order_by(desc(User.created_at))
        .limit(5)
        .all()
    )

    recent_users = [
        {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "address": user.address,
            "created_at": user.created_at,
        }
        for user in recent_users_query
    ]

    recent_accounts_query = (
        db.query(Account)
        .order_by(desc(Account.created_at))
        .limit(5)
        .all()
    )

    recent_accounts = [
        {
            "id": account.id,
            "user_id": account.user_id,
            "account_number": account.account_number,
            "account_type": account.account_type,
            "balance": account.balance,
            "created_at": account.created_at,
        }
        for account in recent_accounts_query
    ]

    recent_meters_query = (
        db.query(Meter)
        .order_by(desc(Meter.created_at))
        .limit(5)
        .all()
    )

    recent_meters = [
        {
            "id": meter.id,
            "account_id": meter.account_id,
            "meter_number": meter.meter_number,
            "meter_type": meter.meter_type,
            "location": meter.location,
            "created_at": meter.created_at,
        }
        for meter in recent_meters_query
    ]

    recent_readings_query = (
        db.query(Reading)
        .order_by(desc(Reading.created_at))
        .limit(5)
        .all()
    )

    recent_readings = [
        {
            "id": reading.id,
            "meter_id": reading.meter_id,
            "reading_value": reading.reading_value,
            "reading_date": reading.reading_date,
            "created_at": reading.created_at,
        }
        for reading in recent_readings_query
    ]

    recent_bills_query = (
        db.query(Bill)
        .order_by(desc(Bill.created_at))
        .limit(5)
        .all()
    )

    recent_bills = [
        {
            "id": bill.id,
            "account_id": bill.account_id,
            "amount": bill.amount,
            "due_date": bill.due_date,
            "status": bill.status,
            "created_at": bill.created_at,
        }
        for bill in recent_bills_query
    ]

    recent_payments_query = (
        db.query(Payment)
        .order_by(desc(Payment.created_at))
        .limit(5)
        .all()
    )

    recent_payments = [
        {
            "id": payment.id,
            "bill_id": payment.bill_id,
            "amount": getattr(payment, payment_amount_column.key),
            "payment_method": payment.payment_method,
            "payment_date": payment.payment_date,
            "created_at": payment.created_at,
        }
        for payment in recent_payments_query
    ]

    return {
        "total_users": total_users,
        "total_accounts": total_accounts,
        "total_meters": total_meters,
        "total_bills": total_bills,
        "total_payments": total_payments,
        "monthly_new_users_count": monthly_new_users_count,
        "monthly_new_accounts_count": monthly_new_accounts_count,
        "overdue_bills_count": overdue_bills_count,
        "pending_bills_count": pending_bills_count,
        "paid_bills_count": paid_bills_count,
        "total_billed_amount": float(total_billed_amount),
        "total_paid_amount": float(total_paid_amount),
        "unpaid_total_amount": float(unpaid_total_amount),
        "average_bill_amount": float(average_bill_amount),
        "average_payment_amount": float(average_payment_amount),
        "monthly_bills_total": float(monthly_bills_total),
        "monthly_payments_total": float(monthly_payments_total),
        "fully_paid_percentage": fully_paid_percentage,
        "collection_rate": collection_rate,
        "bill_status_counts": bill_status_counts,
        "payment_method_counts": payment_method_counts,
        "account_type_counts": account_type_counts,
        "meter_type_counts": meter_type_counts,
        "latest_bill_status_summary": latest_bill_status_summary,
        "latest_payment_summary": latest_payment_summary,
        "recent_activity_summary": recent_activity_summary,
        "recent_users": recent_users,
        "recent_accounts": recent_accounts,
        "recent_meters": recent_meters,
        "recent_readings": recent_readings,
        "recent_bills": recent_bills,
        "recent_payments": recent_payments,
    }