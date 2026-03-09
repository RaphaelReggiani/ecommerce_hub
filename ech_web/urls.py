from django.urls import path

from ech_web.users.views import (
    password_reset_views,
)
from ech_web.users.views import auth_views

app_name = "users"

urlpatterns = [
    
    # =========================
    # AUTH
    # =========================
    path("login/", auth_views.login_view, name="login"),
    path("logout/", auth_views.logout_view, name="logout"),

    # =========================
    # REGISTRATION
    # =========================
    path("register/", auth_views.register_view, name="register"),
    path(
        "confirm-email/<str:token>/",
        auth_views.confirm_email_view,
        name="confirm_email",
    ),

    # =========================
    # PROFILE
    # =========================
    path("profile/", auth_views.user_profile_view, name="profile"),

    # =========================
    # STAFF CREATION
    # =========================
    path(
        "staff/create/",
        auth_views.create_staff_user_view,
        name="create_staff_user",
    ),

    # =========================
    # DASHBOARDS
    # =========================
    path(
        "dashboard/customer/",
        auth_views.customer_dashboard,
        name="customer_dashboard",
    ),
    path(
        "dashboard/support/",
        auth_views.support_staff_dashboard,
        name="support_staff_dashboard",
    ),
    path(
        "dashboard/payment/",
        auth_views.payment_staff_dashboard,
        name="payment_staff_dashboard",
    ),
    path(
        "dashboard/operations/",
        auth_views.operations_staff_dashboard,
        name="operations_staff_dashboard",
    ),
    path(
        "dashboard/adm/",
        auth_views.adm_dashboard,
        name="adm_dashboard",
    ),

    # =========================
    # PASSWORD RESET
    # =========================
    path(
        "password-reset/",
        password_reset_views.password_reset_request_view,
        name="password_reset",
    ),
    path(
        "password-reset/<str:token>/",
        password_reset_views.password_reset_confirm_view,
        name="password_reset_confirm",
    ),
]