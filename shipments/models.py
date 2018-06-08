from django.db import models
from django.urls import reverse
from products import product_price
import datetime,re
from TISProduction import tis_log
#from orders.models import Order
logger=tis_log.get_tis_logger()

# Create your models here.
class Shipment(models.Model):
    SEAFREIGHT='Sea'
    AIRFREIGHT='Air'
    COURIER='Courier'
    MODE=(
        (SEAFREIGHT,'Seafreight'),
        (AIRFREIGHT,'Airfreight'),
        (COURIER,'Courier'),
    )
    ETD_PORT=(
        ('GUANGZHOU','Guangzhou'),
        ('NINGBO','Ningbo'),
        ('SHANGHAI','Shanghai'),
        ('QINGDAO','Qingdao'),
        ('XINGANG','Xingang'),
        ('BEIJING','Beijing'),
        ('OTHER','other'),
    )
    ETA_PORT = (
        ('BRISBANE', 'Brisbane'),
        ('SYDNEY', 'Sydney'),
        ('MELBOURNE', 'Melbourne'),
        ('OTHER', 'Other'),
    )

    TT_DAYS={'GUANGZHOU_SEA':(13,3),'NINGBO_SEA':(11,7),'SHANGHAI_SEA':(13,7),'XINGANG_SEA':(35,3)} #define the tt days
    code=models.TextField(max_length=20)
    supplier = models.TextField(max_length=50)
    etd=models.DateField(default=datetime.datetime.now().date())
    eta=models.DateField()
    instore=models.DateField()
    instore_abm=models.DateField(null=True)
    total_quantity=models.IntegerField(default=0)
    volume=models.DecimalField(max_digits=6,decimal_places=3,default=0)
    cartons=models.IntegerField(default=0)
    weight=models.DecimalField(max_digits=7,decimal_places=1,default=0)
    mode=models.TextField(max_length=10,choices=MODE,default=SEAFREIGHT)
    etd_port=models.TextField(choices=ETD_PORT, default='GUANGZHOU')
    eta_port=models.TextField(choices=ETA_PORT, default='BRISBANE')
    container=models.TextField(max_length=50,null=True,blank=True)

    class Meta:
        verbose_name="Shipment"''
        verbose_name_plural="Shipments"
        ordering=('etd_port','etd',)

    def __str__(self):
        return '{5}-{0}-{1}-{2}-{3}-{4}'.format(self.code,self.etd_port,self.eta_port,self.etd,self.container,self.supplier)

    def get_absolute_url(self):
        return reverse('shipment_detail',kwargs={'pk':self.pk})


    @staticmethod
    def get_tt_days(mode,etd_port):
        tt_days={}
        mode=mode.upper()
        if mode in ['AIR','COURIER']: #all airfreight or courier to be assumed as 4 days flight and 1 days clear
            tt_days['tt_freight']=4
            tt_days['tt_cls']=1
        else: #seafreight
            days=Shipment.TT_DAYS.get('{0}_SEA'.format(etd_port.upper()),(35,3))
            tt_days['tt_freight']=days[0]
            tt_days['tt_cls']=days[1]
        return tt_days

    @staticmethod
    def get_current_and_next_shipment_code(supplier,etd_date):
        codes={}
        mon_year=etd_date.strftime('%b %y').upper()
        supplier_abbr=product_price.supplier_abbreviation.get(supplier.upper(),'OT')
        starts_with='{0}-{1}'.format(supplier_abbr,mon_year)
        logger.debug('starts_with is {0}'.format(starts_with))
        shipment_code_list=[shipment.get('code') for shipment in \
                            Shipment.objects.filter(code__istartswith=starts_with).values('code').order_by('code').distinct()]
        logger.debug('get shipment_code_list {0}'.format(shipment_code_list))
        codes['current']=shipment_code_list
        if shipment_code_list:
            max=int(shipment_code_list[-1].split('-')[2])
        else:
            max=0
        next_no=max+1
        next_ship_code=starts_with+'-'+str(next_no)
        logger.debug('get next ship code {0}'.format(next_ship_code))
        codes['next']=next_ship_code
        return codes

    @staticmethod
    def get_shipment(ship_code,etd,supplier,freight,etd_port):
        '''
        to create or get a current shipment
        :param ship_code: If not None it means the caller assign a current shipment which maybe already in database or \
        maybe need create with this shipcode(for example read from trace excel).\
        If None, then check if exist the shipment with same ETD&Supplier&MODE, Otherwise caller need this function to generate a shipcode accordingly
        :param etd:
        :param supplier:
        :param freight:
        :return: shipment
        '''
        if ship_code is not None:
            try:
                shipment=Shipment.objects.get(code__iexact=ship_code)
                logger.debug('  get current shipment {0}'.format(shipment))
            except Shipment.DoesNotExist:
                shipment=Shipment(code=ship_code,supplier=supplier,etd=etd,mode=freight,etd_port=etd_port)
                logger.debug('   create record for current shipment {0}'.format(shipment))
            return shipment
        else: #No ship_code assigned
            shipment_list=Shipment.objects.filter(etd=etd,supplier__iexact=supplier,
                                                  mode__icontains=freight,etd_port__icontains=etd_port)
            if shipment_list.exists(): #check if exist shipment with same etd supplier mode
                shipment=shipment_list[0]
            else: #need create a new shipment
                mon_year=etd.strftime('%b %y').upper()
                code_start='{0}-{1}-'.format(product_price.supplier_abbreviation.get(supplier.upper(),'OT'),mon_year)
                logger.debug('    ship code start with {0}'.format(code_start))
                try:
                    current_shipment_list=Shipment.objects.filter(code__istartswith=code_start) #get the shipcode of same supplier in this month
                except Exception as e:
                    logger.debug('  error filter ship code list {0}'.format(e))
                if current_shipment_list.exists(): #if exists means there are other shipment in this month
                    seq_list=[]
                    for current_shipment in current_shipment_list:
                        match=re.search(r'(\d+)(-)(\d+)',current_shipment.code) #in TH-MAR 18-2, match (18)(-)(2)
                        seq=int(match.group(3)) #seq=2
                        seq_list.append(seq)
                    logger.debug('    ship code seq list {0}'.format(seq_list))
                    new_code='{0}{1}'.format(code_start,max(seq_list)+1)#get the next sequence of maximum,TH-MAR 18-3
                    logger.debug('    get next ship code for {0} this month {1}'.format(supplier,new_code))
                else: #if there is no other shipment in this month, then assign the seq=1
                    new_code=code_start+'1' #TH-MAR 18-1
                    logger.debug('   new ship code start from 1,  {0}'.format(new_code))
                try:
                    shipment=Shipment(code=new_code,supplier=supplier,etd=etd,mode=freight,etd_port=etd_port)
                except Exception as e:
                    logger.debug('  error when create shipment : {0}'.format(e))
                    return None
            return shipment
