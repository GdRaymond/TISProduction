from django import forms
from products.models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model=Product
        fields=['style_no','commodity','fabric','fabric_usage','quantity_per_carton','volume_per_carton',
                'weight_per_carton']