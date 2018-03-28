from django.db import models
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
        return "Sensor number: {}, Sensor Type: DHT{}, At GPIO-Pin: {}".format(self.sensor_id, self.type, self.GPIO_pin)


class HygroTempData(models.Model):
    humidity = models.DecimalField(max_digits=4, decimal_places=2)
    temperature = models.DecimalField(max_digits=4, decimal_places=2)
    timestamp = models.DateTimeField()
    sensor = models.ForeignKey(SensorSettings, models.CASCADE, default=-1)

    @staticmethod
    def data_period(dt_from, dt_until, sensor_id):
        lt_exclude = HygroTempData.objects.filter(sensor_id=sensor_id).exclude(timestamp__lt=dt_from)
        return lt_exclude.exclude(timestamp__gt=dt_until)

    @staticmethod
    def mean(dt_from, dt_until, *sensor_ids):
        """
        Returns the mean of humidity and temperature in the given time period
        :param dt_from: datetime
        :param dt_until: datetime
        :param sensor_ids: int
            data is taken from this sensors
        :return: HygroTempData, list
            returns a HygroTempData object if only one sensor is given and otherwise a list
            with HygroTempData objects.
        """
        result_data = []
        hum_mean, temp_mean = 0, 0
        for sensor_id in sensor_ids:
            period_data = HygroTempData.data_period(dt_from, dt_until, sensor_id)
            pd_length = period_data.__len__()

            partial_sum_temp = 0
            partial_sum_hum = 0
            for data in period_data:
                partial_sum_temp += data.temperature
                partial_sum_hum += data.humidity
            temp_mean, hum_mean = partial_sum_temp / pd_length, partial_sum_hum / pd_length
            result_data.append(HygroTempData(sensor_id=sensor_id, temperature=temp_mean, humidity=hum_mean))
        if sensor_ids.__len__() == 1:
            return HygroTempData(sensor_id=sensor_ids[0], humidity=hum_mean, temperature=temp_mean)
        return result_data

    @staticmethod
    def latest_data(sensor_id):
        return HygroTempData.objects.filter(sensor_id=sensor_id).latest('timestamp')

