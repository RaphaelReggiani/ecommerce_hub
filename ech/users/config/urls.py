from django.urls import path

from ech.users.views import (
    views, 
    password_reset_views,
)

app_name = "users"

urlpatterns = [
    
    # =========================
    # AUTH
    # =========================
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # =========================
    # REGISTRATION
    # =========================
    path("register/", views.register_view, name="register"),
    path(
        "confirm-email/<str:token>/",
        views.confirm_email_view,
        name="confirm_email",
    ),

    # =========================
    # PROFILE
    # =========================
    path("profile/", views.user_profile_view, name="profile"),

    # =========================
    # STAFF CREATION
    # =========================
    path(
        "staff/create/",
        views.create_staff_user_view,
        name="create_staff_user",
    ),

    # =========================
    # DASHBOARDS
    # =========================
    path(
        "dashboard/customer/",
        views.customer_dashboard,
        name="customer_dashboard",
    ),
    path(
        "dashboard/support/",
        views.support_staff_dashboard,
        name="support_staff_dashboard",
    ),
    path(
        "dashboard/payment/",
        views.payment_staff_dashboard,
        name="payment_staff_dashboard",
    ),
    path(
        "dashboard/operations/",
        views.operations_staff_dashboard,
        name="operations_staff_dashboard",
    ),
    path(
        "dashboard/adm/",
        views.adm_dashboard,
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