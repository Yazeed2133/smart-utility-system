from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.account import Account
from app.models.bill import Bill
from app.models.meter import Meter
from app.models.payment import Payment
from app.models.reading import Reading
from app.models.user import User
from app.schemas.dashboard import (
    BillStatusTrendResponse,
    DashboardRecentListsResponse,
    DashboardStatsResponse,
    DashboardSummaryResponse,
    DashboardTrendResponse,
    DashboardYearlyTrendResponse,
    PaymentMethodTrendResponse,
    TopAccountsByAverageBillAmountResponse,
    TopAccountsByAveragePaymentAmountResponse,
    TopAccountsByBillsResponse,
    TopAccountsByBilledAmountResponse,
    TopAccountsByMetersResponse,
    TopAccountsByPaidAmountResponse,
    TopAccountsByPaymentsResponse,
    TopAccountsByReadingsResponse,
    TopMetersByReadingsResponse,
    TopOutstandingAccountsResponse,
    TopUsersByAccountsResponse,
    TopUsersByAverageBillAmountResponse,
    TopUsersByAveragePaymentAmountResponse,
    TopUsersByBillsResponse,
    TopUsersByBilledAmountResponse,
    TopUsersByMetersResponse,
    TopUsersByOutstandingBalanceResponse,
    TopUsersByPaidAmountResponse,
    TopUsersByPaymentsResponse,
    TopUsersByReadingsResponse,
)
from app.utils import (
    apply_account_filter,
    apply_bill_filter,
    apply_meter_filter,
    apply_payment_filter,
    build_dashboard_summary_data,
    build_grouped_count_trends,
    build_period_trends,
    get_payment_amount_column,
    validate_dashboard_filters,
    validate_date_range,
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummaryResponse)
def dashboard_summary(
    recent_limit: int = Query(5, ge=1, le=100),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    db: Session = Depends(get_db),
):
    return build_dashboard_summary_data(
        db,
        recent_limit=recent_limit,
        date_from=date_from,
        date_to=date_to,
    )


@router.get("/stats", response_model=DashboardStatsResponse)
def dashboard_stats(
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    db: Session = Depends(get_db),
):
    data = build_dashboard_summary_data(
        db,
        date_from=date_from,
        date_to=date_to,
    )

    return {
        "total_users": data["total_users"],
        "total_accounts": data["total_accounts"],
        "total_meters": data["total_meters"],
        "total_bills": data["total_bills"],
        "total_payments": data["total_payments"],
        "monthly_new_users_count": data["monthly_new_users_count"],
        "monthly_new_accounts_count": data["monthly_new_accounts_count"],
        "monthly_new_meters_count": data["monthly_new_meters_count"],
        "monthly_new_bills_count": data["monthly_new_bills_count"],
        "monthly_new_payments_count": data["monthly_new_payments_count"],
        "overdue_bills_count": data["overdue_bills_count"],
        "pending_bills_count": data["pending_bills_count"],
        "paid_bills_count": data["paid_bills_count"],
        "total_billed_amount": data["total_billed_amount"],
        "total_paid_amount": data["total_paid_amount"],
        "unpaid_total_amount": data["unpaid_total_amount"],
        "average_bill_amount": data["average_bill_amount"],
        "average_payment_amount": data["average_payment_amount"],
        "monthly_bills_total": data["monthly_bills_total"],
        "monthly_payments_total": data["monthly_payments_total"],
        "fully_paid_percentage": data["fully_paid_percentage"],
        "collection_rate": data["collection_rate"],
        "bill_status_counts": data["bill_status_counts"],
        "payment_method_counts": data["payment_method_counts"],
        "account_type_counts": data["account_type_counts"],
        "meter_type_counts": data["meter_type_counts"],
        "latest_bill_status_summary": data["latest_bill_status_summary"],
        "latest_payment_summary": data["latest_payment_summary"],
        "recent_activity_summary": data["recent_activity_summary"],
    }


