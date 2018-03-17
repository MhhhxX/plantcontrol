from django.forms import ModelForm, NumberInput, TextInput
from .models import RelaisSettings, SensorSettings


class RelaisModelForm(ModelForm):
    class Meta:
        model = RelaisSettings
        fields = ('relais_id', 'GPIO_pin', 'description', 'name')
        widgets = {
            'relais_id': NumberInput(attrs={'placeholder': 'Relais Id', 'class': 'form-control'}),
            'GPIO_pin': NumberInput(attrs={'placeholder': 'GPIO Pin', 'class': 'form-control'}),
            'name': TextInput(attrs={'placeholder': 'Name', 'class': 'form-control'}),
            'description': TextInput(attrs={'placeholder': 'Description', 'class': 'form-control'})
        }


class SensorModelForm(ModelForm):
    class Meta:
        model = SensorSettings
        fields = ('sensor_id', 'type', 'GPIO_pin', 'description')
        widgets = {
            'sensor_id': NumberInput(attrs={'placeholder': 'Sensor Id', 'class': 'form-control'}),
            'type': NumberInput(attrs={'placeholder': 'Sensor Type', 'class': 'form-control'}),
            'GPIO_pin': NumberInput(attrs={'placeholder': 'GPIO Pin', 'class': 'form-control'}),
            'description': TextInput(attrs={'placeholder': 'Description', 'class': 'form-control'})
        }
