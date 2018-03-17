from django.db import models

# Create your models here.


class RelaisSettings(models.Model):
    relais_id = models.IntegerField(primary_key=True)
    GPIO_pin = models.IntegerField(unique=True)
    description = models.CharField(max_length=30, default="Description")
    name = models.CharField(max_length=15, default="Name")
    state = models.BooleanField(default=False)


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