@router.get("/recent", response_model=DashboardRecentListsResponse)
def dashboard_recent(
    limit: int = Query(5, ge=1, le=100),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    db: Session = Depends(get_db),
):
    data = build_dashboard_summary_data(
        db,
        recent_limit=limit,
        date_from=date_from,
        date_to=date_to,
    )

    return {
        "recent_users": data["recent_users"],
        "recent_accounts": data["recent_accounts"],
        "recent_meters": data["recent_meters"],
        "recent_readings": data["recent_readings"],
        "recent_bills": data["recent_bills"],
        "recent_payments": data["recent_payments"],
    }


@router.get("/trends")
def dashboard_trends(
    group_by: str = Query("month"),
    limit: int | None = Query(None, ge=1, le=500),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    db: Session = Depends(get_db),
):
    validate_date_range(date_from, date_to)

    if group_by not in ["month", "year"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid group_by. Allowed values: month, year",
        )

    if group_by == "month":
        trends = build_period_trends(
            db=db,
            date_format="%Y-%m",
            label_name="month",
            bill_date_from=date_from,
            bill_date_to=date_to,
            payment_date_from=date_from,
            payment_date_to=date_to,
        )
        if limit:
            trends = trends[-limit:]
        return DashboardTrendResponse(trends=trends)

    trends = build_period_trends(
        db=db,
        date_format="%Y",
        label_name="year",
        bill_date_from=date_from,
        bill_date_to=date_to,
        payment_date_from=date_from,
        payment_date_to=date_to,
    )
    if limit:
        trends = trends[-limit:]
    return DashboardYearlyTrendResponse(trends=trends)


@router.get("/yearly-trends", response_model=DashboardYearlyTrendResponse)
def dashboard_yearly_trends(
    limit: int | None = Query(None, ge=1, le=500),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    db: Session = Depends(get_db),
):
    validate_date_range(date_from, date_to)

    trends = build_period_trends(
        db=db,
        date_format="%Y",
        label_name="year",
        bill_date_from=date_from,
        bill_date_to=date_to,
        payment_date_from=date_from,
        payment_date_to=date_to,
    )

    if limit:
        trends = trends[-limit:]

    return {"trends": trends}


@router.get("/bill-status-trends", response_model=BillStatusTrendResponse)
def dashboard_bill_status_trends(
    limit: int | None = Query(None, ge=1, le=500),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    db: Session = Depends(get_db),
):
    validate_date_range(date_from, date_to)

    trends = build_grouped_count_trends(
        db=db,
        model=Bill,
        date_format="%Y-%m",
        date_label="month",
        category_column=Bill.status,
        categories=["pending", "paid", "overdue"],
        date_from=date_from,
        date_to=date_to,
    )

    if limit:
        trends = trends[-limit:]

    return {"trends": trends}


@router.get("/payment-method-trends", response_model=PaymentMethodTrendResponse)
def dashboard_payment_method_trends(
    limit: int | None = Query(None, ge=1, le=500),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    db: Session = Depends(get_db),
):
    validate_date_range(date_from, date_to)

    trends = build_grouped_count_trends(
        db=db,
        model=Payment,
        date_format="%Y-%m",
        date_label="month",
        category_column=Payment.payment_method,
        categories=["cash", "card", "bank_transfer"],
        date_from=date_from,
        date_to=date_to,
    )

    if limit:
        trends = trends[-limit:]

    return {"trends": trends}


@router.get("/top-outstanding-accounts", response_model=TopOutstandingAccountsResponse)
def dashboard_top_outstanding_accounts(
    limit: int = Query(5, ge=1, le=100),
    account_type: str | None = Query(None),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    db: Session = Depends(get_db),
):
    validate_dashboard_filters(account_type=account_type)
    validate_date_range(date_from, date_to)

    query = db.query(Account)
    query = apply_account_filter(query, account_type)

    if date_from:
        query = query.filter(Account.created_at >= date_from)
    if date_to:
        query = query.filter(Account.created_at <= date_to)

    accounts = query.order_by(desc(Account.balance)).limit(limit).all()

    return {
        "accounts": [
            {
                "account_id": account.id,
                "account_number": account.account_number,
                "account_type": account.account_type,
                "balance": float(account.balance),
            }
            for account in accounts
        ]
    }


