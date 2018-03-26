from django.db import models
from products.models import Product
from orders import parse_requisiton
from excelway.read_excel_by_xlrd import read_excel_file
import glob
from TISProduction import tis_log
from shipments.models import Shipment
from django.utils.translation import ugettext_lazy as _
from excelway.tis_excel import TIS_Excel

logger=tis_log.get_tis_logger()
# Create your models here.


class Order(models.Model):
    tis_no=models.CharField(max_length=15,default='TIS18-SO')
    internal_no=models.CharField(max_length=11,default='2018-PO')
    ctm_no=models.CharField(max_length=50)
    client=models.TextField(max_length=50)
    supplier=models.TextField(max_length=50)
    product=models.ForeignKey(Product,on_delete=models.PROTECT,)
    colour=models.TextField(max_length=20)
    quantity=models.IntegerField()
    shipment=models.ForeignKey(Shipment,on_delete=models.SET_NULL,null=True)
    purchase_price=models.DecimalField(max_digits=5,decimal_places=2,default=0)
    sell_price=models.DecimalField(max_digits=5,decimal_places=2,default=0)
    size1=models.IntegerField(default=0)
    size2=models.IntegerField(default=0)
    size3=models.IntegerField(default=0)
    size4=models.IntegerField(default=0)
    size5=models.IntegerField(default=0)
    size6=models.IntegerField(default=0)
    size7=models.IntegerField(default=0)
    size8=models.IntegerField(default=0)
    size9=models.IntegerField(default=0)
    size10=models.IntegerField(default=0)
    size11=models.IntegerField(default=0)
    size12=models.IntegerField(default=0)
    size13=models.IntegerField(default=0)
    size14=models.IntegerField(default=0)
    size15=models.IntegerField(default=0)
    size16=models.IntegerField(default=0)
    size17=models.IntegerField(default=0)
    size18=models.IntegerField(default=0)
    size19=models.IntegerField(default=0)
    size20=models.IntegerField(default=0)
    size21=models.IntegerField(default=0)
    size22=models.IntegerField(default=0)
    size23=models.IntegerField(default=0)
    size24=models.IntegerField(default=0)
    size25=models.IntegerField(default=0)
    size26=models.IntegerField(default=0)
    size27=models.IntegerField(default=0)
    size28=models.IntegerField(default=0)
    size29=models.IntegerField(default=0)
    size30=models.IntegerField(default=0)

    class Meta:
        verbose_name='Order'
        verbose_name_plural='Orders'
        ordering=('tis_no','colour')

    def __str__(self):
        return '{0}-{1}-{2}'.format(self.tis_no,self.product.__str__(),self.quantity)

    def get_tisno_style(self):
        return '{0}-{1}'.format(self.tis_no,self.product.__str__())

    def get_colour_block(self):
        colours=self.colour.split('/')
        return colours

    def get_or_create_fabric_trim(self):
        colours=self.get_colour_block()
        fabrics=[]
        for colour in colours:
            fabric=FabricTrim.objects.get_or_create(colour=colour,order=self)
            fabrics.append(fabric)
        return fabrics

    def create_sample_check(self,type,status,comment,ref):
        '''
        add the type PPSAMPLE,SSSAMPLE check
        :param type:
        :param status:
        :param comment:
        :param ref:
        :return:
        '''
        check=SampleCheck(type=type,status=status,comment=comment,ref=ref,order=self)
        check.save()

    def create_fabric_check(self,fabric,type,status,comment,ref):
        '''
        add the type FABRIC TESTREPORT check
        :param type:
        :param status:
        :param comment:
        :param ref:
        :return:
        '''
        check=SampleCheck(type=type,status=status,comment=comment,ref=ref,fabric=fabric)
        check.save()

    @staticmethod
    def generate_from_requisition(file_path,etd_dict):
        file_position=len(file_path)+1
        files=glob.glob(file_path)
        logger.debug('start to read requisition files in {0},total {1} files'.format(file_path,len(files)))
        for file in files:
            if file.startswith('~',file_position):
                continue
            excel_content=read_excel_file(file)
            if excel_content is None:
                continue
            logger.debug('Start reading file {0}, total {1} sheets'.format(file,len(excel_content.get('sheets'))))
            for sheetname in excel_content.get('sheets'):
                logger.debug('-Start to check the sheet %s'%sheetname)
                result=parse_requisiton.parse_requisition(cell_list=excel_content.get('sheets').get(sheetname), \
                                                    filename=excel_content.get('filename'), \
                                                    sheetname=sheetname,etd_dict=etd_dict)
                if result:
                    logger.debug(result)
                    logger.debug('--Correct')
            logger.debug('-Finish file')






class FabricTrim(models.Model):
    colour_solid=models.TextField(max_length=20)
    order=models.ForeignKey(Order,on_delete=models.CASCADE,)

    class Meta:
        verbose_name='Fabric Trim in Order'
        verbose_name_plural='Fabric Trims in Order'

    def __str__(self):
        return '{0}-{1}'.format(self.order.get_tisno_style(),self.colour_solid)

class SampleCheck(models.Model):
    PPSAMPLE='P'
    SSSAMPLE='S'
    FABRIC='F'
    TESTREPORT='T'
    DOCUMENT='D'
    INSPECTION='I'
    TYPE=(
        (PPSAMPLE,'PP Sample'),
        (SSSAMPLE, 'Shipping Sample'),
        (FABRIC, 'Fabric Swatch'),
        (TESTREPORT, 'Test Report'),
        (INSPECTION, 'Inspection'),
        (DOCUMENT, 'Shipping Doc'),
    )
    NONEED='N'
    NEED='Y'
    SENT='S'
    RECEIVED='R'
    APPROVED='A'
    REJECTED='R'
    STATUS=(
        (NONEED,'No Need'),
        (NEED, 'Need'),
        (SENT, 'Sent'),
        (RECEIVED, 'Received'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
    )
    type=models.CharField(max_length=1,choices=TYPE)
    status=models.CharField(max_length=1,choices=STATUS,default=NONEED)
    check_date=models.DateTimeField(auto_now_add=True)
    comment=models.TextField(max_length=500,null=True,blank=True)
    ref=models.TextField(max_length=100)
    order=models.ForeignKey(Order,on_delete=models.CASCADE,)
    fabric=models.ForeignKey(FabricTrim,on_delete=models.CASCADE,)

    class Meta:
        verbose_name = _("Checking")
        verbose_name_plural = _("Checkings")
        ordering=("check_date",)
