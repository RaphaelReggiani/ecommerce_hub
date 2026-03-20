# =================================
# DEFAULT CACHE TIMEOUTS (seconds)
# =================================

# Payment detail (single payment)
PAYMENT_DETAIL_CACHE_TTL = 60 * 5

# Payment lookup by reference
PAYMENT_REFERENCE_CACHE_TTL = 60 * 5

# Customer dashboard (list of payments)
CUSTOMER_PAYMENT_LIST_CACHE_TTL = 60 * 3

# Admin / staff dashboard
MANAGEMENT_PAYMENT_LIST_CACHE_TTL = 60 * 2

# Filters
PAYMENT_STATUS_LIST_CACHE_TTL = 60 * 2
PAYMENT_METHOD_LIST_CACHE_TTL = 60 * 2

# Related resources
PAYMENT_TRANSACTIONS_CACHE_TTL = 60 * 3
PAYMENT_REFUNDS_CACHE_TTL = 60 * 3

# =========================
# CACHE VERSIONING
# =========================

PAYMENTS_CACHE_VERSION = "v1"

# =========================
# CACHE SAFETY LIMITS
# =========================

PAYMENT_CACHE_PAGE_SIZE_LIMIT = 100