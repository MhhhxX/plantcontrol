from django.db import models
from django.core.exceptions import ObjectDoesNotExist

# Create your models here.
device_names = {'fan': 'Lüfter', 'light': 'Licht', 'pump': 'Pumpe'}

class RelaisSettings(models.Model):
    relais_id = models.IntegerField(primary_key=True)
    GPIO_pin = models.IntegerField(unique=True)
    description = models.CharField(max_length=30, default="Description")
    name = models.CharField(max_length=15, default="Name")
    state = models.BooleanField(default=False)

    @staticmethod
    def pin_checkup(*pins):
        results = {}
        for pin in pins:
            if pin in device_names:
                try:
                    result = RelaisSettings.objects.get(name=device_names[pin]).GPIO_pin
                    results.update({pin: result})
                except ObjectDoesNotExist:
                    print("{} is not specified. Please add a table entry for {} where name is '{}'".
                          format(pin, pin, device_names[pin]))
                    return {}
            else:
                print("There is no task for {}!".format(pin))
                return {}
        return results


class SensorSettings(models.Model):
    sensor_id = models.IntegerField(primary_key=True, default=-1)
    type = models.IntegerField()
    GPIO_pin = models.IntegerField(unique=True)
    description = models.CharField(max_length=30, default="Description")

    def __str__(self):
        return "Sensor number: {}, Sensor Type: DHT{}, At GPIO-Pin: {}".format(self.sensor_id, self.type, self.GPIO_pin)


class HygroTempData(models.Model):
    humidity = models.DecimalField(max_digits=3, decimal_places=2)
    temperature = models.DecimalField(max_digits=3, decimal_places=2)
    timestamp = models.DateTimeField()
    sensor = models.ForeignKey(SensorSettings, models.CASCADE, default=-1)

