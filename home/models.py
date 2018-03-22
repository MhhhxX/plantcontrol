from django.db import models
from django.core.exceptions import ObjectDoesNotExist

# Create your models here.
device_names = {'fan': 'Lüfter', 'light': 'Licht', 'pump': 'Pumpe'}


class RelaySettings(models.Model):
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
                    result = RelaySettings.objects.get(name=device_names[pin]).GPIO_pin
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

    @staticmethod
    def data_period(dt_from, dt_until):
        lt_exclude = HygroTempData.objects.exclude(timestamp__lt=dt_from)
        return lt_exclude.exclude(timestamp__gt=dt_until)

    @staticmethod
    def mean(dt_from, dt_until):
        period_data = HygroTempData.data_period(dt_from, dt_until)

        partial_sum_temp = 0
        partial_sum_hum = 0
        for data in period_data:
            partial_sum_temp += data.temperature
            partial_sum_hum += data.humidity

        return partial_sum_temp / period_data.__len__(), partial_sum_hum / period_data.__len__()
