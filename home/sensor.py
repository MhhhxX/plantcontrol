from django.core.exceptions import ObjectDoesNotExist

try:
    import Adafruit_DHT
except ModuleNotFoundError:
    print("Module Adafruit_DHT not installed!")
from datetime import datetime
from .models import HygroTempData
from .models import SensorSettings


class SensorCacheDecorator:
    def __init__(self):
        self.cache = []

    def cache_hygro_temp_data(self, sensor_id, mode):
        dt_now = datetime.now()
        cache_data = [x for x in self.cache if x.sensor_id == sensor_id]
        if not cache_data:
            new_data = self.func(self, sensor_id=sensor_id, mode=mode)
            self.cache.append(new_data)
            return new_data
        dt1 = cache_data[0].timestamp
        time_diff = (dt_now - dt1).total_seconds()
        if time_diff < 2:
            return cache_data[0]
        new_data = self.func(self, sensor_id=sensor_id, mode=mode)
        index = self.cache.index(cache_data[0])
        self.cache[index] = new_data
        return new_data

    def __call__(self, func):
        self.func = func
        return self.cache_hygro_temp_data


class Sensor(object):
    __instance = None

    def __new__(cls):
        if Sensor.__instance is None:
            Sensor.__instance = object.__new__(cls)
        # initialize members here
        return Sensor.__instance

    @SensorCacheDecorator()
    def read_classic(self, pin, sensor_type, mode):
        if mode == 'once':
            return Adafruit_DHT.read(sensor_type, pin)
        elif mode == 'retry':
            return Adafruit_DHT.read_retry(sensor_type, pin)
        return None, None

    @SensorCacheDecorator()
    def read(self, sensor_id=0, mode='retry'):
        try:
            sensor_type, pin = Sensor.get_sensor_conf(sensor_id=sensor_id)
        except SensorException:
            raise SensorException(sensor_id)
        if mode == 'retry':
            humidity, temperature = Adafruit_DHT.read_retry(sensor_type, pin)
        else:
            humidity, temperature = Adafruit_DHT.read(sensor_type, pin)
        if humidity is None or temperature is None:
            return HygroTempData.latest_data(sensor_id)
        return HygroTempData(sensor_id=sensor_id, humidity=humidity, temperature=temperature, timestamp=datetime.now())

    @staticmethod
    def list_sensors():
        for sensor in SensorSettings.objects.all():
            print(str(sensor))

    @staticmethod
    def get_sensor_conf(sensor_id):
        try:
            sensor = SensorSettings.objects.get(sensor_id=sensor_id)
        except ObjectDoesNotExist:
            raise SensorException(sensor_id)
        return sensor.type, sensor.GPIO_pin

    def read_all(self):
        data = []
        for sensor in SensorSettings.objects.all():
            dht_data = self.read(sensor_id=sensor.sensor_id, mode='retry')
            data.append(dht_data)
        return data


class SensorException(Exception):
    def __init__(self, sensor_id):
        self.sensor_id = sensor_id

    def __str__(self):
        return "Sensor with Id {} is not configured".format(self.sensor_id)
