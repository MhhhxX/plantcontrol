import Adafruit_DHT
from datetime import datetime
from .models import HygroTempData
from .models import SensorSettings


class Sensor(object):
    __instance = None

    def __new__(cls):
        if Sensor.__instance is None:
            Sensor.__instance = object.__new__(cls)
        # initialize members here
        return Sensor.__instance

    def read(self, sensor_id=0):
        if not self.check_sensor(sensor_id):
            raise SensorException(sensor_id)
        sensor_type, pin = self.get_sensor_conf(sensor_id)
        humidity, temperature = Adafruit_DHT.read_retry(sensor_type, pin)
        if humidity is None or temperature is None:
            return self.latest_db_data(sensor_id)
        return HygroTempData(sensor_id=sensor_id, humidity=humidity, temperature=temperature, timestamp=datetime.now())

    def list_sensors(self):
        for sensor in SensorSettings.objects.all():
            print(str(sensor))

    def check_sensor(self, sensor_id):
        if sensor_id not in SensorSettings.objects.order_by("sensor_id"):
            return False
        return True

    def get_sensor_conf(self, sensor_id):
        if not self.check_sensor(sensor_id=sensor_id):
            raise SensorException(sensor_id)
        sensor = SensorSettings.objects.get(sensor_id=sensor_id)
        return sensor.type, sensor.pin

    def latest_db_data(self, sensor_id):
        return HygroTempData.objects.filter(sensor_id=sensor_id).latest('timestamp')

    def read_all(self):
        data = []
        for sensor in SensorSettings.objects.all():
            humidity, temperature = Adafruit_DHT.read_retry(sensor.type, sensor.GPIO_pin)
            if humidity is None or temperature is None:
                data.append(self.latest_db_data(sensor.sensor_id))
            else:
                data.append(HygroTempData(sensor_id=sensor.sensor_id, humidity=humidity, temperature=temperature,
                                          timestamp=datetime.now()))
        return data


class SensorException(Exception):
    def __init__(self, sensor_id):
        self.sensor_id = sensor_id

    def __str__(self):
        return "Sensor with Id {} is not configured".format(self.sensor_id)
