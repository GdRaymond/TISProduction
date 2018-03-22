from django import forms
from shipments.models import Shipment

class ShipmentForm(forms.ModelForm):
    class Meta:
        model=Shipment
        fields='__all__'