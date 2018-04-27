from django.shortcuts import render
from shipments.models import Shipment
from shipments.forms import ShipmentForm
from django.views.generic.edit import CreateView,UpdateView,DeleteView
from django.views.generic import ListView
import datetime,dateutil,calendar
from TISProduction import tis_log

logger=tis_log.get_tis_logger()
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

def get_next_month_warehouse():
    today=datetime.date.today()
    next_month_date=today+dateutil.relativedelta.relativedelta(months=+1)
    firtday,days=calendar.monthrange(next_month_date.year,next_month_date.month)
    last_day_next_month=datetime.date(year=next_month_date.year,month=next_month_date.month,day=days)
    logger.debug(' get the last day of next month is {0}'.format(last_day_next_month))
    try:
        shipments=Shipment.objects.filter(instore__gt=today).filter(instore__lt=last_day_next_month)\
            .order_by('instore').exclude(mode__iexact='Courier')
    except Exception as e:
        logger.error(' error occur when get shipment for warehouse {0}'.format(e))
    return shipments