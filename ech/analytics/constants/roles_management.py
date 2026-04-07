from ech.users.models import CustomUser

ALLOWED_ANALYTICS_ROLES = {
    CustomUser.ROLE_SUPERADMIN,
    CustomUser.ROLE_ADMIN,
    CustomUser.ROLE_ANALYTICS_STAFF,
}