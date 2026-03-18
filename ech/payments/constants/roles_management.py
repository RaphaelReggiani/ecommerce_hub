from ech.users.models import CustomUser

ALLOWED_PAYMENT_ROLES = {
    CustomUser.ROLE_SUPERADMIN,
    CustomUser.ROLE_ADMIN,
    CustomUser.ROLE_PAYMENT_STAFF,
}