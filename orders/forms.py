from django import forms
from orders.models import Order
class OrderForm(forms.ModelForm):
    tis_no=forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}),max_length=13,min_length=12,
                           label='TIS Order No.',required=True,
                           help_text='Starts with TIS',initial='TIS18-SO')
    internal_no=forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}),max_length=11,min_length=11,
                           label='TIS ABM Order No.',
                           help_text='Starts with TIS',initial='2018-PO')
    ctm_no=forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}),
                           label='Customer Order No.',
                           help_text='Client PO No.')
    client=forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}),
                           label='Client Company name')
    supplier=forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}),
                           label='Supplier Company name')
    colour=forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}),
                           label='Colour')

    class Meta:
        model=Order
        fields=['tis_no','internal_no','ctm_no','client','supplier','colour','quantity','product','shipment']