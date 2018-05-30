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

def get_next_2month_inspection():
    today=datetime.date.today()
    start_date=today+dateutil.relativedelta.relativedelta(days=+6)
    next_month_date=today+dateutil.relativedelta.relativedelta(months=+2)
    firtday,days=calendar.monthrange(next_month_date.year,next_month_date.month)
    last_day_next_month=datetime.date(year=next_month_date.year,month=next_month_date.month,day=days)
    logger.debug(' get the last day of next month is {0}'.format(last_day_next_month))
    try:
        shipments=Shipment.objects.filter(etd__gt=start_date).filter(etd__lt=last_day_next_month)\
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
            if str(shipment.mode).strip().upper()=='SEA':
                shipment_info = '\n\nShipment-{0}: {1}  Delivery:{2} with {3} cartons {4} m3 by {5} ; ETD:{6} From {7}'.\
                    format(index+1,shipment.container, shipment.instore, shipment.cartons, shipment.volume,\
                           shipment.supplier,shipment.etd,shipment.etd_port)
            else:
                shipment_info = '\n\nShipment-{0}: {1}  Delivery:{2} with {3} cartons {4} m3 by {5} ; ETD:{6} From {7}'.\
                    format(index + 1, shipment.mode,  shipment.instore, shipment.cartons, shipment.volume,
                    shipment.supplier,shipment.etd, shipment.etd_port)
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
    logger.debug(' gettting insepction order for shipment {0}-{1} etd_port {2}'.format(shipment.id,shipment,shipment.etd_port))
    if str(shipment.etd_port).upper().strip()=='NINGBO':
        orders=shipment.order_set.all()
        logger.debug('   As ETD from Ningbo, get all orders {0}'.format(len(orders)))
    elif not str(shipment.etd_port).upper().strip()=='GUANGZHOU':
        orders=shipment.order_set.filter(~Q(client__iexact='Ritemate'))
        logger.debug('   As ETD not from Ningbo not AUWIN, excluding Ritemate get orders {0}'.format(len(orders)))
    else:
        logger.debug('   As it is Auwin, no need inspect')
        orders=None
    return orders

def write_inspection_shipment(shipments):
    file_name=os.path.normpath(os.path.join(settings.BASE_DIR+'\media\warehouse\Mike_{0}.txt'.\
                                            format(datetime.date.today().strftime('%Y_%m_%d'))))
    logger.debug('start to write to file for Mike inspection schedule {0}'.format(file_name))
    with open(file_name,'w') as ins_file:
        shipment_no=0
        for index in range(len(shipments)):
            shipment=shipments[index]
            orders=get_orders_inspection_from_shipment(shipment)
            if not orders or len(orders)==0:
                logger.debug(' skip shipment {0}  '.format(shipment))
            else:
                shipment_no+=1
                logger.debug('  get shipment {0}, No. {1} with {2} orders'.format(shipment,shipment_no,len(orders)))
                if str(shipment.mode).strip().upper()=='SEA':
                    shipment_info = '\n\nShipment-{0}: {1} ETD {2} EX {3} in {4}'.format(
                        shipment_no, shipment.supplier, shipment.etd, shipment.etd_port,shipment.container)
                else:
                    shipment_info = '\n\nShipment-{0}: {1} ETD {2} EX {3} in {4}'.format(
                        shipment_no, shipment.supplier, shipment.etd, shipment.etd_port, shipment.mode)
                ins_file.write(shipment_info)
                total_qty=0
                for order in orders:
                    order_info = '\n  {0:<13} - {1:<15} - {2:<13} - {3:>5} pcs - {4:>3d} cartons'.format(order.tis_no,
                                                                                      order.product.style_no,
                                                                                      order.colour, order.quantity,
                                                                                      order.cartons)
                    ins_file.write(order_info)
                    total_qty+=order.quantity
                ins_file.write('\n Total Quantity: {0:,} pcs'.format(total_qty))
    logger.debug('finish writing inspection file')




