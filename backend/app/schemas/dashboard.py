from datetime import date, datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict


class LatestBillStatusSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    bill_id: int
    account_id: int
    status: str
    amount: float
    due_date: date
    created_at: datetime


class LatestPaymentSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    payment_id: int
    bill_id: int
    amount: float
    payment_method: str
    payment_date: date
    created_at: datetime


class RecentActivitySummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    latest_user_created_at: Optional[datetime] = None
    latest_account_created_at: Optional[datetime] = None
    latest_meter_created_at: Optional[datetime] = None
    latest_reading_created_at: Optional[datetime] = None
    latest_bill_created_at: Optional[datetime] = None
    latest_payment_created_at: Optional[datetime] = None


class RecentUserItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    phone: str
    address: str
    created_at: datetime


class RecentAccountItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    account_number: str
    account_type: str
    balance: float
    created_at: datetime


class RecentMeterItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    account_id: int
    meter_number: str
    meter_type: str
    location: str
    created_at: datetime


class RecentReadingItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    meter_id: int
    reading_value: float
    reading_date: date
    created_at: datetime


class RecentBillItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    account_id: int
    amount: float
    due_date: date
    status: str
    created_at: datetime


class RecentPaymentItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    bill_id: int
    amount: float
    payment_method: str
    payment_date: date
    created_at: datetime


class DashboardStatsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total_users: int
    total_accounts: int
    total_meters: int
    total_bills: int
    total_payments: int

    monthly_new_users_count: int
    monthly_new_accounts_count: int
    monthly_new_meters_count: int
    monthly_new_bills_count: int
    monthly_new_payments_count: int

    overdue_bills_count: int
    pending_bills_count: int
    paid_bills_count: int

    total_billed_amount: float
    total_paid_amount: float
    unpaid_total_amount: float
    average_bill_amount: float
    average_payment_amount: float
    monthly_bills_total: float
    monthly_payments_total: float
    fully_paid_percentage: float
    collection_rate: float

    bill_status_counts: Dict[str, int]
    payment_method_counts: Dict[str, int]
    account_type_counts: Dict[str, int]
    meter_type_counts: Dict[str, int]

    latest_bill_status_summary: Optional[LatestBillStatusSummary] = None
    latest_payment_summary: Optional[LatestPaymentSummary] = None
    recent_activity_summary: RecentActivitySummary


class DashboardRecentListsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    recent_users: List[RecentUserItem]
    recent_accounts: List[RecentAccountItem]
    recent_meters: List[RecentMeterItem]
    recent_readings: List[RecentReadingItem]
    recent_bills: List[RecentBillItem]
    recent_payments: List[RecentPaymentItem]


class DashboardTrendItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    month: str
    bills_total: float
    payments_total: float


class DashboardTrendResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    trends: List[DashboardTrendItem]


class DashboardYearlyTrendItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    year: str
    bills_total: float
    payments_total: float


class DashboardYearlyTrendResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    trends: List[DashboardYearlyTrendItem]


class BillStatusTrendItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    month: str
    pending: int
    paid: int
    overdue: int


class BillStatusTrendResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    trends: List[BillStatusTrendItem]


class PaymentMethodTrendItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    month: str
    cash: int
    card: int
    bank_transfer: int


class PaymentMethodTrendResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    trends: List[PaymentMethodTrendItem]


class TopOutstandingAccountItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    account_id: int
    account_number: str
    account_type: str
    balance: float


class TopOutstandingAccountsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    accounts: List[TopOutstandingAccountItem]


class TopUserByAccountsItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    name: str
    email: str
    accounts_count: int


class TopUsersByAccountsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    users: List[TopUserByAccountsItem]


class TopAccountByMetersItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    account_id: int
    account_number: str
    account_type: str
    meters_count: int


class TopAccountsByMetersResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    accounts: List[TopAccountByMetersItem]


class TopMeterByReadingsItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    meter_id: int
    meter_number: str
    meter_type: str
    readings_count: int


class TopMetersByReadingsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    meters: List[TopMeterByReadingsItem]


class TopAccountByBillsItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    account_id: int
    account_number: str
    account_type: str
    bills_count: int


class TopAccountsByBillsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    accounts: List[TopAccountByBillsItem]


class TopUserByBillsItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    name: str
    email: str
    bills_count: int


class TopUsersByBillsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    users: List[TopUserByBillsItem]


class TopAccountByPaymentsItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    account_id: int
    account_number: str
    account_type: str
    payments_count: int


class TopAccountsByPaymentsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    accounts: List[TopAccountByPaymentsItem]


class TopUserByPaymentsItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    name: str
    email: str
    payments_count: int


class TopUsersByPaymentsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    users: List[TopUserByPaymentsItem]


class TopAccountByBilledAmountItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    account_id: int
    account_number: str
    account_type: str
    total_billed_amount: float


class TopAccountsByBilledAmountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    accounts: List[TopAccountByBilledAmountItem]


class TopUserByBilledAmountItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    name: str
    email: str
    total_billed_amount: float


class TopUsersByBilledAmountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    users: List[TopUserByBilledAmountItem]


class TopAccountByPaidAmountItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    account_id: int
    account_number: str
    account_type: str
    total_paid_amount: float


class TopAccountsByPaidAmountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    accounts: List[TopAccountByPaidAmountItem]


class TopUserByPaidAmountItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    name: str
    email: str
    total_paid_amount: float


class TopUsersByPaidAmountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    users: List[TopUserByPaidAmountItem]


class TopUserByMetersItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    name: str
    email: str
    meters_count: int


class TopUsersByMetersResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    users: List[TopUserByMetersItem]


class TopUserByReadingsItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    name: str
    email: str
    readings_count: int


class TopUsersByReadingsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    users: List[TopUserByReadingsItem]


class TopAccountByReadingsItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    account_id: int
    account_number: str
    account_type: str
    readings_count: int


class TopAccountsByReadingsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    accounts: List[TopAccountByReadingsItem]


class TopUserByOutstandingBalanceItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    name: str
    email: str
    total_balance: float


class TopUsersByOutstandingBalanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    users: List[TopUserByOutstandingBalanceItem]


class TopAccountByAverageBillAmountItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    account_id: int
    account_number: str
    account_type: str
    average_bill_amount: float


class TopAccountsByAverageBillAmountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    accounts: List[TopAccountByAverageBillAmountItem]


class TopUserByAverageBillAmountItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    name: str
    email: str
    average_bill_amount: float


class TopUsersByAverageBillAmountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    users: List[TopUserByAverageBillAmountItem]


class TopAccountByAveragePaymentAmountItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    account_id: int
    account_number: str
    account_type: str
    average_payment_amount: float


class TopAccountsByAveragePaymentAmountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    accounts: List[TopAccountByAveragePaymentAmountItem]


class TopUserByAveragePaymentAmountItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    name: str
    email: str
    average_payment_amount: float


class TopUsersByAveragePaymentAmountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    users: List[TopUserByAveragePaymentAmountItem]


class DashboardSummaryResponse(DashboardStatsResponse):
    model_config = ConfigDict(from_attributes=True)

    recent_users: List[RecentUserItem]
    recent_accounts: List[RecentAccountItem]
    recent_meters: List[RecentMeterItem]
    recent_readings: List[RecentReadingItem]
    recent_bills: List[RecentBillItem]
    recent_payments: List[RecentPaymentItem]