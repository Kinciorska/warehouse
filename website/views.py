from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.paginator import Paginator
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from .forms import NewUserForm, ItemForm, RequestStatusForm, RequestForm
from .models import Items, Requests
from .utils import check_if_item_in_stock


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
    form_class = RequestStatusForm
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
        context = {
            'page_obj': page_obj,
            'create_form': self.form_class}
        return render(request, self.template_name, context)

    def post(self, request, **ordering):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Item added successfully")
            page_obj = self.get_page_obj(request, **ordering)
            context = {
                'page_obj': page_obj,
                'update_form': form}
            return render(request, self.template_name, context)

        else:
            messages.error(request, "Status not changed")
            page_obj = self.get_page_obj(request, **ordering)
            context = {
                'page_obj': page_obj,
                'update_form': form}
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
            'form': self.form_class}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        data = request.POST

        if RequestForm(data).is_valid():
            item_id = int(data['item_id'])
            item_price = getattr(Items.objects.get(item_id=item_id), 'price_without_VAT')
            employee_name = request.user
            item_id = Items.objects.get(item_id=item_id)
            unit_of_measurement = data['unit_of_measurement']
            quantity = int(data['quantity'])
            price_without_vat = quantity * item_price
            comment = data['comment']
            status = self.model.Status.NEW
            Requests.objects.create(
                item_id=item_id,
                employee_name=employee_name,
                unit_of_measurement=unit_of_measurement,
                quantity=quantity,
                price_without_VAT=price_without_vat,
                comment=comment,
                status=status
                )
            messages.success(request, "Request created")
            return redirect(self.success_url)

        else:
            messages.error(request, "Failed to create request. Please check your input and try again.")
            context = {
                'item_id': data['item_id'],
                'form': self.form_class}

            return render(request, self.template_name, context)


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

    def post(self, request, *args, **kwargs):
        data = request.POST
        match data['status']:
            case 'apr':
                request_object = self.model.objects.get(request_id=int(data['request_id']))
                item_object = request_object.item_id
                item_object_previous_quantity = getattr(item_object, 'quantity')
                request_object_item_quantity = getattr(request_object, 'quantity')
                if check_if_item_in_stock(item_object_previous_quantity, request_object_item_quantity):
                    request_object.status = Requests.Status.APPROVED
                    request_object.save(update_fields=['status'])
                    current_item_object_quantity = item_object_previous_quantity - request_object_item_quantity
                    item_object.quantity = current_item_object_quantity
                    item_object.save(update_fields=['quantity'])
                    return redirect(self.success_url)
                else:
                    messages.error(request, "There is not enough items in stock to complete this order")
                    context = {
                        'request_object': request_object,
                        'request_id': data['request_id'],
                        'form': self.form_class}

                    return render(request, self.template_name, context)

            case 'rej':
                request_object = self.model.objects.get(request_id=int(data['request_id']))
                request_object.status = Requests.Status.REJECTED
                request_object.save(update_fields=['status'])
                return redirect(self.success_url)

            case 'new':
                request_object = self.model.objects.get(request_id=int(data['request_id']))
                request_object.status = Requests.Status.NEW
                request_object.save(update_fields=['status'])
                return redirect(self.success_url)
