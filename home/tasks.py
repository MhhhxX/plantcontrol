import RPi.GPIO as GPIO

from django.core.exceptions import ObjectDoesNotExist
from huey import crontab
from huey.contrib.djhuey import db_periodic_task, periodic_task, task
from .models import HygroTempData, SensorSettings, RelaisSettings
from .sensor import Sensor
from .utils import validate_sunset, error_pin

sensor = Sensor()
try:
    light_pin = RelaisSettings.objects.get(name='Licht').GPIO_pin
except ObjectDoesNotExist:
    light_pin = -1
try:
    pump_pin = RelaisSettings.objects.get(name='Pumpe').GPIO_pin
except ObjectDoesNotExist:
    pump_pin = -1
try:
    fan_pin = RelaisSettings.objects.get(name='Lüfter').GPIO_pin
except ObjectDoesNotExist:
    fan_pin = -1
sensor_id = 0
temp_limit = 14.0


@db_periodic_task(crontab(minute='*/10', hour='20-23,0-7'))
def water_cooling():
    if not error_pin(('pump', pump_pin), ('fan', fan_pin)):
        return
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
    if not error_pin(('light', light_pin)):
        return
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(light_pin, GPIO.OUT)
    GPIO.output(light_pin, 1)


@db_periodic_task(crontab(hour='21', minute='0'))
def daily_light_shutdown():
    if not error_pin(('light', light_pin)):
        return
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(light_pin, GPIO.OUT)
    GPIO.output(light_pin, 0)


@task()
def airing_shutdown():
    if not error_pin(('fan', fan_pin)):
        return
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(fan_pin, GPIO.OUT)
    GPIO.output(fan_pin, 0)


@periodic_task(crontab(hour='8', minute='0'))
def daily_airing():
    if not error_pin(('fan', fan_pin)):
        return
    airing_shutdown.schedule(delay=1800, convert_utc=False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(fan_pin, GPIO.OUT)
    GPIO.output(fan_pin, 1)