@router.get("/top-users-by-accounts", response_model=TopUsersByAccountsResponse)
def dashboard_top_users_by_accounts(
    limit: int = Query(5, ge=1, le=100),
    account_type: str | None = Query(None),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    db: Session = Depends(get_db),
):
    validate_dashboard_filters(account_type=account_type)
    validate_date_range(date_from, date_to)

    query = (
        db.query(
            User.id.label("entity_id"),
            User.name,
            User.email,
            func.count(Account.id).label("total_count"),
        )
        .join(Account, Account.user_id == User.id)
    )

    query = apply_account_filter(query, account_type)

    if date_from:
        query = query.filter(Account.created_at >= date_from)
    if date_to:
        query = query.filter(Account.created_at <= date_to)

    rows = (
        query.group_by(User.id, User.name, User.email)
        .order_by(desc(func.count(Account.id)))
        .limit(limit)
        .all()
    )

    return {
        "users": [
            {
                "user_id": row.entity_id,
                "name": row.name,
                "email": row.email,
                "accounts_count": int(row.total_count),
            }
            for row in rows
        ]
    }


@router.get("/top-accounts-by-meters", response_model=TopAccountsByMetersResponse)
def dashboard_top_accounts_by_meters(
    limit: int = Query(5, ge=1, le=100),
    account_type: str | None = Query(None),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    db: Session = Depends(get_db),
):
    validate_dashboard_filters(account_type=account_type)
    validate_date_range(date_from, date_to)

    query = (
        db.query(
            Account.id.label("entity_id"),
            Account.account_number,
            Account.account_type,
            func.count(Meter.id).label("total_count"),
        )
        .join(Meter, Meter.account_id == Account.id)
    )

    query = apply_account_filter(query, account_type)

    if date_from:
        query = query.filter(Meter.created_at >= date_from)
    if date_to:
        query = query.filter(Meter.created_at <= date_to)

    rows = (
        query.group_by(Account.id, Account.account_number, Account.account_type)
        .order_by(desc(func.count(Meter.id)))
        .limit(limit)
        .all()
    )

    return {
        "accounts": [
            {
                "account_id": row.entity_id,
                "account_number": row.account_number,
                "account_type": row.account_type,
                "meters_count": int(row.total_count),
            }
            for row in rows
        ]
    }


@router.get("/top-users-by-meters", response_model=TopUsersByMetersResponse)
def dashboard_top_users_by_meters(
    limit: int = Query(5, ge=1, le=100),
    account_type: str | None = Query(None),
    meter_type: str | None = Query(None),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    db: Session = Depends(get_db),
):
    validate_dashboard_filters(account_type=account_type, meter_type=meter_type)
    validate_date_range(date_from, date_to)

    query = (
        db.query(
            User.id.label("user_id"),
            User.name,
            User.email,
            func.count(Meter.id).label("meters_count"),
        )
        .join(Account, Account.user_id == User.id)
        .join(Meter, Meter.account_id == Account.id)
    )

    query = apply_account_filter(query, account_type)
    query = apply_meter_filter(query, meter_type)

    if date_from:
        query = query.filter(Meter.created_at >= date_from)
    if date_to:
        query = query.filter(Meter.created_at <= date_to)

    rows = (
        query.group_by(User.id, User.name, User.email)
        .order_by(desc(func.count(Meter.id)))
        .limit(limit)
        .all()
    )

    return {
        "users": [
            {
                "user_id": row.user_id,
                "name": row.name,
                "email": row.email,
                "meters_count": int(row.meters_count),
            }
            for row in rows
        ]
    }


