from django.urls import path
from .views import signup_view, login_view, home
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('signup/', signup_view, name='signup'),
    path('', login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('home', home, name='home'),  # Home page
]

