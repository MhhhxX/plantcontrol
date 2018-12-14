from django.db import models
from django.db.models import Avg, Max, Min
from django.core.exceptions import ObjectDoesNotExist

# Create your models here.
device_names = {'fan': 'Lüfter', 'light': 'Licht', 'pump': 'Pumpe'}


class RelaySettings(models.Model):
    relay_id = models.IntegerField(primary_key=True)
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
        return "Sensor number: {}, Sensor Type: DHT{} at GPIO-Pin: {}".format(self.sensor_id, self.type, self.GPIO_pin)


def aggregate_decorator(func):
    """
    Wraps aggregate functions in HygroTempData class.
    :param func: function
        function that takes a HygroTempData Queryset and returns aggregated data as dict
    :return: func
    """
    def wrapper(dt_from, dt_until, *sensor_ids):
        """
        Calculates aggregations
        :param dt_from: datetime
        :param dt_until: datetime
        :param sensor_ids: int
        :return: dict
        """
        result_data = []
        for sensor_id in sensor_ids:
            period_data = HygroTempData.data_period(dt_from, dt_until, sensor_id)
            aggr = func(period_data)
            aggr['sensor_id'] = sensor_id
            result_data.append(aggr)
        return result_data
    return wrapper


class HygroTempData(models.Model):
    humidity = models.DecimalField(max_digits=4, decimal_places=2)
    temperature = models.DecimalField(max_digits=4, decimal_places=2)
    timestamp = models.DateTimeField()
    sensor = models.ForeignKey(SensorSettings, models.CASCADE, default=-1)

    @staticmethod
    def data_period(dt_from, dt_until, sensor_id):
        """
        Returns data between dt_from and dt_until from the given Sensor
        :param dt_from: datetime
        :param dt_until: datetime
        :param sensor_id: int
        :return: Queryset
        """
        lt_exclude = HygroTempData.objects.filter(sensor_id=sensor_id).exclude(timestamp__lt=dt_from)
        return lt_exclude.exclude(timestamp__gt=dt_until)

    @staticmethod
    def mean_from_set(period_data):
        """
        Returns the mean of humidity and temperature from the given Queryset
        :param period_data: Queryset
        :return: dict
            dict contains keys temperature__avg and humidity__avg
        """
        return period_data.aggregate(Avg('temperature'), Avg('humidity'))

    @staticmethod
    def max_from_set(period_data):
        return period_data.aggregate(Max('temperature'), Max('humidity'))

    @staticmethod
    def min_from_set(period_data):
        return period_data.aggregate(Min('temperature'), Min('humidity'))

    @staticmethod
    def latest_data(sensor_id):
        return HygroTempData.objects.filter(sensor_id=sensor_id).latest('timestamp')