@router.get("/top-meters-by-readings", response_model=TopMetersByReadingsResponse)
def dashboard_top_meters_by_readings(
    limit: int = Query(5, ge=1, le=100),
    meter_type: str | None = Query(None),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    db: Session = Depends(get_db),
):
    validate_dashboard_filters(meter_type=meter_type)
    validate_date_range(date_from, date_to)

    query = (
        db.query(
            Meter.id.label("entity_id"),
            Meter.meter_number,
            Meter.meter_type,
            func.count(Reading.id).label("total_count"),
        )
        .join(Reading, Reading.meter_id == Meter.id)
    )

    query = apply_meter_filter(query, meter_type)

    if date_from:
        query = query.filter(Reading.created_at >= date_from)
    if date_to:
        query = query.filter(Reading.created_at <= date_to)

    rows = (
        query.group_by(Meter.id, Meter.meter_number, Meter.meter_type)
        .order_by(desc(func.count(Reading.id)))
        .limit(limit)
        .all()
    )

    return {
        "meters": [
            {
                "meter_id": row.entity_id,
                "meter_number": row.meter_number,
                "meter_type": row.meter_type,
                "readings_count": int(row.total_count),
            }
            for row in rows
        ]
    }


@router.get("/top-users-by-readings", response_model=TopUsersByReadingsResponse)
def dashboard_top_users_by_readings(
    limit: int = Query(5, ge=1, le=100),
    account_type: str | None = Query(None),
    meter_type: str | None = Query(None),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    db: Session = Depends(get_db),
):
    validate_dashboard_filters(account_type=account_type, meter_type=meter_type)
    validate_date_range(date_from, date_to)

    query = (
        db.query(
            User.id.label("user_id"),
            User.name,
            User.email,
            func.count(Reading.id).label("readings_count"),
        )
        .join(Account, Account.user_id == User.id)
        .join(Meter, Meter.account_id == Account.id)
        .join(Reading, Reading.meter_id == Meter.id)
    )

    query = apply_account_filter(query, account_type)
    query = apply_meter_filter(query, meter_type)

    if date_from:
        query = query.filter(Reading.created_at >= date_from)
    if date_to:
        query = query.filter(Reading.created_at <= date_to)

    rows = (
        query.group_by(User.id, User.name, User.email)
        .order_by(desc(func.count(Reading.id)))
        .limit(limit)
        .all()
    )

    return {
        "users": [
            {
                "user_id": row.user_id,
                "name": row.name,
                "email": row.email,
                "readings_count": int(row.readings_count),
            }
            for row in rows
        ]
    }


@router.get("/top-accounts-by-readings", response_model=TopAccountsByReadingsResponse)
def dashboard_top_accounts_by_readings(
    limit: int = Query(5, ge=1, le=100),
    account_type: str | None = Query(None),
    meter_type: str | None = Query(None),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    db: Session = Depends(get_db),
):
    validate_dashboard_filters(account_type=account_type, meter_type=meter_type)
    validate_date_range(date_from, date_to)

    query = (
        db.query(
            Account.id.label("account_id"),
            Account.account_number,
            Account.account_type,
            func.count(Reading.id).label("readings_count"),
        )
        .join(Meter, Meter.account_id == Account.id)
        .join(Reading, Reading.meter_id == Meter.id)
    )

    query = apply_account_filter(query, account_type)
    query = apply_meter_filter(query, meter_type)

    if date_from:
        query = query.filter(Reading.created_at >= date_from)
    if date_to:
        query = query.filter(Reading.created_at <= date_to)

    rows = (
        query.group_by(Account.id, Account.account_number, Account.account_type)
        .order_by(desc(func.count(Reading.id)))
        .limit(limit)
        .all()
    )

    return {
        "accounts": [
            {
                "account_id": row.account_id,
                "account_number": row.account_number,
                "account_type": row.account_type,
                "readings_count": int(row.readings_count),
            }
            for row in rows
        ]
    }


