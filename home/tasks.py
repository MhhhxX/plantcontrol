try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print('Can not import RPi.GPIO!')

from huey import crontab
from huey.contrib.djhuey import db_periodic_task, periodic_task, task
from .models import HygroTempData, SensorSettings, RelaySettings
from .sensor import Sensor
from .utils import validate_sunset
from datetime import datetime

sensor = Sensor()
sensor_id = 0
temp_limit = 14.0


@db_periodic_task(crontab(minute='*/10', hour='20-23,0-7'))
def water_cooling():
    pins = RelaySettings.pin_checkup('fan', 'pump')
    if not pins:
        return
    GPIO.setmode(GPIO.BCM)
    hygro_temp_data = sensor.read(0)
    if hygro_temp_data.temperature >= temp_limit:
        GPIO.setup([pins['pump'], pins['fan']], GPIO.OUT)
        GPIO.output([pins['pump'], pins['fan']], 1)
    else:
        GPIO.setup([pins['pump'], pins['fan']], GPIO.OUT)
        GPIO.output([pins['pump'], pins['fan']], 0)


@db_periodic_task(crontab(minute='*/5'))
def hygro_temp_logging():
    data = sensor.read_all()
    for d in data:
        d.save()


@task()
def shutdown(pin):
    pins = RelaySettings.pin_checkup(pin)
    if not pins:
        return
    gpio_switch(pins[pin], state=0)


@db_periodic_task(validate_sunset())
def light_at_sunset():
    dt = datetime.now()
    pins = RelaySettings.pin_checkup('light')
    if not pins:
        return
    gpio_switch(pins['light'], state=1)
    eta = datetime(dt.year, dt.month, dt.day, 21, 0, 0, 0)
    if eta > dt:
        shutdown.schedule(args=('light',), eta=eta, convert_utc=False)
    else:
        print("[Huey, function light_at_sunset]: datetime doesn't lie ahead. Can not schedule shutdown task")


@periodic_task(crontab(hour='8,20', minute='0'))
def daily_airing():
    pins = RelaySettings.pin_checkup('fan')
    if not pins:
        return
    shutdown.schedule(args=('fan',), delay=1800, convert_utc=False)
    gpio_switch(pins['fan'], state=1)


def gpio_switch(*pins, state: int):
    if state != 0 and state != 1:
        state = 1
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pins, GPIO.OUT)
    GPIO.output(pins, state)
