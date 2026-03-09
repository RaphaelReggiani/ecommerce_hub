from ech.users.models import CustomUser

ALLOWED_OPERATION_ROLES = {
    CustomUser.ROLE_SUPERADMIN,
    CustomUser.ROLE_ADMIN,
    CustomUser.ROLE_OPERATIONS_STAFF,
}