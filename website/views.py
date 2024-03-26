from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.core.paginator import Paginator
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic.edit import UpdateView, DeleteView

from .forms import NewUserForm, ItemForm
from .models import Items


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
