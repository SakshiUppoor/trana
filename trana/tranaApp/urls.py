from django.urls import path
from . import views

path('',views.home,name='home'),
path('login/',views.login_view,name='login'),
#path('logout/',views.logout_view,name='logout'),
path('postlogin/',views.post_login,name='postlogin'),