@router.get("/top-accounts-by-bills", response_model=TopAccountsByBillsResponse)
def dashboard_top_accounts_by_bills(
    limit: int = Query(5, ge=1, le=100),
    account_type: str | None = Query(None),
    bill_status: str | None = Query(None),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    db: Session = Depends(get_db),
):
    validate_dashboard_filters(account_type=account_type, bill_status=bill_status)
    validate_date_range(date_from, date_to)

    query = (
        db.query(
            Account.id.label("entity_id"),
            Account.account_number,
            Account.account_type,
            func.count(Bill.id).label("total_count"),
        )
        .join(Bill, Bill.account_id == Account.id)
    )

    query = apply_account_filter(query, account_type)
    query = apply_bill_filter(query, bill_status, date_from, date_to)

    rows = (
        query.group_by(Account.id, Account.account_number, Account.account_type)
        .order_by(desc(func.count(Bill.id)))
        .limit(limit)
        .all()
    )

    return {
        "accounts": [
            {
                "account_id": row.entity_id,
                "account_number": row.account_number,
                "account_type": row.account_type,
                "bills_count": int(row.total_count),
            }
            for row in rows
        ]
    }


@router.get("/top-users-by-bills", response_model=TopUsersByBillsResponse)
def dashboard_top_users_by_bills(
    limit: int = Query(5, ge=1, le=100),
    bill_status: str | None = Query(None),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    db: Session = Depends(get_db),
):
    validate_dashboard_filters(bill_status=bill_status)
    validate_date_range(date_from, date_to)

    query = (
        db.query(
            User.id.label("entity_id"),
            User.name,
            User.email,
            func.count(Bill.id).label("total_count"),
        )
        .join(Account, Account.user_id == User.id)
        .join(Bill, Bill.account_id == Account.id)
    )

    query = apply_bill_filter(query, bill_status, date_from, date_to)

    rows = (
        query.group_by(User.id, User.name, User.email)
        .order_by(desc(func.count(Bill.id)))
        .limit(limit)
        .all()
    )

    return {
        "users": [
            {
                "user_id": row.entity_id,
                "name": row.name,
                "email": row.email,
                "bills_count": int(row.total_count),
            }
            for row in rows
        ]
    }


@router.get("/top-accounts-by-payments", response_model=TopAccountsByPaymentsResponse)
def dashboard_top_accounts_by_payments(
    limit: int = Query(5, ge=1, le=100),
    account_type: str | None = Query(None),
    bill_status: str | None = Query(None),
    payment_method: str | None = Query(None),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    db: Session = Depends(get_db),
):
    validate_dashboard_filters(
        account_type=account_type,
        bill_status=bill_status,
        payment_method=payment_method,
    )
    validate_date_range(date_from, date_to)

    query = (
        db.query(
            Account.id.label("entity_id"),
            Account.account_number,
            Account.account_type,
            func.count(Payment.id).label("total_count"),
        )
        .join(Bill, Bill.account_id == Account.id)
        .join(Payment, Payment.bill_id == Bill.id)
    )

    query = apply_account_filter(query, account_type)
    query = apply_bill_filter(query, bill_status)
    query = apply_payment_filter(query, payment_method, date_from, date_to)

    rows = (
        query.group_by(Account.id, Account.account_number, Account.account_type)
        .order_by(desc(func.count(Payment.id)))
        .limit(limit)
        .all()
    )

    return {
        "accounts": [
            {
                "account_id": row.entity_id,
                "account_number": row.account_number,
                "account_type": row.account_type,
                "payments_count": int(row.total_count),
            }
            for row in rows
        ]
    }


@router.get("/top-users-by-payments", response_model=TopUsersByPaymentsResponse)
def dashboard_top_users_by_payments(
    limit: int = Query(5, ge=1, le=100),
    bill_status: str | None = Query(None),
    payment_method: str | None = Query(None),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    db: Session = Depends(get_db),
):
    validate_dashboard_filters(
        bill_status=bill_status,
        payment_method=payment_method,
    )
    validate_date_range(date_from, date_to)

    query = (
        db.query(
            User.id.label("entity_id"),
            User.name,
            User.email,
            func.count(Payment.id).label("total_count"),
        )
        .join(Account, Account.user_id == User.id)
        .join(Bill, Bill.account_id == Account.id)
        .join(Payment, Payment.bill_id == Bill.id)
    )

    query = apply_bill_filter(query, bill_status)
    query = apply_payment_filter(query, payment_method, date_from, date_to)

    rows = (
        query.group_by(User.id, User.name, User.email)
        .order_by(desc(func.count(Payment.id)))
        .limit(limit)
        .all()
    )

    return {
        "users": [
            {
                "user_id": row.entity_id,
                "name": row.name,
                "email": row.email,
                "payments_count": int(row.total_count),
            }
            for row in rows
        ]
    }


