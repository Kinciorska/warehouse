from django.contrib import admin
from django.urls import path

from website.views import HomePageView, RegisterView, LoginView, LogoutView, ItemsView, ItemUpdateView, ItemDeleteView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home', HomePageView.as_view(), name='home'),
    path('register', RegisterView.as_view(), name='register'),
    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('items', ItemsView.as_view(), name='items'),
    path('items/<ordering>', ItemsView.as_view(), name='items_ordered'),
    path('items/<pk>/update/', ItemUpdateView.as_view(), name='update'),
    path('items/<pk>/delete/', ItemDeleteView.as_view(), name='delete'),
]
