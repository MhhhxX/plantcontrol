from django.test import TestCase
from .models import RelaySettings, HygroTempData, SensorSettings, device_names
from .utils import validate_sunset, sunrise_sunset
from .tasks import gpio_switch
from datetime import datetime, timedelta
import time
import pytz
# Create your tests here.


class RelayTestCase(TestCase):
    def setUp(self):
        RelaySettings.objects.create(name="Pumpe", GPIO_pin=1, description="Wasserpumpe für Kühlung",
                                     relay_id=1, state=False)
        RelaySettings.objects.create(name="Lüfter", GPIO_pin=2, description="Radiator Kühlung", relay_id=2, state=False)

    def test_pin_checkup(self):
        pins = RelaySettings.pin_checkup('pump', 'fan')
        pins_empty = RelaySettings.pin_checkup('light')
        self.assertTrue('pump' in pins)
        self.assertTrue('fan' in pins)
        self.assertFalse('light' in pins)
        self.assertFalse(pins_empty)


class ValidateDateCase(TestCase):
    def setUp(self):
        self.sunset = sunrise_sunset()
        dt = datetime.now()
        self.sunset1 = sunrise_sunset(year=dt.year, month=dt.month, day=dt.day+1)
        self.limit_dt = datetime(year=dt.year, month=dt.month, day=dt.day, hour=21, minute=0, second=0, microsecond=0)
        self.limit_dt1 = datetime(year=dt.year, month=dt.month, day=dt.day+1, hour=21, minute=0, second=0, microsecond=0)
        self.td = timedelta(hours=1)
        self.td_true = timedelta(seconds=15)
        self.td_true30 = timedelta(seconds=30)

    def test_validate_sunset(self):
        self.assertTrue('sunset' in self.sunset)
        sunset_dt = self.sunset['sunset']
        sunset_dt1 = self.sunset1['sunset']
        sunset_plus_one = sunset_dt + self.td
        sunset_minus_one = sunset_dt - self.td
        sunset_plus_15sec = sunset_dt + self.td_true
        sunset_minus_30sec = sunset_dt - self.td_true30
        validate_date = validate_sunset()
        if sunset_dt <= self.limit_dt:
            self.assertTrue(validate_date(sunset_dt))
            self.assertTrue(validate_date(sunset_plus_15sec))
            self.assertTrue(validate_date(sunset_minus_30sec))
            self.assertFalse(validate_date(sunset_plus_one))
            self.assertFalse(validate_date(sunset_minus_one))
        else:
            self.assertFalse(validate_date(sunset_dt))
        if sunset_dt1 <= self.limit_dt1:
            self.assertTrue(validate_date(sunset_dt1))
            self.assertTrue(validate_date(sunset_dt1 + self.td_true))
            self.assertTrue(validate_date(sunset_dt1 + self.td_true30))
            self.assertFalse(validate_date(sunset_dt1 + self.td))
            self.assertFalse(validate_date(sunset_dt1 - self.td))
        else:
            self.assertFalse(validate_date(sunset_dt1))


class HygroTempCase(TestCase):
    def setUp(self):
        # parameter tzinfo may cause problems with python <3.6
        self.dt1 = datetime(2018, 1, 1, 15, 43, 32, 0, tzinfo=pytz.UTC)
        self.dt2 = datetime(2018, 1, 2, 12, 6, 14, 87, tzinfo=pytz.UTC)
        self.dt3 = datetime(2018, 1, 3, 5, 25, 35, 0, tzinfo=pytz.UTC)
        HygroTempData.objects.create(sensor_id=0, humidity=64.73, temperature=23.21, timestamp=self.dt1)
        HygroTempData.objects.create(sensor_id=0, humidity=98.32, temperature=21.75, timestamp=self.dt2)
        HygroTempData.objects.create(sensor_id=0, humidity=76.44, temperature=15.82, timestamp=self.dt3)
        HygroTempData.objects.create(sensor_id=1, humidity=76.44, temperature=15.82, timestamp=self.dt3)

    def test_mean(self):
        means = HygroTempData.mean_from_set(self.dt1, self.dt3, 0)
        means1 = HygroTempData.mean_from_set(self.dt1, self.dt3, 0, 1)
        self.assertEqual(float(means[0]['humidity__avg']), 79.83)
        self.assertEqual(float(means[0]['temperature__avg']), 20.26)
        self.assertEqual(float(means1[0]['humidity__avg']), 79.83)
        self.assertEqual(float(means1[0]['temperature__avg']), 20.26)
        self.assertEqual(float(means1[1]['humidity__avg']), 76.44)
        self.assertEqual(float(means1[1]['temperature__avg']), 15.82)

    def test_latest_data(self):
        latest = HygroTempData.latest_data(0)
        self.assertEqual(latest.timestamp, self.dt3)


class GpioTestCase(TestCase):
    def setUp(self):
        try:
            import RPi.GPIO as GPIO
        except RuntimeError:
            self.skipTest('Device does not support GPIO. Test canceled')

    def test_gpio_switch(self):
        pins = RelaySettings.pin_checkup(*device_names)
        gpio_switch(pins.values(), state=1)
        time.sleep(3)
        gpio_switch(pins.values(), state=0)