@router.get("/top-accounts-by-billed-amount", response_model=TopAccountsByBilledAmountResponse)
def dashboard_top_accounts_by_billed_amount(
    limit: int = Query(5, ge=1, le=100),
    account_type: str | None = Query(None),
    bill_status: str | None = Query(None),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    db: Session = Depends(get_db),
):
    validate_dashboard_filters(account_type=account_type, bill_status=bill_status)
    validate_date_range(date_from, date_to)

    query = (
        db.query(
            Account.id.label("entity_id"),
            Account.account_number,
            Account.account_type,
            func.coalesce(func.sum(Bill.amount), 0).label("total_sum"),
        )
        .join(Bill, Bill.account_id == Account.id)
    )

    query = apply_account_filter(query, account_type)
    query = apply_bill_filter(query, bill_status, date_from, date_to)

    rows = (
        query.group_by(Account.id, Account.account_number, Account.account_type)
        .order_by(desc(func.coalesce(func.sum(Bill.amount), 0)))
        .limit(limit)
        .all()
    )

    return {
        "accounts": [
            {
                "account_id": row.entity_id,
                "account_number": row.account_number,
                "account_type": row.account_type,
                "total_billed_amount": float(row.total_sum),
            }
            for row in rows
        ]
    }


@router.get("/top-users-by-billed-amount", response_model=TopUsersByBilledAmountResponse)
def dashboard_top_users_by_billed_amount(
    limit: int = Query(5, ge=1, le=100),
    bill_status: str | None = Query(None),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    db: Session = Depends(get_db),
):
    validate_dashboard_filters(bill_status=bill_status)
    validate_date_range(date_from, date_to)

    query = (
        db.query(
            User.id.label("entity_id"),
            User.name,
            User.email,
            func.coalesce(func.sum(Bill.amount), 0).label("total_sum"),
        )
        .join(Account, Account.user_id == User.id)
        .join(Bill, Bill.account_id == Account.id)
    )

    query = apply_bill_filter(query, bill_status, date_from, date_to)

    rows = (
        query.group_by(User.id, User.name, User.email)
        .order_by(desc(func.coalesce(func.sum(Bill.amount), 0)))
        .limit(limit)
        .all()
    )

    return {
        "users": [
            {
                "user_id": row.entity_id,
                "name": row.name,
                "email": row.email,
                "total_billed_amount": float(row.total_sum),
            }
            for row in rows
        ]
    }


@router.get("/top-accounts-by-paid-amount", response_model=TopAccountsByPaidAmountResponse)
def dashboard_top_accounts_by_paid_amount(
    limit: int = Query(5, ge=1, le=100),
    account_type: str | None = Query(None),
    bill_status: str | None = Query(None),
    payment_method: str | None = Query(None),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    db: Session = Depends(get_db),
):
    validate_dashboard_filters(
        account_type=account_type,
        bill_status=bill_status,
        payment_method=payment_method,
    )
    validate_date_range(date_from, date_to)

    payment_amount_column = get_payment_amount_column()

    query = (
        db.query(
            Account.id.label("entity_id"),
            Account.account_number,
            Account.account_type,
            func.coalesce(func.sum(payment_amount_column), 0).label("total_sum"),
        )
        .join(Bill, Bill.account_id == Account.id)
        .join(Payment, Payment.bill_id == Bill.id)
    )

    query = apply_account_filter(query, account_type)
    query = apply_bill_filter(query, bill_status)
    query = apply_payment_filter(query, payment_method, date_from, date_to)

    rows = (
        query.group_by(Account.id, Account.account_number, Account.account_type)
        .order_by(desc(func.coalesce(func.sum(payment_amount_column), 0)))
        .limit(limit)
        .all()
    )

    return {
        "accounts": [
            {
                "account_id": row.entity_id,
                "account_number": row.account_number,
                "account_type": row.account_type,
                "total_paid_amount": float(row.total_sum),
            }
            for row in rows
        ]
    }


