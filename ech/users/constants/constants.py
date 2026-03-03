# =========================
# URLS
# =========================

URL_HOME = "home"
URL_LOGIN = "login"
URL_LOGOUT = "logout"
URL_REGISTER = "register"
URL_USER_PROFILE = "user_profile"
URL_SUPER_STAFF = "super_staff"
URL_PAYMENT_STAFF = "payment_staff"
URL_PROCCESS_STAFF = "process_staff"
URL_SUPPORT_STAFF = "support_staff"
URL_LOGIN_REQUIRED = "login_required"
URL_PW_RESET = "pw_reset"
URL_PW_RESET_DONE = "pw_reset_done"
URL_PW_RESET_CONFIRM = "pw_reset_confirm"
URL_PW_RESET_COMPLETE = "pw_reset_complete"

# =========================
# MODELS INPUTS
# =========================

MAX_LENGTH_NAME = 255
MAX_LENGTH_PHONE = 15
MINIMUM_AGE = 18
MAXIMUM_AGE = 95
MAX_LENGTH_ROLE = 30
MAX_LENGTH_ADDRESS = 50
MAX_LENGTH_COUNTRY = 50
MAX_LENGTH_STATE = 50
CORPORATE_EMAIL_DOMAIN = "@company.com"

# =========================
# LABELS INPUTS
# =========================

LABEL_NAME = "Name"
LABEL_PASSWORD = "Password"
LABEL_PASSWORD_CONFIRMATION = "Passoword Confirmation"
LABEL_EMAIL = "Email"
LABEL_AGE = "Age"
LABEL_ROLE = "Role"
LABEL_PHONE = "Phone"
LABEL_COUNTRY = "Country"
LABEL_STATE = "State"
LABEL_ADDRESS = "Address"
LABEL_PROFILE_PHOTO = "Photo"

# =========================
# USER LABELS
# =========================

LABEL_SUPERADM = "SuperADM"
LABEL_SUPER_STAFF = "SuperStaff"
LABEL_PAYMENT_STAFF = "PaymentStaff"
LABEL_PROCCESS_STAFF = "ProcessStaff"
LABEL_SUPPORT_STAFF = "SupportStaff"
LABEL_COMMON_USER = "CommonUser"

# =========================
# TOKEN LABELS
# =========================

LABEL_TOKEN_TYPE_EMAIL_CONFIRMATION = "Email Confirmation"
LABEL_TOKEN_TYPE_PASSWORD_RESET = "Password Reset"
LABEL_TOKEN_TYPE_MAGIC_LOGIN = "Magic Login"
LABEL_TOKEN_TYPE_INVITATION = "Invitation"
LABEL_TOKEN_TYPE_EMAIL_CHANGE = "Email Change"
LABEL_TOKEN_TYPE_2FA = "Two Factor Authentication"

# =========================
# TOKEN EXPIRATION (HOURS)
# =========================

EMAIL_CONFIRMATION_EXPIRATION_HOURS = 24
PASSWORD_RESET_EXPIRATION_HOURS = 2
