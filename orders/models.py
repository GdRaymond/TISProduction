from django.db import models
from django.conf import settings
from products.models import Product

from orders import parse_requisiton
from excelway.read_excel_by_xlrd import read_excel_file
import glob
from shipments.models import Shipment
from django.utils.translation import ugettext_lazy as _
import re,datetime
from django.dispatch import receiver
from django.db.models.signals import post_save
from products import product_price


from TISProduction import tis_log
logger=tis_log.get_tis_logger()
# Create your models here.


class Order(models.Model):
    tis_no=models.CharField(max_length=15,default='TIS18-SO')
    internal_no=models.CharField(max_length=11,default='2018-PO',null=True)
    ctm_no=models.CharField(max_length=50,null=True)
    client=models.TextField(max_length=50)
    supplier=models.TextField(max_length=50)
    if settings.DEBUG:
        product = models.ForeignKey(Product, on_delete=models.CASCADE)
    else:
        product=models.ForeignKey(Product,on_delete=models.PROTECT)
    colour=models.TextField(max_length=20)
    quantity=models.IntegerField()
    shipment=models.ForeignKey(Shipment,on_delete=models.SET_NULL,null=True)
    purchase_price=models.DecimalField(max_digits=5,decimal_places=2,default=0,null=True)
    sell_price=models.DecimalField(max_digits=5,decimal_places=2,default=0,null=True)
    size1=models.IntegerField(default=0,null=True)
    size2=models.IntegerField(default=0,null=True)
    size3=models.IntegerField(default=0,null=True)
    size4=models.IntegerField(default=0,null=True)
    size5=models.IntegerField(default=0,null=True)
    size6=models.IntegerField(default=0,null=True)
    size7=models.IntegerField(default=0,null=True)
    size8=models.IntegerField(default=0,null=True)
    size9=models.IntegerField(default=0,null=True)
    size10=models.IntegerField(default=0,null=True)
    size11=models.IntegerField(default=0,null=True)
    size12=models.IntegerField(default=0,null=True)
    size13=models.IntegerField(default=0,null=True)
    size14=models.IntegerField(default=0,null=True)
    size15=models.IntegerField(default=0,null=True)
    size16=models.IntegerField(default=0,null=True)
    size17=models.IntegerField(default=0,null=True)
    size18=models.IntegerField(default=0,null=True)
    size19=models.IntegerField(default=0,null=True)
    size20=models.IntegerField(default=0,null=True)
    size21=models.IntegerField(default=0,null=True)
    size22=models.IntegerField(default=0,null=True)
    size23=models.IntegerField(default=0,null=True)
    size24=models.IntegerField(default=0,null=True)
    size25=models.IntegerField(default=0,null=True)
    size26=models.IntegerField(default=0,null=True)
    size27=models.IntegerField(default=0,null=True)
    size28=models.IntegerField(default=0,null=True)
    size29=models.IntegerField(default=0,null=True)
    size30=models.IntegerField(default=0,null=True)

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
    RECEIVED='G'
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
    check_date=models.DateField(default=datetime.date.today())
    comment=models.TextField(max_length=500,null=True,blank=True)
    ref=models.TextField(max_length=100,null=True,blank=True)
    order=models.ForeignKey(Order,on_delete=models.CASCADE,)
    fabric=models.ForeignKey(FabricTrim,on_delete=models.CASCADE,null=True)

    class Meta:
        verbose_name = _("Checking")
        verbose_name_plural = _("Checkings")
        ordering=("check_date",)

@receiver(post_save,sender=Order)
def create_fabric_trim(sender,created,instance,**kwargs):
    if created:
        colours=instance.colour.split('/')
        logger.debug('   new order, analyse colours {0}'.format(colours))
        for colour in colours:
            colour_name=product_price.check_colour_abbr(colour.strip().upper())
            fabric_trim=FabricTrim(colour_solid=colour_name,order=instance)
            fabric_trim.save()
            logger.debug('   fabric trim saved {0}'.format(fabric_trim))

