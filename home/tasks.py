import RPi.GPIO as GPIO

from huey import crontab
from huey.contrib.djhuey import db_periodic_task
from .models import HygroTempData, SensorSettings, RelaisSettings
from .sensor import Sensor
from .utils import validate_sunset

sensor = Sensor()
light_pin = RelaisSettings.objects.get(name='Licht').GPIO_pin
temp_limit = 14.0
pump_pin = 3
fan_pin = 4
sensor_id = 0


@db_periodic_task(crontab(day='', minute='/*5', hour='0-7,20-23'))
def water_cooling():
    GPIO.setmode(GPIO.BCM)
    hygro_temp_data = sensor.read(0)
    if hygro_temp_data.temperature >= temp_limit:
        GPIO.setup([pump_pin, fan_pin], GPIO.OUT)
        GPIO.output([pump_pin, fan_pin], 1)
    else:
        GPIO.setup([pump_pin, fan_pin], GPIO.OUT)
        GPIO.output([pump_pin, fan_pin], 0)


@db_periodic_task(crontab(minute='*/5'))
def hygro_temp_logging():
    data = sensor.read_all()
    for d in data:
        d.save()


@db_periodic_task(validate_sunset())
def light_at_sunset():
    if light_pin:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(light_pin, GPIO.OUT)
        GPIO.output(light_pin, 1)


@db_periodic_task(crontab(hour='21', minute='0'))
def daily_light_shutdown():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(light_pin, GPIO.OUT)
    GPIO.output(light_pin, 0)
