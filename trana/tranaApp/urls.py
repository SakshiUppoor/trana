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
    path("condition/", views.reportCondition, name="condition"),
    path("medicine/", views.orderMedicine, name="medicine"),
    path("notify/<str:id>", views.notify, name="notify"),
    path("resolve/<str:id>", views.resolve, name="resolve"),
    path("404/", views.page404, name="404"),
]
