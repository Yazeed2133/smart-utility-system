from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.schemas.account import AccountCreate, AccountResponse, AccountUpdate
from app.schemas.meter import MeterCreate, MeterResponse, MeterUpdate
from app.schemas.reading import ReadingCreate, ReadingResponse, ReadingUpdate
from app.schemas.bill import BillCreate, BillResponse, BillUpdate
from app.schemas.payment import PaymentCreate, PaymentResponse, PaymentUpdate
from app.schemas.dashboard import (
    BillStatusTrendItem,
    BillStatusTrendResponse,
    DashboardRecentListsResponse,
    DashboardStatsResponse,
    DashboardSummaryResponse,
    DashboardTrendItem,
    DashboardTrendResponse,
    DashboardYearlyTrendItem,
    DashboardYearlyTrendResponse,
    LatestBillStatusSummary,
    LatestPaymentSummary,
    PaymentMethodTrendItem,
    PaymentMethodTrendResponse,
    RecentAccountItem,
    RecentActivitySummary,
    RecentBillItem,
    RecentMeterItem,
    RecentPaymentItem,
    RecentReadingItem,
    RecentUserItem,
    TopAccountByAverageBillAmountItem,
    TopAccountByAveragePaymentAmountItem,
    TopAccountByBilledAmountItem,
    TopAccountByBillsItem,
    TopAccountByMetersItem,
    TopAccountByPaidAmountItem,
    TopAccountByPaymentsItem,
    TopAccountByReadingsItem,
    TopAccountsByAverageBillAmountResponse,
    TopAccountsByAveragePaymentAmountResponse,
    TopAccountsByBilledAmountResponse,
    TopAccountsByBillsResponse,
    TopAccountsByMetersResponse,
    TopAccountsByPaidAmountResponse,
    TopAccountsByPaymentsResponse,
    TopAccountsByReadingsResponse,
    TopMeterByReadingsItem,
    TopMetersByReadingsResponse,
    TopOutstandingAccountItem,
    TopOutstandingAccountsResponse,
    TopUserByAccountsItem,
    TopUserByAverageBillAmountItem,
    TopUserByAveragePaymentAmountItem,
    TopUserByBilledAmountItem,
    TopUserByBillsItem,
    TopUserByMetersItem,
    TopUserByOutstandingBalanceItem,
    TopUserByPaidAmountItem,
    TopUserByPaymentsItem,
    TopUserByReadingsItem,
    TopUsersByAccountsResponse,
    TopUsersByAverageBillAmountResponse,
    TopUsersByAveragePaymentAmountResponse,
    TopUsersByBilledAmountResponse,
    TopUsersByBillsResponse,
    TopUsersByMetersResponse,
    TopUsersByOutstandingBalanceResponse,
    TopUsersByPaidAmountResponse,
    TopUsersByPaymentsResponse,
    TopUsersByReadingsResponse,
)

__all__ = [
    "MessageResponse",
    "PaginatedResponse",

    "UserCreate",
    "UserResponse",
    "UserUpdate",

    "AccountCreate",
    "AccountResponse",
    "AccountUpdate",

    "MeterCreate",
    "MeterResponse",
    "MeterUpdate",

    "ReadingCreate",
    "ReadingResponse",
    "ReadingUpdate",

    "BillCreate",
    "BillResponse",
    "BillUpdate",

    "PaymentCreate",
    "PaymentResponse",
    "PaymentUpdate",

    "LatestBillStatusSummary",
    "LatestPaymentSummary",
    "RecentActivitySummary",
    "RecentUserItem",
    "RecentAccountItem",
    "RecentMeterItem",
    "RecentReadingItem",
    "RecentBillItem",
    "RecentPaymentItem",

    "DashboardStatsResponse",
    "DashboardRecentListsResponse",
    "DashboardSummaryResponse",

    "DashboardTrendItem",
    "DashboardTrendResponse",
    "DashboardYearlyTrendItem",
    "DashboardYearlyTrendResponse",

    "BillStatusTrendItem",
    "BillStatusTrendResponse",
    "PaymentMethodTrendItem",
    "PaymentMethodTrendResponse",

    "TopOutstandingAccountItem",
    "TopOutstandingAccountsResponse",

    "TopUserByAccountsItem",
    "TopUsersByAccountsResponse",

    "TopAccountByMetersItem",
    "TopAccountsByMetersResponse",

    "TopUserByMetersItem",
    "TopUsersByMetersResponse",

    "TopMeterByReadingsItem",
    "TopMetersByReadingsResponse",

    "TopUserByReadingsItem",
    "TopUsersByReadingsResponse",

    "TopAccountByReadingsItem",
    "TopAccountsByReadingsResponse",

    "TopAccountByBillsItem",
    "TopAccountsByBillsResponse",

    "TopUserByBillsItem",
    "TopUsersByBillsResponse",

    "TopAccountByPaymentsItem",
    "TopAccountsByPaymentsResponse",

    "TopUserByPaymentsItem",
    "TopUsersByPaymentsResponse",

    "TopAccountByBilledAmountItem",
    "TopAccountsByBilledAmountResponse",

    "TopUserByBilledAmountItem",
    "TopUsersByBilledAmountResponse",

    "TopAccountByPaidAmountItem",
    "TopAccountsByPaidAmountResponse",

    "TopUserByPaidAmountItem",
    "TopUsersByPaidAmountResponse",

    "TopUserByOutstandingBalanceItem",
    "TopUsersByOutstandingBalanceResponse",

    "TopAccountByAverageBillAmountItem",
    "TopAccountsByAverageBillAmountResponse",

    "TopUserByAverageBillAmountItem",
    "TopUsersByAverageBillAmountResponse",

    "TopAccountByAveragePaymentAmountItem",
    "TopAccountsByAveragePaymentAmountResponse",

    "TopUserByAveragePaymentAmountItem",
    "TopUsersByAveragePaymentAmountResponse",
]