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

class Actual_quantity(models.Model):
    packing=models.ForeignKey(Packing,on_delete=models.SET_NULL,null=True)
    colour=models.CharField(max_length=20)
    total_quantity=models.IntegerField(default=0)
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
        verbose_name='actual ship quantity'

    def __str__(self):
        return '{0}-{1}-{2}-{3}'.format(self.packing.invoice_no,self.packing.style,self.colour,self.total_quantity)
