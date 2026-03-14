from datetime import date

from fastapi import HTTPException
from sqlalchemy import desc, func
from sqlalchemy.orm import Query, Session

from app.models.account import Account
from app.models.bill import Bill
from app.models.meter import Meter
from app.models.payment import Payment
from app.models.reading import Reading
from app.models.user import User

VALID_BILL_STATUSES = {"pending", "paid", "overdue"}
VALID_PAYMENT_METHODS = {"cash", "card", "bank_transfer"}
VALID_ACCOUNT_TYPES = {"residential", "commercial"}
VALID_METER_TYPES = {"electricity", "water", "gas"}


def get_object_or_404(db: Session, model, object_id: int):
    obj = db.query(model).filter(model.id == object_id).first()
    if not obj:
        raise HTTPException(
            status_code=404,
            detail=f"{model.__name__} with id {object_id} not found",
        )
    return obj


def get_payment_amount_column():
    if hasattr(Payment, "amount"):
        return Payment.amount
    if hasattr(Payment, "payment_amount"):
        return Payment.payment_amount

    raise AttributeError(
        "Payment model must have either 'amount' or 'payment_amount' column"
    )


def validate_dashboard_filters(
    bill_status: str | None = None,
    payment_method: str | None = None,
    account_type: str | None = None,
    meter_type: str | None = None,
):
    if bill_status and bill_status not in VALID_BILL_STATUSES:
        raise HTTPException(
            status_code=400,
            detail="Invalid bill_status. Allowed values: pending, paid, overdue",
        )

    if payment_method and payment_method not in VALID_PAYMENT_METHODS:
        raise HTTPException(
            status_code=400,
            detail="Invalid payment_method. Allowed values: cash, card, bank_transfer",
        )

    if account_type and account_type not in VALID_ACCOUNT_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Invalid account_type. Allowed values: residential, commercial",
        )

    if meter_type and meter_type not in VALID_METER_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Invalid meter_type. Allowed values: electricity, water, gas",
        )


def validate_date_range(
    date_from: date | None = None,
    date_to: date | None = None,
):
    if date_from and date_to and date_from > date_to:
        raise HTTPException(
            status_code=400,
            detail="date_from cannot be greater than date_to",
        )


def get_recent_model_items(db: Session, model, limit: int = 5):
    return db.query(model).order_by(desc(model.created_at)).limit(limit).all()


def build_recent_users(db: Session, limit: int = 5):
    users = get_recent_model_items(db, User, limit)
    return [
        {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "address": user.address,
            "created_at": user.created_at,
        }
        for user in users
    ]


def build_recent_accounts(db: Session, limit: int = 5):
    accounts = get_recent_model_items(db, Account, limit)
    return [
        {
            "id": account.id,
            "user_id": account.user_id,
            "account_number": account.account_number,
            "account_type": account.account_type,
            "balance": float(account.balance),
            "created_at": account.created_at,
        }
        for account in accounts
    ]


def build_recent_meters(db: Session, limit: int = 5):
    meters = get_recent_model_items(db, Meter, limit)
    return [
        {
            "id": meter.id,
            "account_id": meter.account_id,
            "meter_number": meter.meter_number,
            "meter_type": meter.meter_type,
            "location": meter.location,
            "created_at": meter.created_at,
        }
        for meter in meters
    ]


def build_recent_readings(db: Session, limit: int = 5):
    readings = get_recent_model_items(db, Reading, limit)
    return [
        {
            "id": reading.id,
            "meter_id": reading.meter_id,
            "reading_value": float(reading.reading_value),
            "reading_date": reading.reading_date,
            "created_at": reading.created_at,
        }
        for reading in readings
    ]


def build_recent_bills(db: Session, limit: int = 5):
    bills = get_recent_model_items(db, Bill, limit)
    return [
        {
            "id": bill.id,
            "account_id": bill.account_id,
            "amount": float(bill.amount),
            "due_date": bill.due_date,
            "status": bill.status,
            "created_at": bill.created_at,
        }
        for bill in bills
    ]


def build_recent_payments(db: Session, limit: int = 5):
    payment_amount_column = get_payment_amount_column()
    payments = get_recent_model_items(db, Payment, limit)
    return [
        {
            "id": payment.id,
            "bill_id": payment.bill_id,
            "amount": float(getattr(payment, payment_amount_column.key)),
            "payment_method": payment.payment_method,
            "payment_date": payment.payment_date,
            "created_at": payment.created_at,
        }
        for payment in payments
    ]


