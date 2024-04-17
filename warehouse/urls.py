from django.contrib import admin
from django.urls import path

from website.views import (HomePageView, RegisterView, LoginView, LogoutView, ItemsView, ItemUpdateView, ItemDeleteView,
                           RequestView, RequestCreateView, RequestUpdateView, RequestRowView, RequestRowUpdateView)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', HomePageView.as_view(), name='home'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('items/', ItemsView.as_view(), name='items'),
    path('items/<ordering>', ItemsView.as_view(), name='items_ordered'),
    path('items/<pk>/update/', ItemUpdateView.as_view(), name='update'),
    path('items/<pk>/delete/', ItemDeleteView.as_view(), name='delete'),
    path('requests/', RequestView.as_view(), name='requests'),
    path('requests/<ordering>', RequestView.as_view(), name='requests_ordered'),
    path('requests/<item_id>/create/', RequestCreateView.as_view(), name='requests_create'),
    path('requests/<pk>/update/', RequestUpdateView.as_view(), name='requests_update'),
    path('request_row/', RequestRowView.as_view(), name='request_row'),
    path('request_row/<pk>/update/', RequestRowUpdateView.as_view(), name='request_row_update'),
]
