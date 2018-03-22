from django.db import models
from django.urls import reverse
import datetime
# Create your models here.
class Shipment(models.Model):
    SEAFREIGHT='S'
    AIRFREIGHT='F'
    COURIER='C'
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
    code=models.TextField(max_length=20)
    etd=models.DateField(default=datetime.datetime.now().date())
    eta=models.DateField()
    instore=models.DateField()
    instore_abm=models.DateField()
    total_quantity=models.IntegerField(default=0)
    volume=models.DecimalField(max_digits=4,decimal_places=1,default=0)
    cartons=models.IntegerField(default=0)
    mode=models.TextField(max_length=1,choices=MODE,default=SEAFREIGHT)
    etd_port=models.TextField(choices=ETD_PORT, default='GUANGZHOU')
    eta_port=models.TextField(choices=ETA_PORT, default='BRISBANE')
    container=models.TextField(max_length=50,null=True,blank=True)

    class Meta:
        verbose_name="Shipment"''
        verbose_name_plural="Shipments"
        ordering=('etd_port','etd',)

    def __str__(self):
        return '{0}-{1}-{2}-{3}-{4}'.format(self.code,self.etd_port,self.eta_port,self.etd,self.container)

    def get_absolute_url(self):
        return reverse('shipment_detail',kwargs={'pk':self.pk})
