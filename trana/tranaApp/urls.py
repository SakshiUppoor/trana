from django.urls import path
from . import views

urlpatterns = [
    # path("", views.home, name="home"),
    path("signup/", views.signup, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("", views.usersDashboard, name="users"),
    path("reports/", views.reportsDashboard, name="reports"),
    path("medicines/", views.medicinesDashboard, name="medicines"),
    path("appuser/", views.appuser, name="appuser"),
    path("appuser/condition/", views.reportCondition, name="condition"),
    path("appuser/medicine/", views.orderMedicine, name="medicine"),
    path("notify/<str:UId>", views.notify, name="notify"),
]
