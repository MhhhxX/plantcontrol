from django.test import TestCase
from .models import RelaisSettings
# Create your tests here.


class RelaisTestCase(TestCase):
    def setUp(self):
        RelaisSettings.objects.create(name="Wasserpumpe", GPIO_pin=1, description="Wasserpumpe für Kühlung",
                                      relais_id=1)
        RelaisSettings.objects.create(name="Lüfter", GPIO_pin=1, description="Radiator Kühlung", relais_id=2)
