# ============================
# CACHE KEY PREFIXES
# ============================

REVIEWS_CACHE_PREFIX = "reviews"

REVIEW_DETAIL_CACHE_PREFIX = "review_detail"
CUSTOMER_REVIEW_LIST_CACHE_PREFIX = "customer_review_list"
MANAGEMENT_REVIEW_LIST_CACHE_PREFIX = "management_review_list"
PUBLIC_PRODUCT_REVIEW_LIST_CACHE_PREFIX = "public_product_review_list"
PRODUCT_REVIEW_SUMMARY_CACHE_PREFIX = "product_review_summary"

# ============================
# CACHE VERSION KEY PREFIXES
# ============================

REVIEW_DETAIL_VERSION_PREFIX = "review_detail_version"
CUSTOMER_REVIEW_LIST_VERSION_PREFIX = "customer_review_list_version"
MANAGEMENT_REVIEW_LIST_VERSION_PREFIX = "management_review_list_version"
PUBLIC_PRODUCT_REVIEW_LIST_VERSION_PREFIX = "public_product_review_list_version"
PRODUCT_REVIEW_SUMMARY_VERSION_PREFIX = "product_review_summary_version"

# ============================
# CACHE TTLs (SECONDS)
# ============================

REVIEW_DETAIL_CACHE_TTL = 60 * 10
CUSTOMER_REVIEW_LIST_CACHE_TTL = 60 * 5
MANAGEMENT_REVIEW_LIST_CACHE_TTL = 60 * 5
PUBLIC_PRODUCT_REVIEW_LIST_CACHE_TTL = 60 * 5
PRODUCT_REVIEW_SUMMARY_CACHE_TTL = 60 * 10

# ============================
# CACHE DEFAULTS
# ============================

DEFAULT_CACHE_NAMESPACE_VERSION = 1