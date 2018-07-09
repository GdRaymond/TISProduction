from django.db import models

# Create your models here.
class Packing (models.Model):
    tis_no=models.CharField(max_length=15,default='TIS18-SO')
    internal_no=models.CharField(max_length=11,null=True,blank=True)
    supplier=models.CharField(max_length=50)
    style=models.CharField(max_length=50)
    commodity=models.CharField(max_length=100,null=True,blank=True)
    price=models.DecimalField(max_digits=5,decimal_places=3,default=0.0,null=True,blank=True)
    invoice_no=models.CharField(max_length=50)
    total_quantity=models.IntegerField(default=0,null=True,blank=True)
    total_carton=models.IntegerField(default=0,null=True,blank=True)
    total_weight=models.DecimalField(max_digits=7,decimal_places=2,null=True,blank=True)
    total_volume=models.DecimalField(max_digits=9,decimal_places=6,null=True,blank=True)
    invoice_date=models.DateField()
    source=models.CharField(max_length=100)

    class Meta:
        verbose_name='invoice'
        verbose_name_plural='invoices'
        ordering=('tis_no',)

    def __str__(self):
        return '{0}-{1}-{2}-{3}'.format(self.tis_no,self.style,self.total_quantity,self.invoice_no)

