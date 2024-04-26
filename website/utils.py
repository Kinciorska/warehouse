from .models import Order, LinkedOrder

FILTER_STATUS = {
    'a': Order.Status.APPROVED,
    'r': Order.Status.REJECTED,
    'n': Order.Status.NEW
}


def check_if_item_in_stock(item_quantity, requested_quantity):
    return item_quantity - requested_quantity >= 0


def get_next_order_number():
    order_number_count = LinkedOrder.objects.values('order_number').distinct().count()
    next_order_number = order_number_count + 1
    return next_order_number


def get_next_position_in_linked_order(order_number):
    identical_order_number_count = LinkedOrder.objects.filter(order_number=order_number).count()
    next_position = identical_order_number_count + 1
    return next_position
