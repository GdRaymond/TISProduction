from django.shortcuts import render
from django.views.generic import ListView
from django.views.generic.edit import CreateView
from products.models import Product
from products.forms import ProductForm
from django.http import HttpResponse,HttpResponseBadRequest

# Create your views here.
class ProductCreate(CreateView):
    template_name='product_form.html'
    model=Product
    form_class=ProductForm
    success_url='/product/list'

class ProductList(ListView):
    model=Product
    template_name='product_list.html'

def get_product_list(request):
    print('start get_product_list')
    if request.method=='GET':
        product_list=Product.objects.all()
        print(product_list)
        html=''
        for product in product_list:
            html="{0}\n<option value='{1}'>{2}</option>".format(html,product.pk,product.style_no)
            return HttpResponse(html)
    else:
        return HttpResponseBadRequest
