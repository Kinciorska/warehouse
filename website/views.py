import re

from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.http import Http404
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView

from .forms import (NewUserForm, ItemForm, RequestStatusForm, RequestForm, RequestForRequestRowForm, SearchRequestForm,
                    FilterRequestForm)
from .models import Items, Requests, RequestRow
from .utils import FILTER_STATUS, check_if_item_in_stock, get_next_request_row_request_id, get_next_request_row_number


class HomePageView(TemplateView):
    template_name = 'website/home.html'


class RegisterView(View):
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

    def get(self, request):
        logout(request)
        messages.info(request, "You have successfully logged out.")
        return redirect("home")


class ItemsView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'website.view_items'
    template_name = 'website/items.html'
    paginate_by = 20
    model = Items
    item_form_class = ItemForm
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
            'create_item_form': self.item_form_class}

        return render(request, self.template_name, context)

    def post(self, request, **ordering):
        form = self.item_form_class(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Item added successfully")
            page_obj = self.get_page_obj(request, **ordering)
            context = {
                'page_obj': page_obj,
                'create_item_form': self.item_form_class}

            return render(request, self.template_name, context)

        else:
            messages.error(request, "Item not added")
            page_obj = self.get_page_obj(request, **ordering)
            context = {
                'page_obj': page_obj,
                'create_item_form': self.item_form_class}

            return render(request, self.template_name, context)


class ItemUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'website.change_items'
    model = Items
    success_url = '/items'
    fields = ['item_name', 'item_group', 'unit_of_measurement', 'quantity', 'price_without_VAT', 'status',
              'storage_location', 'contact_person', 'photo']
    template_name_suffix = '_update_form'


class ItemDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'website.delete_items'
    model = Items
    success_url = '/items'
    template_name_suffix = '_confirm_delete'


class RequestView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = ['website.view_requests', 'website.change_requests']
    template_name = 'website/requests.html'
    paginate_by = 20
    model = Requests
    form_class = SearchRequestForm
    order_by = 'item_id'

    def get_page_obj(self, request, **ordering):
        requests_list = self.model.objects.all()
        if ordering:
            self.order_by = ordering['ordering']
        ordered_requests_list = requests_list.order_by(self.order_by)
        paginator = Paginator(ordered_requests_list, self.paginate_by)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        return page_obj

    def get(self, request, **ordering):
        page_obj = self.get_page_obj(request, **ordering)
        context = {'page_obj': page_obj,
                   'search_form': self.form_class,
                   'filter_form': FilterRequestForm}
        return render(request, self.template_name, context)

    def post(self, request, **parameters):
        data = request.POST
        search_form = SearchRequestForm(data)
        filter_form = FilterRequestForm(data)

        if 'search' in data and search_form.is_valid():
            cleaned_data = search_form.cleaned_data
            request_id = cleaned_data['request_id']
            return redirect('request_by_id', request_id)

        if 'filter' in data and filter_form.is_valid and len(data) > 2:  # if there are only 2 params, no filter is applied
            filter_values = [parameter for parameter, value in data.items() if value == 'on']
            return redirect('requests_filtered', filter_values)

        else:
            messages.error(request, "Invalid input. Please make sure your search or filter criteria are correct "
                                    "and try again")
            page_obj = self.get_page_obj(request, **parameters)
            context = {
                'page_obj': page_obj,
                'search_form': self.form_class}
            return render(request, self.template_name, context)


class SingleRequestView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = ['website.view_requests', 'website.change_requests']
    template_name = 'website/requests_single.html'
    model = Requests
    form_class = SearchRequestForm

    def get(self, request, **request_id):
        request_id = request_id['request_id']
        try:
            request_object = get_object_or_404(self.model.objects, request_id=request_id)
            context = {'request_object': request_object}
            return render(request, self.template_name, context)
        except Http404:
            messages.error(request, "There is no such request")
            return redirect('requests')


class FilterRequestView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = ['website.view_requests', 'website.change_requests']
    template_name = 'website/requests_filter.html'
    paginate_by = 20
    model = Requests
    form_class = SearchRequestForm
    order_by = 'item_id'

    def get_filtered_obj(self, filter_values):
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

        requests_objects = self.model.objects.filter(
            price_without_VAT__lte=max_price,
            price_without_VAT__gte=min_price,
            quantity__lte=max_quantity,
            quantity__gte=min_quantity
        )

        if 'not' not in status and len(quantity.split('_')) <= 3:
            # if all statuses are on, there is no need to filter by status
            match len(status.split('_')):
                case 2:
                    filtered_requests_objects = requests_objects.filter(status=FILTER_STATUS[status.split('_')[1]])
                case 3:
                    status_1 = FILTER_STATUS[status.split('_')[1]]
                    status_2 = FILTER_STATUS[status.split('_')[2]]
                    filtered_requests_objects = requests_objects.filter(Q(status=status_1) | Q(status=status_2))

            return filtered_requests_objects

        filtered_requests_objects = requests_objects

        return filtered_requests_objects

    def get_page_obj(self, request, filter_values):
        filtered_requests_objects = self.get_filtered_obj(filter_values)
        ordered_requests_list = filtered_requests_objects.order_by(self.order_by)
        paginator = Paginator(ordered_requests_list, self.paginate_by)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        return page_obj

    @staticmethod
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

    @staticmethod
    def get_status_values(filter_value):
        if not filter_value:
            return 'not'
        values = [f'_{status[7]}' for status in filter_value]
        values = ''.join(values)
        return values

    def get_filter_values(self, filtering):
        filter_values_str = filtering[2:-2]  # removes the square bracket and comma
        filter_values = filter_values_str.split("', '")

        price = [value for value in filter_values if 'price' in value]
        price_values = self.get_min_max_values(price)
        price_values = f'p{price_values}'

        quantity = [value for value in filter_values if 'quantity' in value]
        quantity_values = self.get_min_max_values(quantity)
        quantity_values = f'q{quantity_values}'

        status = [value for value in filter_values if 'status' in value]
        status_values = self.get_status_values(status)
        status_values = f's{status_values}'

        filter_values = price_values + ',' + quantity_values + ',' + status_values

        return filter_values

    def get(self, request, filtering):
        filter_values = self.get_filter_values(filtering)
        page_obj = self.get_page_obj(request, filter_values)
        context = {'page_obj': page_obj,
                   'search_form': self.form_class}
        return render(request, self.template_name, context)


class RequestCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'website.add_requests'
    model = Requests
    success_url = '/items'
    form_class = RequestForm
    template_name = 'website/requests_create_form.html'

    def get(self, request, item_id):
        context = {
            'item_id': item_id,
            'request_row_form': RequestForRequestRowForm,
            'form': self.form_class}
        return render(request, self.template_name, context)

    @transaction.atomic
    def crate_new_request_row(self, request, selected_request_id, request_row_request_id):
        request_object = Requests.objects.get(request_id=selected_request_id)

        try:
            with transaction.atomic():
                new_request_row_object = RequestRow(
                    request_id=request_row_request_id,
                    request_row=1,
                    item_id=getattr(request_object, 'item_id'),
                    unit_of_measurement=getattr(request_object, 'unit_of_measurement'),
                    quantity=getattr(request_object, 'quantity'),
                    price_without_VAT=getattr(request_object, 'price_without_VAT'),
                    comment=getattr(request_object, 'comment'),
                    status=getattr(request_object, 'status')
                )
                new_request_row_object.save()
                request_object.delete()
        except IntegrityError:
            messages.error(request, "Error adding to RequestsRow")
            return IntegrityError

    def add_to_request_row(self, request_row_request_id, new_request_data):
        request_row = get_next_request_row_number(request_row_request_id)
        RequestRow.objects.create(
            request_id=request_row_request_id,
            request_row=request_row,
            item_id=new_request_data['item_id'],
            unit_of_measurement=new_request_data['unit_of_measurement'],
            quantity=new_request_data['quantity'],
            price_without_VAT=new_request_data['price_without_vat'],
            comment=new_request_data['comment'],
            status=new_request_data['status']
        )

    def post(self, request, *args, **kwargs):
        data = request.POST
        if RequestForm(data).is_valid():
            item_id = int(data['item_id'])
            quantity = int(data['quantity'])
            item_price = getattr(Items.objects.get(item_id=item_id), 'price_without_VAT')
            new_request_data = {
                'employee_name': request.user,
                'item_id': Items.objects.get(item_id=item_id),
                'unit_of_measurement': data['unit_of_measurement'],
                'quantity': quantity,
                'price_without_vat': quantity * item_price,
                'comment': data['comment'],
                'status': self.model.Status.NEW,
            }
            if 'add_to_request' in data:  # checks if the user wanted to add a new request or add it to request row
                next_request_row_request_id = get_next_request_row_request_id()

                if not data['requests']:  # implies that there is no request row object yet, it should be created
                    selected_request_id = int(data['request'])
                    request_row_request_id = next_request_row_request_id
                    try:
                        self.crate_new_request_row(request, selected_request_id, request_row_request_id)
                        self.add_to_request_row(request_row_request_id, new_request_data)
                        messages.success(request, "Request updated")
                        return redirect(self.success_url)
                    except IntegrityError:
                        messages.error(request, "Error adding to Requests Row, contact the administrator")

                if not data['request']:  # implies that there is a request row object to be connected to
                    selected_request_row_id = int(data['requests'])
                    request_row_request_id = getattr(RequestRow.objects.get(request_row_id=selected_request_row_id),
                                                     'request_id')
                    self.add_to_request_row(request_row_request_id, new_request_data)
                    messages.success(request, "Request updated")
                    return redirect(self.success_url)
                else:
                    messages.error(request, "You didn't chose a request to add to.")
                    context = {
                        'item_id': item_id,
                        'request_row_form': RequestForRequestRowForm,
                        'form': self.form_class}
                    return render(request, self.template_name, context)

            if 'add_to_request' not in data:
                self.model.objects.create(
                    item_id=new_request_data['item_id'],
                    employee_name=new_request_data['employee_name'],
                    unit_of_measurement=new_request_data['unit_of_measurement'],
                    quantity=new_request_data['quantity'],
                    price_without_VAT=new_request_data['price_without_vat'],
                    comment=new_request_data['comment'],
                    status=new_request_data['status']
                )
                return redirect(self.success_url)

            else:
                messages.error(request, "Failed to create request. Please check your input and try again.")
                context = {
                    'item_id': item_id,
                    'request_row_form': RequestForRequestRowForm,
                    'form': self.form_class}
                return render(request, self.template_name, context)


def update_status(status, request_object, request_model):
    match status:
        case 'apr':
            item_object = request_object.item_id
            item_object_previous_quantity = getattr(item_object, 'quantity')
            request_object_item_quantity = getattr(request_object, 'quantity')
            if check_if_item_in_stock(item_object_previous_quantity, request_object_item_quantity):
                request_object.status = request_model.Status.APPROVED
                request_object.save(update_fields=['status'])
                current_item_object_quantity = item_object_previous_quantity - request_object_item_quantity
                item_object.quantity = current_item_object_quantity
                item_object.save(update_fields=['quantity'])
            else:
                raise ValidationError(_("Not enough item to complete this order"))
        case 'rej':
            request_object.status = request_model.Status.REJECTED
            request_object.save(update_fields=['status'])

        case 'new':
            request_object.status = request_model.Status.NEW
            request_object.save(update_fields=['status'])


class RequestUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'website.change_requests'
    model = Requests
    form_class = RequestStatusForm
    success_url = '/requests'
    template_name = 'website/requests_update_form.html'

    def get(self, request, pk):
        request_object = Requests.objects.get(request_id=pk)
        context = {
            'request_object': request_object,
            'request_id': pk,
            'form': self.form_class}
        return render(request, self.template_name, context)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        data = request.POST
        status = data['status']
        request_id = int(data['request_id'])
        request_object = self.model.objects.get(request_id=request_id)

        try:
            with transaction.atomic():
                update_status(status, request_object, self.model)

                return redirect(self.success_url)

        except ValidationError:
            messages.error(request, "There is not enough items in stock to complete this order")

            request_object = self.model.objects.get(request_id=int(data['request_id']))
            context = {
                'request_object': request_object,
                'request_id': data['request_id'],
                'form': self.form_class}

            return render(request, self.template_name, context)


class RequestRowView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = ['website.view_requestrow', 'website.change_requestrow']
    template_name = 'website/request_row.html'
    paginate_by = 20
    model = RequestRow


class RequestRowUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'website.change_requestrow'
    model = RequestRow
    form_class = RequestStatusForm
    success_url = '/request_row'
    template_name = 'website/request_row_update_form.html'

    def get(self, request, pk):
        first_request_row_object = self.model.objects.get(request_id=pk, request_row=1)
        request_objects = self.model.objects.filter(request_id=pk)
        context = {
            'request_row_object': first_request_row_object,
            'request_row_objects': request_objects,
            'request_id': pk,
            'form': self.form_class}
        return render(request, self.template_name, context)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        data = request.POST
        status = data['status']
        request_row_request_id = int(data['request_id'])
        number_of_request_in_request_row = self.model.objects.filter(request_id=request_row_request_id).count()
        try:
            with transaction.atomic():

                for number in range(1, number_of_request_in_request_row + 1):
                    request_row_object = self.model.objects.get(request_id=request_row_request_id, request_row=number)
                    update_status(status, request_row_object, self.model)

                return redirect(self.success_url)

        except ValidationError:
            messages.error(request, "There is not enough items in stock to complete this order")
            first_request_row_object = self.model.objects.get(request_id=int(data['request_id']), request_row=1)
            request_objects = RequestRow.objects.filter(request_id=int(data['request_id']))
            context = {
                'request_row_object': first_request_row_object,
                'request_row_objects': request_objects,
                'request_id': int(data['request_id']),
                'form': self.form_class}

            return render(request, self.template_name, context)
