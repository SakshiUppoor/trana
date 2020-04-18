from django.urls import path
from . import views

urlpatterns = [
    # path("", views.home, name="home"),
    path("signup/", views.signup, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("users/", views.usersDashboard, name="users"),
    path("reports/", views.reportsDashboard, name="reports"),
    path("medicines/", views.medicinesDashboard, name="medicines"),
]
