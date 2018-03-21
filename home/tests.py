from django.test import TestCase
from .models import RelaisSettings
from .utils import validate_sunset, sunrise_sunset
from datetime import datetime, timedelta
# Create your tests here.


class RelayTestCase(TestCase):
    def setUp(self):
        RelaisSettings.objects.create(name="Pumpe", GPIO_pin=1, description="Wasserpumpe für Kühlung",
                                      relais_id=1, state=False)
        RelaisSettings.objects.create(name="Lüfter", GPIO_pin=2, description="Radiator Kühlung", relais_id=2, state=False)

    def test_pin_checkup(self):
        pins = RelaisSettings.pin_checkup('pump', 'fan')
        pins_empty = RelaisSettings.pin_checkup('light')
        self.assertTrue('pump' in pins)
        self.assertTrue('fan' in pins)
        self.assertFalse('light' in pins)
        self.assertFalse(pins_empty)


class ValidateDateCase(TestCase):
    def setUp(self):
        self.sunset = sunrise_sunset()
        dt = datetime.now()
        self.limit_dt = datetime(year=dt.year, month=dt.month, day=dt.day, hour=21, minute=0, second=0, microsecond=0)
        self.td = timedelta(hours=1)
        self.td_true = timedelta(seconds=15)
        self.td_true30 = timedelta(seconds=30)

    def test_validate_sunset(self):
        self.assertTrue('sunset' in self.sunset)
        sunset_dt = self.sunset['sunset']
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

