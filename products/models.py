from django.db import models
from django.conf import settings

# Create your models here.

class Fabric(models.Model):
    fabric=models.TextField(max_length=200)

    class Meta:
        verbose_name='Fabric'
        verbose_name_plural='Fabrics'

DEFAULT_FABRIC_ID=44
class Product(models.Model):

    style_no=models.TextField(max_length=50)
    client=models.TextField(max_length=100,null=True,blank=True)
    commodity=models.TextField(max_length=100,null=True,blank=True)
    if settings.DEBUG:
        fabric = models.ForeignKey(Fabric, on_delete=models.CASCADE,default=DEFAULT_FABRIC_ID)
    else:
        fabric = models.ForeignKey(Fabric, on_delete=models.PROTECT,default=DEFAULT_FABRIC_ID)
    fabric_usage=models.DecimalField(max_digits=4,decimal_places=2,default=0)
    quantity_per_carton=models.IntegerField(default=0)
    volume_per_carton=models.DecimalField(max_digits=4,decimal_places=3,default=0)
    weight_per_carton=models.DecimalField(max_digits=3,decimal_places=1,default=0)

    class Meta:
        verbose_name='Product'
        verbose_name_plural='Products'
        ordering=('style_no',)

    def __str__(self):
        return '{0} {1} for {2}'.format(self.style_no,self.commodity,self.client)

    @staticmethod
    def get_default_fabric():
        return Fabric.objects.get(fabric='other')
