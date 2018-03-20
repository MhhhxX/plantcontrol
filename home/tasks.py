try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print('Can not import RPi.GPIO!')

from django.core.exceptions import ObjectDoesNotExist
from huey import crontab
from huey.contrib.djhuey import db_periodic_task, periodic_task, task
from .models import HygroTempData, SensorSettings, RelaisSettings
from .sensor import Sensor
from .utils import validate_sunset

device_names = {'fan': 'Lüfter', 'light': 'Licht', 'pump': 'Pumpe'}
sensor = Sensor()
sensor_id = 0
temp_limit = 14.0


@db_periodic_task(crontab(minute='*/10', hour='20-23,0-7'))
def water_cooling():
    pins = pin_checkup('fan', 'pump')
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


@db_periodic_task(validate_sunset())
def light_at_sunset():
    pins = pin_checkup('light')
    if not pins:
        return
    gpio_switch(pins['light'], state=1)


@db_periodic_task(crontab(hour='21', minute='0'))
def daily_light_shutdown():
    pins = pin_checkup('light')
    if not pins:
        return
    gpio_switch(pins['light'], state=0)


@task()
def airing_shutdown():
    pins = pin_checkup('fan')
    if not pins:
        return
    gpio_switch(pins['fan'], state=0)


@periodic_task(crontab(hour='8', minute='0'))
def daily_airing():
    pins = pin_checkup('fan')
    if not pins:
        return
    airing_shutdown.schedule(delay=1800, convert_utc=False)
    gpio_switch(pins['fan'], state=1)


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


def gpio_switch(*pins, state: int):
    if state != 0 and state != 1:
        state = 1
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pins, GPIO.OUT)
    GPIO.output(pins, state)
