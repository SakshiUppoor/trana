from django.urls import path
from .views import (
    signup,
    login_view,
    logout_view,
    usersDashboard,
    medicinesDashboard,
    reportsDashboard,
    reportCondition,
    orderMedicine,
    notify,
    resolve,
    page404,
)

urlpatterns = [
    # path("", home, name="home"),
    path("signup/", signup, name="signup"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("", usersDashboard, name="users"),
    path("reports/", reportsDashboard, name="reports"),
    path("medicines/", medicinesDashboard, name="medicines"),
    path("condition/", reportCondition, name="condition"),
    path("medicine/", orderMedicine, name="medicine"),
    path("notify/<str:id>", notify, name="notify"),
    path("resolve/<str:id>", resolve, name="resolve"),
    path("404/", page404, name="404"),
]
