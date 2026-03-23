from ech.users.models import CustomUser

ALLOWED_SHIPPING_ROLES = {
    CustomUser.ROLE_SUPERADMIN,
    CustomUser.ROLE_ADMIN,
    CustomUser.ROLE_OPERATIONS_STAFF,
    CustomUser.ROLE_SUPPORT_STAFF,
}