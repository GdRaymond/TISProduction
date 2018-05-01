from django.shortcuts import render
from shipments.models import Shipment
from shipments.forms import ShipmentForm
from django.views.generic.edit import CreateView,UpdateView,DeleteView
from django.views.generic import ListView
import datetime,dateutil,calendar,os
from TISProduction import tis_log
from orders.models import Order
from django.conf import settings
from django.db.models import Q

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

def get_next_month_inspection():
    today=datetime.date.today()
    next_month_date=today+dateutil.relativedelta.relativedelta(months=+1)
    firtday,days=calendar.monthrange(next_month_date.year,next_month_date.month)
    last_day_next_month=datetime.date(year=next_month_date.year,month=next_month_date.month,day=days)
    logger.debug(' get the last day of next month is {0}'.format(last_day_next_month))
    try:
        shipments=Shipment.objects.filter(etd__gt=today).filter(etd__lt=last_day_next_month)\
            .order_by('etd').exclude(mode__iexact='Courier')
    except Exception as e:
        logger.error(' error occur when get shipment for warehouse {0}'.format(e))
    return shipments


def cal_shipment_volume(shipment):
    logger.debug('  start to calculate shipment {0}'.format(shipment))
    shipment_v={}
    orders=Order.objects.filter(shipment=shipment)
    logger.debug('  get {0} orders in this shipment '.format(len(orders)))
    cartons=0
    volumes=0
    weights=0
    quantities=0
    for order in orders:
        cartons+=order.cartons
        volumes+=order.volumes
        weights+=order.weights
        quantities+=order.quantity
    shipment_v['cartons']=cartons
    shipment_v['volume']=volumes
    shipment_v['weight']=weights
    shipment_v['total_quantity']=quantities
    if shipment.mode=='Sea':
        if volumes>=62:
            shipment_v['container']='Need Split'
        elif volumes>44:
            shipment_v['container']='40HQ'
        elif volumes>=25:
            shipment_v['container']='40GP'
        elif volumes>=12:
            shipment_v['container']='20GP'
        else:
            shipment_v['container']='LCL'
    return shipment_v

def cal_all_shipment_volume():
    try:
        shipments=Shipment.objects.all()
    except Exception as e:
        logger.error(' error when get all shipments'.format(e))
    logger.debug(' get {0} shipments'.format(len(shipments)))
    for shipment in shipments:
        vol=cal_shipment_volume(shipment)
        shipment.cartons=vol.get('cartons',0)
        shipment.volume=vol.get('volume',0)
        shipment.weight=vol.get('weight',0)
        shipment.total_quantity=vol.get('total_quantity',0)
        shipment.container=vol.get('container')
        shipment.save()
    logger.info('finish saved all {0} shipment volume '.format(len(shipments)))

def write_all_shipment_warehouse(shipments):
    filename = os.path.normpath(os.path.join(settings.BASE_DIR+'\media\warehouse\warehouse_{0}.txt'.format(
        datetime.date.today().strftime('%Y_%m_%d'))))
    logger.info('Start to write {0} shipment to warehouse file {1}'.format(len(shipments),filename))
    with open(filename,'w') as dest_file:
        for index in range(len(shipments)):
            shipment=shipments[index]
            shipment_info = '\n\nShipment-{0}: {1} {2} Delivery:{3} with {4} cartons {5} m3 by {6} ; ETD:{7} From {8}'.format(
                index+1,shipment.mode,shipment.container, shipment.instore, shipment.cartons, shipment.volume, shipment.supplier,
            shipment.etd,shipment.etd_port)
            dest_file.write(shipment_info)
            try:
                orders = shipment.order_set.all()
                logger.debug(' get orders from shipment {0}'.format(len(orders)))
                for order in orders:
                    order_info='\n  {0} - {1} - {2} - {3} pcs - {4} cartons'.format(order.tis_no,order.product.style_no,
                                                                                  order.colour,order.quantity,order.cartons)
                    dest_file.write(order_info)
            except Exception as e:
                logger.error('  error when get orders from shipment {0}'.format(e))

def get_orders_inspection_from_shipment(shipment):
    if shipment.etd_port.upper()=='NINGBO':
        orders=shipment.order_set.all()
    elif not shipment.etd_port.upper()=='GUANGZHOU':
        orders=shipment.order_set.filter(~Q(client__iexact='Ritemate'))
    return orders



