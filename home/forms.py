from django.forms import ModelForm, NumberInput, TextInput, Select
from .models import RelaySettings, SensorSettings


class RelayModelForm(ModelForm):
    class Meta:
        model = RelaySettings
        fields = ("relay_id", 'GPIO_pin', 'description', 'name')
        widgets = {
            "relay_id": NumberInput(attrs={'placeholder': 'Relay Id', 'class': 'form-control'}),
            'GPIO_pin': NumberInput(attrs={'placeholder': 'GPIO Pin', 'class': 'form-control'}),
            'name': TextInput(attrs={'placeholder': 'Name', 'class': 'form-control'}),
            'description': TextInput(attrs={'placeholder': 'Description', 'class': 'form-control'})
        }


class SensorModelForm(ModelForm):
    class Meta:
        CHOICES = (('DHT11', 11), ('DHT22', 22))
        model = SensorSettings
        fields = ('sensor_id', 'type', 'GPIO_pin', 'description')
        widgets = {
            'sensor_id': NumberInput(attrs={'placeholder': 'Sensor Id', 'class': 'form-control'}),
            'type': Select(attrs={'placeholder': 'Sensor Type', 'class': 'custom-select'}, choices=CHOICES),
            'GPIO_pin': NumberInput(attrs={'placeholder': 'GPIO Pin', 'class': 'form-control'}),
            'description': TextInput(attrs={'placeholder': 'Description', 'class': 'form-control'})
        }
