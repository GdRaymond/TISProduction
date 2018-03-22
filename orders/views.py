from django.shortcuts import render
from django.views.generic.edit import CreateView,UpdateView
from django.views.generic import ListView
from orders.models import Order
from orders.forms import OrderForm
# Create your views here.

class OrderCreat(CreateView):
    model=Order
    form_class = OrderForm
    success_url = '/order/list/'

class OrderList(ListView):
    model=Order
    template_name='order_list.html'