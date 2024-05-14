import re

from django.db.models import Q

from .models import Order, LinkedOrder

FILTER_STATUS = {
    'a': Order.Status.APPROVED,
    'r': Order.Status.REJECTED,
    'n': Order.Status.NEW
}


def check_if_item_in_stock(item_quantity, requested_quantity):
    return item_quantity - requested_quantity >= 0


def get_next_order_number():
    """Returns the next available id to create a new Linked Order object"""

    order_number_count = LinkedOrder.objects.values('order_number').distinct().count()
    next_order_number = order_number_count + 1
    return next_order_number


def get_next_position_in_linked_order(order_number):
    """Returns the next available order number to assign an order to a Linked Order object"""

    identical_order_number_count = LinkedOrder.objects.filter(order_number=order_number).count()
    next_position = identical_order_number_count + 1
    return next_position


# FILTERING
def get_min_max_values(filter_value):
    if not filter_value:
        return 'not'
    values_str = ''.join(filter_value)
    values_list = re.findall(r'\d+', values_str)  # finds numbers
    values = [int(value) for value in values_list]
    max_value = max(values)
    min_value = min(values)
    values = f'_{min_value}_{max_value}'
    return values


def get_status_values(filter_value):
    if not filter_value:
        return 'not'
    values = [f'_{status[7]}' for status in filter_value]
    values = ''.join(values)
    return values


def get_filter_values(filtering):
    filter_values_str = filtering[2:-2]  # removes the square bracket and comma
    filter_values = filter_values_str.split("', '")

    price = [value for value in filter_values if 'price' in value]
    price_values = get_min_max_values(price)
    price_values = f'p{price_values}'

    quantity = [value for value in filter_values if 'quantity' in value]
    quantity_values = get_min_max_values(quantity)
    quantity_values = f'q{quantity_values}'

    status = [value for value in filter_values if 'status' in value]
    status_values = get_status_values(status)
    status_values = f's{status_values}'

    filter_values = price_values + ',' + quantity_values + ',' + status_values

    return filter_values


def get_filtered_obj(model, filter_values):
    filter_values = filter_values.split(',')
    price = filter_values[0]
    quantity = filter_values[1]
    status = filter_values[2]
    min_price = 0
    max_price = 9999999
    min_quantity = 0
    max_quantity = 9999999

    if 'not' not in price:
        min_price = int(price.split('_')[1])
        max_price = int(price.split('_')[2])

    if 'not' not in quantity:
        min_quantity = int(quantity.split('_')[1])
        max_quantity = int(quantity.split('_')[2])

    objects = model.objects.filter(
        price_without_VAT__lte=max_price,
        price_without_VAT__gte=min_price,
        quantity__lte=max_quantity,
        quantity__gte=min_quantity
    )

    if 'not' not in status and len(quantity.split('_')) <= 3:
        # if all statuses are on, there is no need to filter by status
        match len(status.split('_')):
            case 2:
                filtered_objects = objects.filter(status=FILTER_STATUS[status.split('_')[1]])
            case 3:
                status_1 = FILTER_STATUS[status.split('_')[1]]
                status_2 = FILTER_STATUS[status.split('_')[2]]
                filtered__objects = objects.filter(Q(status=status_1) | Q(status=status_2))

        return filtered_objects

    filtered_objects = objects

    return filtered_objects