def build_latest_bill_status_summary(db: Session):
    latest_bill = db.query(Bill).order_by(desc(Bill.created_at)).first()

    if not latest_bill:
        return None

    return {
        "bill_id": latest_bill.id,
        "account_id": latest_bill.account_id,
        "status": latest_bill.status,
        "amount": float(latest_bill.amount),
        "due_date": latest_bill.due_date,
        "created_at": latest_bill.created_at,
    }


def build_latest_payment_summary(db: Session):
    payment_amount_column = get_payment_amount_column()
    latest_payment = db.query(Payment).order_by(desc(Payment.created_at)).first()

    if not latest_payment:
        return None

    return {
        "payment_id": latest_payment.id,
        "bill_id": latest_payment.bill_id,
        "amount": float(getattr(latest_payment, payment_amount_column.key)),
        "payment_method": latest_payment.payment_method,
        "payment_date": latest_payment.payment_date,
        "created_at": latest_payment.created_at,
    }


def build_recent_activity_summary(db: Session):
    return {
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


def apply_account_filter(query: Query, account_type: str | None = None):
    if account_type:
        query = query.filter(Account.account_type == account_type)
    return query


def apply_meter_filter(query: Query, meter_type: str | None = None):
    if meter_type:
        query = query.filter(Meter.meter_type == meter_type)
    return query


def apply_bill_filter(
    query: Query,
    bill_status: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
):
    if bill_status:
        query = query.filter(Bill.status == bill_status)
    if date_from:
        query = query.filter(Bill.created_at >= date_from)
    if date_to:
        query = query.filter(Bill.created_at <= date_to)
    return query


def apply_payment_filter(
    query: Query,
    payment_method: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
):
    if payment_method:
        query = query.filter(Payment.payment_method == payment_method)
    if date_from:
        query = query.filter(Payment.created_at >= date_from)
    if date_to:
        query = query.filter(Payment.created_at <= date_to)
    return query


def query_top_by_count(
    db: Session,
    entity_id_column,
    extra_columns,
    count_column,
    joins,
    group_by_columns,
    limit: int = 5,
):
    query = db.query(
        entity_id_column.label("entity_id"),
        *extra_columns,
        func.count(count_column).label("total_count"),
    )

    for join_target, join_condition in joins:
        query = query.join(join_target, join_condition)

    return (
        query.group_by(*group_by_columns)
        .order_by(desc(func.count(count_column)))
        .limit(limit)
        .all()
    )


def query_top_by_sum(
    db: Session,
    entity_id_column,
    extra_columns,
    sum_column,
    joins,
    group_by_columns,
    limit: int = 5,
):
    query = db.query(
        entity_id_column.label("entity_id"),
        *extra_columns,
        func.coalesce(func.sum(sum_column), 0).label("total_sum"),
    )

    for join_target, join_condition in joins:
        query = query.join(join_target, join_condition)

    return (
        query.group_by(*group_by_columns)
        .order_by(desc(func.coalesce(func.sum(sum_column), 0)))
        .limit(limit)
        .all()
    )


def build_dashboard_summary_data(
    db: Session,
    recent_limit: int = 5,
    date_from: date | None = None,
    date_to: date | None = None,
):
    validate_date_range(date_from, date_to)

    today = date.today()
    month_start = date(today.year, today.month, 1)

    payment_amount_column = get_payment_amount_column()

    users_query = db.query(User)
    accounts_query = db.query(Account)
    meters_query = db.query(Meter)
    readings_query = db.query(Reading)
    bills_query = db.query(Bill)
    payments_query = db.query(Payment)

    if date_from:
        users_query = users_query.filter(User.created_at >= date_from)
        accounts_query = accounts_query.filter(Account.created_at >= date_from)
        meters_query = meters_query.filter(Meter.created_at >= date_from)
        readings_query = readings_query.filter(Reading.created_at >= date_from)
        bills_query = bills_query.filter(Bill.created_at >= date_from)
        payments_query = payments_query.filter(Payment.created_at >= date_from)

    if date_to:
        users_query = users_query.filter(User.created_at <= date_to)
        accounts_query = accounts_query.filter(Account.created_at <= date_to)
        meters_query = meters_query.filter(Meter.created_at <= date_to)
        readings_query = readings_query.filter(Reading.created_at <= date_to)
        bills_query = bills_query.filter(Bill.created_at <= date_to)
        payments_query = payments_query.filter(Payment.created_at <= date_to)

    total_users = users_query.count()
    total_accounts = accounts_query.count()
    total_meters = meters_query.count()
    total_bills = bills_query.count()
    total_payments = payments_query.count()

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

    monthly_new_meters_count = (
        db.query(Meter)
        .filter(Meter.created_at >= month_start)
        .count()
    )

    monthly_new_bills_count = (
        db.query(Bill)
        .filter(Bill.created_at >= month_start)
        .count()
    )

    monthly_new_payments_count = (
        db.query(Payment)
        .filter(Payment.created_at >= month_start)
        .count()
    )

    overdue_bills_count = bills_query.filter(Bill.status == "overdue").count()
    pending_bills_count = bills_query.filter(Bill.status == "pending").count()
    paid_bills_count = bills_query.filter(Bill.status == "paid").count()

    total_billed_amount = bills_query.with_entities(
        func.coalesce(func.sum(Bill.amount), 0)
    ).scalar()

    total_paid_amount = payments_query.with_entities(
        func.coalesce(func.sum(payment_amount_column), 0)
    ).scalar()

    unpaid_total_amount = bills_query.filter(
        Bill.status.in_(["pending", "overdue"])
    ).with_entities(func.coalesce(func.sum(Bill.amount), 0)).scalar()

    average_bill_amount = bills_query.with_entities(
        func.coalesce(func.avg(Bill.amount), 0)
    ).scalar()

    average_payment_amount = payments_query.with_entities(
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
        bills_query.with_entities(Bill.status, func.count(Bill.id))
        .group_by(Bill.status)
        .all()
    )
    bill_status_counts = {
        status: count for status, count in bill_status_counts_query
    }

    payment_method_counts_query = (
        payments_query.with_entities(Payment.payment_method, func.count(Payment.id))
        .group_by(Payment.payment_method)
        .all()
    )
    payment_method_counts = {
        method: count for method, count in payment_method_counts_query
    }

    account_type_counts_query = (
        accounts_query.with_entities(Account.account_type, func.count(Account.id))
        .group_by(Account.account_type)
        .all()
    )
    account_type_counts = {
        account_type: count for account_type, count in account_type_counts_query
    }

    meter_type_counts_query = (
        meters_query.with_entities(Meter.meter_type, func.count(Meter.id))
        .group_by(Meter.meter_type)
        .all()
    )
    meter_type_counts = {
        meter_type: count for meter_type, count in meter_type_counts_query
    }

    recent_users_query = db.query(User)
    recent_accounts_query = db.query(Account)
    recent_meters_query = db.query(Meter)
    recent_readings_query = db.query(Reading)
    recent_bills_query = db.query(Bill)
    recent_payments_query = db.query(Payment)

    if date_from:
        recent_users_query = recent_users_query.filter(User.created_at >= date_from)
        recent_accounts_query = recent_accounts_query.filter(Account.created_at >= date_from)
        recent_meters_query = recent_meters_query.filter(Meter.created_at >= date_from)
        recent_readings_query = recent_readings_query.filter(Reading.created_at >= date_from)
        recent_bills_query = recent_bills_query.filter(Bill.created_at >= date_from)
        recent_payments_query = recent_payments_query.filter(Payment.created_at >= date_from)

    if date_to:
        recent_users_query = recent_users_query.filter(User.created_at <= date_to)
        recent_accounts_query = recent_accounts_query.filter(Account.created_at <= date_to)
        recent_meters_query = recent_meters_query.filter(Meter.created_at <= date_to)
        recent_readings_query = recent_readings_query.filter(Reading.created_at <= date_to)
        recent_bills_query = recent_bills_query.filter(Bill.created_at <= date_to)
        recent_payments_query = recent_payments_query.filter(Payment.created_at <= date_to)

    recent_users = [
        {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "address": user.address,
            "created_at": user.created_at,
        }
        for user in recent_users_query.order_by(desc(User.created_at)).limit(recent_limit).all()
    ]

    recent_accounts = [
        {
            "id": account.id,
            "user_id": account.user_id,
            "account_number": account.account_number,
            "account_type": account.account_type,
            "balance": float(account.balance),
            "created_at": account.created_at,
        }
        for account in recent_accounts_query.order_by(desc(Account.created_at)).limit(recent_limit).all()
    ]

    recent_meters = [
        {
            "id": meter.id,
            "account_id": meter.account_id,
            "meter_number": meter.meter_number,
            "meter_type": meter.meter_type,
            "location": meter.location,
            "created_at": meter.created_at,
        }
        for meter in recent_meters_query.order_by(desc(Meter.created_at)).limit(recent_limit).all()
    ]

    recent_readings = [
        {
            "id": reading.id,
            "meter_id": reading.meter_id,
            "reading_value": float(reading.reading_value),
            "reading_date": reading.reading_date,
            "created_at": reading.created_at,
        }
        for reading in recent_readings_query.order_by(desc(Reading.created_at)).limit(recent_limit).all()
    ]

    recent_bills = [
        {
            "id": bill.id,
            "account_id": bill.account_id,
            "amount": float(bill.amount),
            "due_date": bill.due_date,
            "status": bill.status,
            "created_at": bill.created_at,
        }
        for bill in recent_bills_query.order_by(desc(Bill.created_at)).limit(recent_limit).all()
    ]

    recent_payments = [
        {
            "id": payment.id,
            "bill_id": payment.bill_id,
            "amount": float(getattr(payment, payment_amount_column.key)),
            "payment_method": payment.payment_method,
            "payment_date": payment.payment_date,
            "created_at": payment.created_at,
        }
        for payment in recent_payments_query.order_by(desc(Payment.created_at)).limit(recent_limit).all()
    ]

    latest_bill_query = db.query(Bill)
    latest_payment_query = db.query(Payment)

    if date_from:
        latest_bill_query = latest_bill_query.filter(Bill.created_at >= date_from)
        latest_payment_query = latest_payment_query.filter(Payment.created_at >= date_from)

    if date_to:
        latest_bill_query = latest_bill_query.filter(Bill.created_at <= date_to)
        latest_payment_query = latest_payment_query.filter(Payment.created_at <= date_to)

    latest_bill = latest_bill_query.order_by(desc(Bill.created_at)).first()
    latest_payment = latest_payment_query.order_by(desc(Payment.created_at)).first()

    latest_bill_status_summary = None
    if latest_bill:
        latest_bill_status_summary = {
            "bill_id": latest_bill.id,
            "account_id": latest_bill.account_id,
            "status": latest_bill.status,
            "amount": float(latest_bill.amount),
            "due_date": latest_bill.due_date,
            "created_at": latest_bill.created_at,
        }

    latest_payment_summary = None
    if latest_payment:
        latest_payment_summary = {
            "payment_id": latest_payment.id,
            "bill_id": latest_payment.bill_id,
            "amount": float(getattr(latest_payment, payment_amount_column.key)),
            "payment_method": latest_payment.payment_method,
            "payment_date": latest_payment.payment_date,
            "created_at": latest_payment.created_at,
        }

    activity_user_query = db.query(User.created_at)
    activity_account_query = db.query(Account.created_at)
    activity_meter_query = db.query(Meter.created_at)
    activity_reading_query = db.query(Reading.created_at)
    activity_bill_query = db.query(Bill.created_at)
    activity_payment_query = db.query(Payment.created_at)

    if date_from:
        activity_user_query = activity_user_query.filter(User.created_at >= date_from)
        activity_account_query = activity_account_query.filter(Account.created_at >= date_from)
        activity_meter_query = activity_meter_query.filter(Meter.created_at >= date_from)
        activity_reading_query = activity_reading_query.filter(Reading.created_at >= date_from)
        activity_bill_query = activity_bill_query.filter(Bill.created_at >= date_from)
        activity_payment_query = activity_payment_query.filter(Payment.created_at >= date_from)

    if date_to:
        activity_user_query = activity_user_query.filter(User.created_at <= date_to)
        activity_account_query = activity_account_query.filter(Account.created_at <= date_to)
        activity_meter_query = activity_meter_query.filter(Meter.created_at <= date_to)
        activity_reading_query = activity_reading_query.filter(Reading.created_at <= date_to)
        activity_bill_query = activity_bill_query.filter(Bill.created_at <= date_to)
        activity_payment_query = activity_payment_query.filter(Payment.created_at <= date_to)

    recent_activity_summary = {
        "latest_user_created_at": activity_user_query.order_by(desc(User.created_at)).scalar(),
        "latest_account_created_at": activity_account_query.order_by(desc(Account.created_at)).scalar(),
        "latest_meter_created_at": activity_meter_query.order_by(desc(Meter.created_at)).scalar(),
        "latest_reading_created_at": activity_reading_query.order_by(desc(Reading.created_at)).scalar(),
        "latest_bill_created_at": activity_bill_query.order_by(desc(Bill.created_at)).scalar(),
        "latest_payment_created_at": activity_payment_query.order_by(desc(Payment.created_at)).scalar(),
    }

    return {
        "total_users": total_users,
        "total_accounts": total_accounts,
        "total_meters": total_meters,
        "total_bills": total_bills,
        "total_payments": total_payments,
        "monthly_new_users_count": monthly_new_users_count,
        "monthly_new_accounts_count": monthly_new_accounts_count,
        "monthly_new_meters_count": monthly_new_meters_count,
        "monthly_new_bills_count": monthly_new_bills_count,
        "monthly_new_payments_count": monthly_new_payments_count,
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


def build_period_trends(
    db: Session,
    date_format: str,
    label_name: str,
    bill_date_from: date | None = None,
    bill_date_to: date | None = None,
    payment_date_from: date | None = None,
    payment_date_to: date | None = None,
):
    payment_amount_column = get_payment_amount_column()

    bills_query = db.query(
        func.strftime(date_format, Bill.created_at).label(label_name),
        func.coalesce(func.sum(Bill.amount), 0).label("bills_total"),
    )

    payments_query = db.query(
        func.strftime(date_format, Payment.created_at).label(label_name),
        func.coalesce(func.sum(payment_amount_column), 0).label("payments_total"),
    )

    if bill_date_from:
        bills_query = bills_query.filter(Bill.created_at >= bill_date_from)
    if bill_date_to:
        bills_query = bills_query.filter(Bill.created_at <= bill_date_to)

    if payment_date_from:
        payments_query = payments_query.filter(Payment.created_at >= payment_date_from)
    if payment_date_to:
        payments_query = payments_query.filter(Payment.created_at <= payment_date_to)

    bills_rows = (
        bills_query
        .group_by(func.strftime(date_format, Bill.created_at))
        .order_by(func.strftime(date_format, Bill.created_at))
        .all()
    )

    payments_rows = (
        payments_query
        .group_by(func.strftime(date_format, Payment.created_at))
        .order_by(func.strftime(date_format, Payment.created_at))
        .all()
    )

    trends_map = {}

    for row in bills_rows:
        key = getattr(row, label_name)
        trends_map[key] = {
            label_name: key,
            "bills_total": float(row.bills_total),
            "payments_total": 0.0,
        }

    for row in payments_rows:
        key = getattr(row, label_name)
        if key not in trends_map:
            trends_map[key] = {
                label_name: key,
                "bills_total": 0.0,
                "payments_total": float(row.payments_total),
            }
        else:
            trends_map[key]["payments_total"] = float(row.payments_total)

    return [trends_map[key] for key in sorted(trends_map.keys())]


def build_grouped_count_trends(
    db: Session,
    model,
    date_format: str,
    date_label: str,
    category_column,
    categories: list[str],
    date_from: date | None = None,
    date_to: date | None = None,
):
    query = db.query(
        func.strftime(date_format, model.created_at).label(date_label),
        category_column,
        func.count(model.id).label("count"),
    )

    if date_from:
        query = query.filter(model.created_at >= date_from)
    if date_to:
        query = query.filter(model.created_at <= date_to)

    rows = (
        query.group_by(func.strftime(date_format, model.created_at), category_column)
        .order_by(func.strftime(date_format, model.created_at), category_column)
        .all()
    )

    trends_map = {}

    for row in rows:
        label_value = getattr(row, date_label)

        if label_value not in trends_map:
            trends_map[label_value] = {date_label: label_value}
            for category in categories:
                trends_map[label_value][category] = 0

        category_value = row[1]
        if category_value in categories:
            trends_map[label_value][category_value] = int(row.count)

    return [trends_map[key] for key in sorted(trends_map.keys())]