@router.get("/top-users-by-paid-amount", response_model=TopUsersByPaidAmountResponse)
def dashboard_top_users_by_paid_amount(
    limit: int = Query(5, ge=1, le=100),
    bill_status: str | None = Query(None),
    payment_method: str | None = Query(None),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    db: Session = Depends(get_db),
):
    validate_dashboard_filters(
        bill_status=bill_status,
        payment_method=payment_method,
    )
    validate_date_range(date_from, date_to)

    payment_amount_column = get_payment_amount_column()

    query = (
        db.query(
            User.id.label("entity_id"),
            User.name,
            User.email,
            func.coalesce(func.sum(payment_amount_column), 0).label("total_sum"),
        )
        .join(Account, Account.user_id == User.id)
        .join(Bill, Bill.account_id == Account.id)
        .join(Payment, Payment.bill_id == Bill.id)
    )

    query = apply_bill_filter(query, bill_status)
    query = apply_payment_filter(query, payment_method, date_from, date_to)

    rows = (
        query.group_by(User.id, User.name, User.email)
        .order_by(desc(func.coalesce(func.sum(payment_amount_column), 0)))
        .limit(limit)
        .all()
    )

    return {
        "users": [
            {
                "user_id": row.entity_id,
                "name": row.name,
                "email": row.email,
                "total_paid_amount": float(row.total_sum),
            }
            for row in rows
        ]
    }


@router.get("/top-users-by-outstanding-balance", response_model=TopUsersByOutstandingBalanceResponse)
def dashboard_top_users_by_outstanding_balance(
    limit: int = Query(5, ge=1, le=100),
    account_type: str | None = Query(None),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    db: Session = Depends(get_db),
):
    validate_dashboard_filters(account_type=account_type)
    validate_date_range(date_from, date_to)

    query = (
        db.query(
            User.id.label("user_id"),
            User.name,
            User.email,
            func.coalesce(func.sum(Account.balance), 0).label("total_balance"),
        )
        .join(Account, Account.user_id == User.id)
    )

    query = apply_account_filter(query, account_type)

    if date_from:
        query = query.filter(Account.created_at >= date_from)
    if date_to:
        query = query.filter(Account.created_at <= date_to)

    rows = (
        query.group_by(User.id, User.name, User.email)
        .order_by(desc(func.coalesce(func.sum(Account.balance), 0)))
        .limit(limit)
        .all()
    )

    return {
        "users": [
            {
                "user_id": row.user_id,
                "name": row.name,
                "email": row.email,
                "total_balance": float(row.total_balance),
            }
            for row in rows
        ]
    }


@router.get("/top-accounts-by-average-bill-amount", response_model=TopAccountsByAverageBillAmountResponse)
def dashboard_top_accounts_by_average_bill_amount(
    limit: int = Query(5, ge=1, le=100),
    account_type: str | None = Query(None),
    bill_status: str | None = Query(None),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    db: Session = Depends(get_db),
):
    validate_dashboard_filters(account_type=account_type, bill_status=bill_status)
    validate_date_range(date_from, date_to)

    query = (
        db.query(
            Account.id.label("account_id"),
            Account.account_number,
            Account.account_type,
            func.coalesce(func.avg(Bill.amount), 0).label("average_bill_amount"),
        )
        .join(Bill, Bill.account_id == Account.id)
    )

    query = apply_account_filter(query, account_type)
    query = apply_bill_filter(query, bill_status, date_from, date_to)

    rows = (
        query.group_by(Account.id, Account.account_number, Account.account_type)
        .order_by(desc(func.coalesce(func.avg(Bill.amount), 0)))
        .limit(limit)
        .all()
    )

    return {
        "accounts": [
            {
                "account_id": row.account_id,
                "account_number": row.account_number,
                "account_type": row.account_type,
                "average_bill_amount": float(row.average_bill_amount),
            }
            for row in rows
        ]
    }


