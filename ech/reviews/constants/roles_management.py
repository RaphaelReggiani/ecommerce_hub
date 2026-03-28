from ech.users.models import CustomUser

ALLOWED_REVIEWS_ROLES = {
    CustomUser.ROLE_SUPERADMIN,
    CustomUser.ROLE_ADMIN,
    CustomUser.ROLE_SUPPORT_STAFF,
}