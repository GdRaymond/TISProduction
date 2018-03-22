"""TISOrder URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from core import views as coreviews
from django.contrib.auth import views as django_authen_views
from authentication import views as local_authen_views
from shipments import views as shipment_views
from products import views as product_views
from orders import views as order_views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$',coreviews.home,name='home'),
    url(r'^login$',django_authen_views.login,{'template_name':'core/cover.html'},name='login'),
    url(r'^logout$',django_authen_views.logout,{'next_page':'/'},name='logout'),
    url(r'^signup$',local_authen_views.signup,name='signup'),
    url(r'^(?P<username>[^/]+)/$',coreviews.profile,name='profile'),
    url(r'^settings$',coreviews.settings,name='settings'),
    url(r'^shipment/add/',shipment_views.ShipmentCreate.as_view(),name='create_shipment'),
    url(r'^shipment/list/',shipment_views.ShipmentList.as_view(),name='shipment_list'),
    url(r'^product/add/',product_views.ProductCreate.as_view(),name='create_product'),
    url(r'^product/list/',product_views.ProductList.as_view(),name='product_list'),
    url(r'^product/get_list_ajax/',product_views.get_product_list,name='get_product_list'),
    url(r'^order/add/',order_views.OrderCreat.as_view(),name='create_order'),
    url(r'^order/list/',order_views.OrderList.as_view(),name='order_list'),


]