@router.get("/top-users-by-average-bill-amount", response_model=TopUsersByAverageBillAmountResponse)
def dashboard_top_users_by_average_bill_amount(
    limit: int = Query(5, ge=1, le=100),
    bill_status: str | None = Query(None),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    db: Session = Depends(get_db),
):
    validate_dashboard_filters(bill_status=bill_status)
    validate_date_range(date_from, date_to)

    query = (
        db.query(
            User.id.label("user_id"),
            User.name,
            User.email,
            func.coalesce(func.avg(Bill.amount), 0).label("average_bill_amount"),
        )
        .join(Account, Account.user_id == User.id)
        .join(Bill, Bill.account_id == Account.id)
    )

    query = apply_bill_filter(query, bill_status, date_from, date_to)

    rows = (
        query.group_by(User.id, User.name, User.email)
        .order_by(desc(func.coalesce(func.avg(Bill.amount), 0)))
        .limit(limit)
        .all()
    )

    return {
        "users": [
            {
                "user_id": row.user_id,
                "name": row.name,
                "email": row.email,
                "average_bill_amount": float(row.average_bill_amount),
            }
            for row in rows
        ]
    }


@router.get("/top-accounts-by-average-payment-amount", response_model=TopAccountsByAveragePaymentAmountResponse)
def dashboard_top_accounts_by_average_payment_amount(
    limit: int = Query(5, ge=1, le=100),
    account_type: str | None = Query(None),
    bill_status: str | None = Query(None),
    payment_method: str | None = Query(None),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    db: Session = Depends(get_db),
):
    validate_dashboard_filters(
        account_type=account_type,
        bill_status=bill_status,
        payment_method=payment_method,
    )
    validate_date_range(date_from, date_to)

    payment_amount_column = get_payment_amount_column()

    query = (
        db.query(
            Account.id.label("account_id"),
            Account.account_number,
            Account.account_type,
            func.coalesce(func.avg(payment_amount_column), 0).label("average_payment_amount"),
        )
        .join(Bill, Bill.account_id == Account.id)
        .join(Payment, Payment.bill_id == Bill.id)
    )

    query = apply_account_filter(query, account_type)
    query = apply_bill_filter(query, bill_status)
    query = apply_payment_filter(query, payment_method, date_from, date_to)

    rows = (
        query.group_by(Account.id, Account.account_number, Account.account_type)
        .order_by(desc(func.coalesce(func.avg(payment_amount_column), 0)))
        .limit(limit)
        .all()
    )

    return {
        "accounts": [
            {
                "account_id": row.account_id,
                "account_number": row.account_number,
                "account_type": row.account_type,
                "average_payment_amount": float(row.average_payment_amount),
            }
            for row in rows
        ]
    }


@router.get("/top-users-by-average-payment-amount", response_model=TopUsersByAveragePaymentAmountResponse)
def dashboard_top_users_by_average_payment_amount(
    limit: int = Query(5, ge=1, le=100),
    bill_status: str | None = Query(None),
    payment_method: str | None = Query(None),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    db: Session = Depends(get_db),
):
    validate_dashboard_filters(
        bill_status=bill_status,
        payment_method=payment_method,
    )
    validate_date_range(date_from, date_to)

    payment_amount_column = get_payment_amount_column()

    query = (
        db.query(
            User.id.label("user_id"),
            User.name,
            User.email,
            func.coalesce(func.avg(payment_amount_column), 0).label("average_payment_amount"),
        )
        .join(Account, Account.user_id == User.id)
        .join(Bill, Bill.account_id == Account.id)
        .join(Payment, Payment.bill_id == Bill.id)
    )

    query = apply_bill_filter(query, bill_status)
    query = apply_payment_filter(query, payment_method, date_from, date_to)

    rows = (
        query.group_by(User.id, User.name, User.email)
        .order_by(desc(func.coalesce(func.avg(payment_amount_column), 0)))
        .limit(limit)
        .all()
    )

    return {
        "users": [
            {
                "user_id": row.user_id,
                "name": row.name,
                "email": row.email,
                "average_payment_amount": float(row.average_payment_amount),
            }
            for row in rows
        ]
    }