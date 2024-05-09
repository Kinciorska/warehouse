from django.contrib import admin
from django.urls import path

from website.views import (HomePageView, RegisterView, LoginView, LogoutView, ItemsView, ItemUpdateView, ItemDeleteView,
                           SingleItemView, FilterItemView, OrderView, SingleOrderView, FilterOrderView, OrderCreateView, OrderUpdateView,
                           LinkedOrderView, LinkedOrderUpdateView)

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
    path('items/search/<item_name>', SingleItemView.as_view(), name='item_by_name'),
    path('items/filter/<filtering>', FilterItemView.as_view(), name='items_filtered'),
    path('orders/', OrderView.as_view(), name='orders'),
    path('orders/<ordering>', OrderView.as_view(), name='orders_ordered'),
    path('orders/filter/<filtering>', FilterOrderView.as_view(), name='orders_filtered'),
    path('orders/search/<order_id>', SingleOrderView.as_view(), name='order_by_id'),
    path('orders/<item_id>/create/', OrderCreateView.as_view(), name='orders_create'),
    path('orders/<pk>/update/', OrderUpdateView.as_view(), name='orders_update'),
    path('linked_orders/', LinkedOrderView.as_view(), name='linked_orders'),
    path('linked_orders/<pk>/update/', LinkedOrderUpdateView.as_view(), name='linked_orders_update'),
]