def create_test_report_check(order_id, test_report_group):
    '''
    from trace excel parse the test report record to databas
    :param tis_no: 'TIS18-SO1234'
    :param test_report_group: [{'comment_date':2018-1-1,'colours':['ORANGE','NAVY'],'reference':'NQA123','comment':'NAVY APPROVE ORANGE REJECTED'},{{'comment_date':2018-1-7,'colours':['ORANGE'],'reference':'NQA234','comment':'ORANGE APP'}]
    :return: number of saving sample check
    '''
    logger.debug('  start to create test report check for order {0} with report comments {1}'.format(order_id,test_report_group))
    try:
        trims=FabricTrim.objects.filter(order_id=order_id) #[{colour_solid=ORANGE,orderid},{colour_solid=ORANGE,orderid}]
    except Exception as e:
        logger.debug('  error when query for Fabric tirm : {0}'.format(e))
    logger.debug('    trims for order {0} is {1}'.format(order_id,trims))
    result=0
    for trim in trims:
        logger.debug('    check trim colour {0}'.format(trim.colour_solid))
        for test_report in test_report_group: #{'comment_date':2018-1-1,'colours':['ORANGE','NAVY'],'reference':'NQA123','comment':'NAVY APPROVE ORANGE REJECTED'}
            logger.debug('    test report {0}'.format(test_report))
            colours=test_report.get('colours') #['ORANGE','NAVY']
            logger.debug('    colours={0}'.format(colours))
            if colours=='ALL' or trim.colour_solid in colours: #ORANGE
                comment=test_report.get('comment') #NAVY APPROVE ORANGE REJECTED
                logger.debug('    comment is {0}'.format(comment))
                if comment:
                    comment_words=[word.strip().upper() for word in comment.split(' ')]#['NAVY', 'APPROVE', 'ORANGE', 'REJECTED']
                    logger.debug('   comment_words list is {0}'.format(comment_words))
                    if trim.colour_solid in comment_words:
                        index_colour=comment_words.index(trim.colour_solid) # 2
                        logger.debug('      find the colour in comments words index {0}'.format(index_colour))
                        if len(comment_words)>index_colour+1:
                            comment_colour=comment_words[index_colour+1].strip().upper()#'REJECTED'
                            logger.debug('      comment for colour is {0}'.format(comment_colour))
                            if comment_colour[:3]=='REJ':
                                status='R'
                                logger.debug('      status R because comment REJ following colour')
                            else:
                                status='A'
                                logger.debug('      status A because no comment following colour')
                        else:
                            status='A'
                            logger.debug('      status A because no text following colour')
                    else: # no colour name in comment then search the APPROVE OR REJECT Word
                        for word in comment_words: #only asserted by the 1st word containing APP or REJ
                                if word[:3]=='APP':
                                    status='A'
                                    logger.debug('      status A because no colour in comment but with APP')
                                    break
                                elif word[:3]=='REJ':
                                    status='R'
                                    logger.debug('      status R because no colour in comment but with REJ')
                                    break
                        else: # can not find APP or REJ in comments, then assume approve
                            status='A'
                            logger.debug('      status A because no colour in comment no APP or REJ')

                else: #no comment means this test report is approved completely
                    status='A'
                    logger.debug('      status A because no comment')
                try:
                    test_report_check=SampleCheck(type='T',status=status,check_date=test_report.get('comment_date')
                                              ,comment=comment,ref=test_report.get('reference'),fabric=trim,order_id=order_id)
                    test_report_check.save()
                except Exception as e:
                    logger.debug('    error when save the test_report_check: {0}'.format(e))
                result+=1
            else: # no colour match or no ALL
                logger.debug('   not match colour or ALL')

    logger.debug('  finish test report parse')
    return result

def create_garment_sample_check(type,order_id,comment):
    result=0
    logger.debug('  start to create garment sample check {0}-{1}-{2}'.format(type,order_id,comment))
    if not comment:
        return result
    match=re.search(r'\b(?P<day>\d{1,2})\s+(?P<mon>\w+)\s+(?P<year>\d{4}).*',comment)
    if match:
        mon=int(datetime.datetime.strptime(match.group('mon'),'%b').strftime('%m'))
        year=int(match.group('year'))
        day=int(match.group('day'))
        check_date=datetime.date(year=year,month=mon,day=day)
        logger.debug('  parse check date {0}'.format(check_date))
    else:
        logger.debug('  can not match the date, exit')
        return result
    comment_words=[word.strip().upper() for word in comment.split(' ')]
    for word in comment_words:
        if word[:3]=='APP':
            status='A'
            logger.debug('  status A because find APP in comment')
            break
        elif word[:3]=='REJ':
            status='R'
            logger.debug('  status R because find REJ in comment')
            break
    else: #can not find APP or REJ
        logger.debug('  status A because NOT find APP or REJ in comment')
        status='A'
    try:
        garment_check_dict={'type':type,'status':status,'check_date':check_date,'comment':comment,'order_id':order_id}
        garment_check=SampleCheck.objects.create(**garment_check_dict)
        result=1
        logger.debug('  finished save garment check {0}'.format(garment_check))
    except Exception as e:
        logger.debug('  error when saveing garment check {0}'.format(e))
    return result