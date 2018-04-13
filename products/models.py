from django.db import models

# Create your models here.

class Fabric(models.Model):
    fabric=models.TextField(max_length=200)

    class Meta:
        verbose_name='Fabric'
        verbose_name_plural='Fabrics'

class Product(models.Model):

    style_no=models.TextField(max_length=50)
    client=models.TextField(max_length=100,null=True,blank=True)
    commodity=models.TextField(max_length=100,null=True,blank=True)
    fabric=models.ForeignKey(Fabric,on_delete=models.PROTECT)
    fabric_usage=models.DecimalField(max_digits=4,decimal_places=2,default=0)
    quantity_per_carton=models.IntegerField(default=0)
    volume_per_carton=models.DecimalField(max_digits=4,decimal_places=3,default=0)
    weight_per_carton=models.DecimalField(max_digits=3,decimal_places=1,default=0)

    class Meta:
        verbose_name='Product'
        verbose_name_plural='Products'
        ordering=('style_no',)

    def __str__(self):
        return self.style_no
