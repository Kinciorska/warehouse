from django.contrib import admin
from django.urls import path

from website.views import HomePageView, RegisterView, LoginView, LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home', HomePageView.as_view(), name='home'),
    path('register', RegisterView.as_view(), name='register'),
    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
]
