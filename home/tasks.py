import RPi.GPIO as GPIO
import math
from math import floor, sin, cos, tan, atan, asin, acos
import time

from datetime import datetime
from huey import crontab
from huey.contrib.djhuey import db_periodic_task
from .models import HygroTempData, SensorSettings
from datetime import datetime
from .sensor import Sensor

sensor = Sensor()
temp_limit = 14.0
pump_pin = 2
fan_pin = 3
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
    GPIO.cleanup()


@db_periodic_task(crontab(minute='*/5'))
def hygro_temp_logging():
    data = sensor.read_all()
    for d in data:
        d.save()


def sunrise_sunset(day=int(datetime.now().day), month=int(datetime.now().month), year=int(datetime.now().year),
                   latitude=48.4601, longitude=11.1276, angle='official', rise_or_set='both', utc=False):
    """
    calculates and returns either sunrise or sunset times or both values
    
    :param day: int
        day of given month
    :param month: int
    :param year: int
    :param latitude: float
    :param longitude: float
    :param angle: str
        must be in ['official', 'nautical', 'civil', 'astronomical']
    :param rise_or_set: str
        value in ['riseonly', setonly, both]
    :param utc: boolean
        when False sunset/sunrise will returned in localtime
    :return: dict
        contains datetime objects with 'sunset' and/or 'sunrise' keys or a str key with never
        dict may contain str values for error handling under key 'error'
    """
    types = {'official': 90.5, 'nautical': 102, 'civil': 96, 'astronomical': 108}
    mode = ['riseonly', 'setonly', 'both']
    if angle not in types:
        return {'error': 'Can not assign given angle: ' + str(angle) + '. Type must be in: ' + str(types)}
    if rise_or_set not in mode:
        return {'error': 'This mode does not exist: ' + str(rise_or_set) + '. Must be in: ' + str(mode)}

    zenit_radians = to_radians(types[angle])
    latitude_radians = to_radians(latitude)

    # 1. calculation for the day of the year
    N1 = floor(275 * month / 9)
    N2 = floor((month + 9) / 12)
    N3 = (1 + floor((year - 4 * floor(year / 4) + 2) / 3))
    N = N1 - (N2 * N3) + day - 30

    # 2. longitude conversion to hour and approximate time
    lng_hour = longitude / 15

    if rise_or_set:
        t = N + ((6 - lng_hour) / 24)
    else:
        t = N + ((18 - lng_hour) / 24)

    # 3. Sun's mean
    M = (0.9856 * t) - 3.289
    M_r = to_radians(M)

    # 4. Sun's true longitude
    L = M + (1.916 * sin(M_r)) + (0.02 * sin(2 * M_r)) + 282.634
    L_r = to_radians(adjust_value(L))
    L_a = adjust_value(L)

    # 5a. Sun's right ascension
    RA = to_degree(atan(0.91764 * tan(L_r)))
    RA_a = adjust_value(RA)

    # 5b. right ascension value need to be in the same quadrant as L
    L_quadrant = (floor(L_a / 90)) * 90
    RA_quadrant = (floor(RA_a / 90)) * 90
    RA_a = RA_a + (L_quadrant - RA_quadrant)

    # 5c. right ascension value needs to be converted into hours
    RA_a = RA_a / 15

    # 6. Sun's declination
    sin_dec = 0.39782 * sin(L_r)
    cos_dec = cos(asin(sin_dec))

    # 7a. Sun's local hour angle
    cos_h = (cos(zenit_radians) - (sin_dec * sin(latitude_radians))) / \
            (cos_dec * cos(latitude_radians))

    if cos_h > 1:
        return {'sunrise': 'never'}
    if cos_h < -1:
        return {'sunset': 'never'}

    # 7b. calculating H and convert into hours
    set_hour = None
    if rise_or_set == 'riseonly':
        H = 360 - to_degree(acos(cos_h))
    if rise_or_set == 'setonly':
        H = to_degree(acos(cos_h))
    if rise_or_set == 'both':
        H = 360 - to_degree(acos(cos_h))
        set_hour = to_degree(acos(cos_h))
    H = H / 15

    # 8.local mean time of rising/setting
    T = H + RA_a - (0.06571 * t) - 6.622

    # 9. adjust back to UTC
    if set_hour is not None:
        set_hour = set_hour / 15
        set_T = set_hour + RA_a - (0.06571 * t) - 6.622
        set_UT = adjust_value24(set_T - lng_hour)
        if not utc:
            set_UT = set_UT - time.timezone/3600
        extracted_set_time = extract_time(set_UT)
        print(str(extracted_set_time))
        set_datetime = datetime(year, month, day, extracted_set_time['hours'], extracted_set_time['minutes'],
                                extracted_set_time['seconds'], extracted_set_time['microseconds'])
    UT = T - lng_hour
    sun_time = adjust_value24(UT)
    if not utc:
        sun_time = sun_time - time.timezone/3600
    extracted_time = extract_time(sun_time)
    calc_datetime = datetime(year, month, day, extracted_time['hours'], extracted_time['minutes'],
                             extracted_time['seconds'], extracted_time['microseconds'])
    if rise_or_set == 'riseonly':
        return {'sunrise': calc_datetime}
    if rise_or_set == 'setonly':
        return {'sunset': calc_datetime}
    return {'sunrise': calc_datetime, 'sunset': set_datetime}


def extract_time(time_value):
    hours = int(time_value)
    minute_portion = (time_value - floor(time_value)) * 60
    minutes = int(minute_portion)
    second_portion = (minute_portion - floor(minute_portion)) * 60
    seconds = int(second_portion)
    microseconds = int((second_portion - floor(second_portion)) * 1000000)
    return {'hours': hours, 'minutes': minutes, 'seconds': seconds, 'microseconds': microseconds}


def to_radians(x):
    return x * (math.pi / 180)


def to_degree(x):
    return x * (180 / math.pi)


def adjust_value(x):
    if x < 0.0:
        return x + 360
    if x > 360.0:
        return x - 360
    return x


def adjust_value24(x):
    if x < 0.0:
        return x + 24.0
    if x > 24.0:
        return x - 24.0
    return x
