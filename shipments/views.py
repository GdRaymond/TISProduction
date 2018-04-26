from django.shortcuts import render
from shipments.models import Shipment
from shipments.forms import ShipmentForm
from django.views.generic.edit import CreateView,UpdateView,DeleteView
from django.views.generic import ListView
# Create your views here.

def _create_shipment(shipment_dict):
    shipment=Shipment(etd=shipment_dict.get('etd'),eta=shipment_dict.get('eta'),instore=shipment_dict.get('instore')\
                      ,instore_abm=shipment_dict.get('instore_abm'),mode=shipment_dict.get('mode')\
                      ,etd_port=shipment_dict.get('etd_port'),eta_port=shipment_dict.get('eta_port')\
                      ,container=shipment_dict.get('contaier'),code=shipment_dict.get('code'))
    shipment.save()

def create_shipment(request):
    pass

class ShipmentCreate(CreateView):
    print('shipment create')
    model=Shipment
    form_class=ShipmentForm
    success_url = '/shipment/add/'

class ShipmentList(ListView):
    model=Shipment

def get_all_shipment():
    return Shipment.objects.all().order_by('etd_port','etd')