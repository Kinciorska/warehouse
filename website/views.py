from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.http import Http404
from django.db import IntegrityError, transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView

from .forms import (NewUserForm, ItemForm, SearchItemForm, FilterItemForm, OrderStatusForm, OrderForm,
                    OrderForLinkedOrderForm, LinkedOrderStatusForm, SearchOrderForm, FilterOrderForm)
from .models import Item, Order, LinkedOrder
from .utils import (check_if_item_in_stock, get_next_order_number, get_next_position_in_linked_order,
                    get_filter_values, get_filtered_obj)


class HomePageView(TemplateView):
    """View class displaying the home page of the application."""

    template_name = 'website/home.html'


class RegisterView(View):
    """View class allowing user registration."""

    template_name = 'website/register.html'
    form_class = NewUserForm

    def get(self, request):
        form = self.form_class
        context = {"form": form}
        return render(request, self.template_name, context)

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect("home")
        else:
            messages.error(request, "Unsuccessful registration - invalid information.")
            context = {"form": form}
            return render(request, self.template_name, context)


class LoginView(View):
    """View class allowing user log in."""

    template_name = 'website/login.html'
    form_class = AuthenticationForm

    def get(self, request):
        form = self.form_class
        context = {"form": form}
        return render(request, self.template_name, context)

    def post(self, request):
        form = self.form_class(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is None:
                messages.error(request, "Invalid username or password")
            else:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("home")
        else:
            messages.error(request, "Invalid username or password")
            context = {"form": form}
            return render(request, self.template_name, context)


class LogoutView(View):
    """View class allowing user log out."""

    def get(self, request):
        logout(request)
        messages.info(request, "You have successfully logged out.")
        return redirect("home")


class ItemsView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """View class displaying all Items, paginated by 20 per page."""

    permission_required = 'website.view_item'
    template_name = 'website/item.html'
    paginate_by = 20
    model = Item
    form_class = SearchItemForm
    item_form_class = ItemForm
    filter_class = FilterItemForm
    order_by = 'item_name'

    def get_page_obj(self, request, **ordering):
        items_list = self.model.objects.all()
        if ordering:
            self.order_by = ordering['ordering']
        ordered_items_list = items_list.order_by(self.order_by)
        paginator = Paginator(ordered_items_list, self.paginate_by)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        return page_obj

    def get(self, request, **ordering):
        page_obj = self.get_page_obj(request, **ordering)
        context = {
            'page_obj': page_obj,
            'create_item_form': self.item_form_class,
            'search_form': self.form_class,
            'filter_form': self.filter_class}

        return render(request, self.template_name, context)

    def post(self, request, **parameters):
        """
            Depending on the form name in the POST data, it redirects to a searched Item, returns filtered Items, or
            creates a new Item object.
        """
        data = request.POST
        add_item_form = self.item_form_class(data)
        search_form = self.form_class(data)
        filter_form = FilterItemForm

        if 'searched_item_name' in data and search_form.is_valid():
            cleaned_data = search_form.cleaned_data
            item_name = cleaned_data['searched_item_name']
            return redirect('item_by_name', item_name)

        if 'filter' in data and filter_form.is_valid and len(
                data) > 2:  # if there are only 2 params, no filter is applied
            filter_values = [parameter for parameter, value in data.items() if value == 'on']
            return redirect('items_filtered', filter_values)

        if 'item_name' in data and add_item_form.is_valid():
            add_item_form.save()
            messages.success(request, "Item added successfully")
            page_obj = self.get_page_obj(request, **parameters)
            context = {
                'page_obj': page_obj,
                'create_item_form': self.item_form_class,
                'search_form': self.form_class}

            return render(request, self.template_name, context)

        else:
            messages.error(request, "Item not added")
            page_obj = self.get_page_obj(request, **parameters)
            context = {
                'page_obj': page_obj,
                'create_item_form': self.item_form_class}

            return render(request, self.template_name, context)


class ItemUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """View class allowing coordinators update the Item quantity and information."""

    permission_required = 'website.change_item'
    model = Item
    success_url = '/items'
    fields = ['item_name', 'item_group', 'unit_of_measurement', 'quantity', 'price_without_VAT', 'status',
              'storage_location', 'contact_person', 'photo']
    template_name_suffix = '_update_form'


class ItemDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """View class allowing coordinators to delete a specified Item."""

    permission_required = 'website.delete_items'
    model = Item
    success_url = '/items'
    template_name_suffix = '_confirm_delete'


class SingleItemView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """View class displaying only one Item."""

    permission_required = 'website.view_item'
    template_name = 'website/item_single.html'
    model = Item

    def get(self, request, **item_name):
        item_name = item_name['item_name']
        try:
            item_object = get_object_or_404(self.model.objects, item_name=item_name)
            context = {'item_object': item_object}
            return render(request, self.template_name, context)
        except Http404:
            messages.error(request, "There is no such item")
            return redirect('items')


class FilterItemView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """View class which returns Items filtered by values specified by the user."""

    permission_required = 'website.view_item'
    template_name = 'website/item_filter.html'
    paginate_by = 20
    model = Item
    form_class = SearchItemForm
    order_by = 'item_id'

    def get_page_obj(self, request, filter_values):
        filtered_objects = get_filtered_obj(self.model, filter_values)
        ordered_object_list = filtered_objects.order_by(self.order_by)
        paginator = Paginator(ordered_object_list, self.paginate_by)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        return page_obj

    def get(self, request, filtering):
        filter_values = get_filter_values(filtering)
        page_obj = self.get_page_obj(request, filter_values)
        context = {'page_obj': page_obj,
                   'search_form': self.form_class}
        return render(request, self.template_name, context)

    def post(self, request):
        data = request.POST
        search_form = self.form_class(data)

        if search_form.is_valid():
            cleaned_data = search_form.cleaned_data
            item_name = cleaned_data['searched_item_name']
            return redirect('item_by_name', item_name)

        else:
            messages.error(request, "Something went wrong")
            return redirect('items')


class OrderView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """View class displaying all Orders, paginated by 20 per page."""

    permission_required = ['website.view_order', 'website.change_order']
    template_name = 'website/order.html'
    paginate_by = 20
    model = Order
    form_class = SearchOrderForm
    order_by = 'item_id'

    def get_page_obj(self, request, **ordering):
        order_list = self.model.objects.all()
        if ordering:
            self.order_by = ordering['ordering']
        ordered_order_list = order_list.order_by(self.order_by)
        paginator = Paginator(ordered_order_list, self.paginate_by)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        return page_obj

    def get(self, request, **ordering):
        page_obj = self.get_page_obj(request, **ordering)
        context = {'page_obj': page_obj,
                   'search_form': self.form_class,
                   'filter_form': FilterOrderForm}
        return render(request, self.template_name, context)

    def post(self, request, **parameters):
        """ Depending on the form name in the POST data, it redirects to a searched Order or returns filtered Orders."""
        data = request.POST
        search_form = SearchOrderForm(data)
        filter_form = FilterOrderForm(data)

        if 'search' in data and search_form.is_valid():
            cleaned_data = search_form.cleaned_data
            order_id = cleaned_data['order_id']
            return redirect('order_by_id', order_id)

        if 'filter' in data and filter_form.is_valid and len(data) > 2:
            # if there are only 2 params, no filter is applied
            filter_values = [parameter for parameter, value in data.items() if value == 'on']
            return redirect('orders_filtered', filter_values)

        else:
            messages.error(request, "Invalid input. Please make sure your search or filter criteria are correct "
                                    "and try again")
            page_obj = self.get_page_obj(request, **parameters)
            context = {
                'page_obj': page_obj,
                'search_form': self.form_class}
            return render(request, self.template_name, context)


class SingleOrderView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """View class displaying only one Order."""

    permission_required = ['website.view_order', 'website.change_order']
    template_name = 'website/order_single.html'
    model = Order

    def get(self, request, **order_id):
        order_id = order_id['order_id']
        try:
            order_object = get_object_or_404(self.model.objects, order_id=order_id)
            context = {'order_object': order_object}
            return render(request, self.template_name, context)
        except Http404:
            messages.error(request, "There is no such order")
            return redirect('orders')


class FilterOrderView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """View class which returns Orders filtered by values specified by the user."""

    permission_required = ['website.view_order', 'website.change_order']
    template_name = 'website/order_filter.html'
    paginate_by = 20
    model = Order
    form_class = SearchOrderForm
    order_by = 'item_id'

    def get_page_obj(self, request, filter_values):
        filtered_objects = get_filtered_obj(self.model, filter_values)
        ordered_object_list = filtered_objects.order_by(self.order_by)
        paginator = Paginator(ordered_object_list, self.paginate_by)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        return page_obj

    def get(self, request, filtering):
        filter_values = get_filter_values(filtering)
        page_obj = self.get_page_obj(request, filter_values)
        context = {'page_obj': page_obj,
                   'search_form': self.form_class}
        return render(request, self.template_name, context)

    def post(self, request):
        data = request.POST
        search_form = self.form_class(data)

        if search_form.is_valid():
            cleaned_data = search_form.cleaned_data
            order_id = cleaned_data['order_id']
            return redirect('order_by_id', order_id)

        else:
            messages.error(request, "Something went wrong")
            return redirect('orders')


class OrderCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """View class allowing employees creation of Orders."""

    permission_required = 'website.add_order'
    model = Order
    success_url = '/items'
    form_class = OrderForm
    template_name = 'website/order_create_form.html'

    def get(self, request, item_id):
        context = {
            'item_id': item_id,
            'linked_order_form': OrderForLinkedOrderForm,
            'form': self.form_class}
        return render(request, self.template_name, context)

    @transaction.atomic
    def create_new_linked_order(self, request, selected_order_id, order_number):

        order_object = self.model.objects.get(order_id=selected_order_id)

        try:
            with transaction.atomic():
                new_linked_order_object = LinkedOrder(
                    order_number=order_number,
                    position=1,
                    item_id=getattr(order_object, 'item_id'),
                    unit_of_measurement=getattr(order_object, 'unit_of_measurement'),
                    quantity=getattr(order_object, 'quantity'),
                    price_without_VAT=getattr(order_object, 'price_without_VAT'),
                    comment=getattr(order_object, 'comment'),
                    status=getattr(order_object, 'status')
                )
                new_linked_order_object.save()
                order_object.delete()
        except IntegrityError:
            messages.error(request, "Error connecting the orders")
            return IntegrityError

    @staticmethod
    def add_to_linked_order(order_number, new_order_data):
        next_position = get_next_position_in_linked_order(order_number)
        LinkedOrder.objects.create(
            order_number=order_number,
            position=next_position,
            item_id=new_order_data['item_id'],
            unit_of_measurement=new_order_data['unit_of_measurement'],
            quantity=new_order_data['quantity'],
            price_without_VAT=new_order_data['price_without_vat'],
            comment=new_order_data['comment'],
            status=new_order_data['status']
        )

    def post(self, request, *args, **kwargs):
        """
        Depending on the user's choice, either creates a new linked order object and assigns the selected order to it,
        or assigns it to a selected, previously created linked order object. Note that during this process the Order
        object is deleted and recreated as a Linked Order object.
         """

        data = request.POST
        if OrderForm(data).is_valid():
            item_id = int(data['item_id'])
            quantity = int(data['quantity'])
            item_price = getattr(Item.objects.get(item_id=item_id), 'price_without_VAT')
            new_order_data = {
                'employee_name': request.user,
                'item_id': Item.objects.get(item_id=item_id),
                'unit_of_measurement': data['unit_of_measurement'],
                'quantity': quantity,
                'price_without_vat': quantity * item_price,
                'comment': data['comment'],
                'status': self.model.Status.NEW,
            }
            if 'add_to_order' in data:  # checks if the user wanted to add a new order or add it to linked orders
                next_order_number = get_next_order_number()

                if not data['linked_order']:  # implies that there is no linked order object yet, it should be created
                    selected_order_id = int(data['order'])
                    order_number = next_order_number
                    try:
                        self.create_new_linked_order(request, selected_order_id, order_number)
                        self.add_to_linked_order(order_number, new_order_data)
                        messages.success(request, "Order updated")
                        return redirect(self.success_url)
                    except IntegrityError:
                        messages.error(request, "Error combining the orders, contact the administrator")

                if not data['order']:  # implies that there is a linked order object to be connected to
                    selected_linked_order_id = int(data['linked_order'])
                    order_number = getattr(LinkedOrder.objects.get(linked_order_id=selected_linked_order_id),
                                           'order_number')
                    self.add_to_linked_order(order_number, new_order_data)
                    messages.success(request, "Order updated")
                    return redirect(self.success_url)
                else:
                    messages.error(request, "You didn't chose a request to add to.")
                    context = {
                        'item_id': item_id,
                        'linked_order_form': OrderForLinkedOrderForm,
                        'form': self.form_class}
                    return render(request, self.template_name, context)

            if 'add_to_order' not in data:

                self.model.objects.create(
                    item_id=new_order_data['item_id'],
                    employee_name=new_order_data['employee_name'],
                    unit_of_measurement=new_order_data['unit_of_measurement'],
                    quantity=new_order_data['quantity'],
                    price_without_VAT=new_order_data['price_without_vat'],
                    comment=new_order_data['comment'],
                    status=new_order_data['status']
                )
                return redirect(self.success_url)

            else:
                messages.error(request, "Failed to create order. Please check your input and try again.")
                context = {
                    'item_id': item_id,
                    'linked_order_form': OrderForLinkedOrderForm,
                    'form': self.form_class}
                return render(request, self.template_name, context)


def update_status(status, order_object, order_model):
    """
    A function which allows the change of the Order/Linked Orders status. The possible statuses are: New, Accepted,
    Rejected. After accepting an order, the quantity of the ordered item/s is subtracted from the overall quantity.
    """

    match status:
        case 'apr':
            item_object = order_object.item_id
            item_object_previous_quantity = getattr(item_object, 'quantity')
            order_object_item_quantity = getattr(order_object, 'quantity')
            if check_if_item_in_stock(item_object_previous_quantity, order_object_item_quantity):
                order_object.status = order_model.Status.APPROVED
                order_object.save(update_fields=['status'])
                current_item_object_quantity = item_object_previous_quantity - order_object_item_quantity
                item_object.quantity = current_item_object_quantity
                item_object.save(update_fields=['quantity'])
            else:
                raise ValidationError(_("Not enough item to complete this order"))
        case 'rej':
            order_object.status = order_model.Status.REJECTED
            order_object.save(update_fields=['status'])

        case 'new':
            order_object.status = order_model.Status.NEW
            order_object.save(update_fields=['status'])


class OrderUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    View class allowing coordinators to update the Order status and information. Upon accepting an order, there is a
    custom validation which checks if there is enough items in stock to complete this order.
    """

    permission_required = 'website.change_order'
    model = Order
    form_class = OrderStatusForm
    success_url = '/orders'
    template_name = 'website/order_update_form.html'

    def get(self, request, pk):
        order_object = self.model.objects.get(order_id=pk)
        context = {
            'order_object': order_object,
            'order_id': pk,
            'form': self.form_class}
        return render(request, self.template_name, context)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        data = request.POST
        status = data['status']
        order_id = int(data['order_id'])
        order_object = self.model.objects.get(order_id=order_id)

        try:
            with transaction.atomic():
                update_status(status, order_object, self.model)

                return redirect(self.success_url)

        except ValidationError:
            messages.error(request, "There is not enough items in stock to complete this order")

            order_object = self.model.objects.get(order_id=int(data['order_id']))
            context = {
                'order_object': order_object,
                'order_id': data['order_id'],
                'form': self.form_class}

            return render(request, self.template_name, context)


class LinkedOrderView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """View class displaying all Linked Orders, paginated by 20 per page."""

    permission_required = ['website.view_linkedorder', 'website.change_linkedorder']
    template_name = 'website/linked_order.html'
    paginate_by = 20
    model = LinkedOrder


class LinkedOrderUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    View class allowing coordinators to update the Linked Order status and information. Upon accepting an order, there
    is a custom validation which checks if there is enough items in stock for each of the linked orders to be completed.
    """
    permission_required = 'website.change_linkedorder'
    model = LinkedOrder
    form_class = LinkedOrderStatusForm
    success_url = '/linked_orders'
    template_name = 'website/linked_order_update_form.html'

    def get(self, request, pk):
        first_linked_order_object = self.model.objects.get(order_number=pk, position=1)
        order_objects = self.model.objects.filter(order_number=pk)
        context = {
            'linked_order_object': first_linked_order_object,
            'linked_order_objects': order_objects,
            'order_number': pk,
            'form': self.form_class}

        return render(request, self.template_name, context)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        data = request.POST
        status = data['status']
        comment = data['comment']
        order_number = int(data['order_number'])
        orders_in_linked_order_count = self.model.objects.filter(order_number=order_number).count()
        try:
            with transaction.atomic():

                for number in range(1, orders_in_linked_order_count + 1):
                    linked_order_object = self.model.objects.get(order_number=order_number, position=number)
                    update_status(status, linked_order_object, self.model)
                    linked_order_object.comment = comment
                    linked_order_object.save(update_fields=['comment'])

                return redirect(self.success_url)

        except ValidationError:
            messages.error(request, "There is not enough items in stock to complete this order")
            first_linked_order_object = self.model.objects.get(order_number=order_number, position=1)
            order_objects = self.model.objects.filter(order_number=order_number)
            context = {
                'linked_order_object': first_linked_order_object,
                'linked_order_objects': order_objects,
                'order_number': order_number,
                'form': self.form_class}

            return render(request, self.template_name, context)
