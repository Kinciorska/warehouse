from .models import RequestRow


def check_if_item_in_stock(item_quantity, requested_quantity):
    return item_quantity - requested_quantity >= 0


def get_next_request_row_request_id():
    request_id_number = RequestRow.objects.values('request_id').distinct().count()
    next_request_row_id = request_id_number + 1
    return next_request_row_id


def get_next_request_row_number(next_request_row_id):
    request_row_number = RequestRow.objects.filter(request_id=next_request_row_id).count()
    next_request_row_number = request_row_number + 1
    return next_request_row_number
