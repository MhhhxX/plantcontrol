try:
    import RPi.GPIO as GPIO
    gpio_imported = True
except RuntimeError:
    gpio_imported = False
    print('Can not import RPi.GPIO!')
import random
from .sensor import Sensor

from django.shortcuts import render, get_object_or_404
from datetime import datetime
from django.template import RequestContext, loader
from django.http import HttpResponse, JsonResponse
from .models import RelaySettings, SensorSettings
from .forms import RelayModelForm, SensorModelForm
# Create your views here.


def home(request):
    if gpio_imported:
        check_relay_state()
    context = {'relay': RelaySettings.objects.all(), 'relay_form': RelayModelForm, 'sensor_form': SensorModelForm,
               'sensor': SensorSettings.objects.all()}
    if request.method == 'POST':
        data = request.POST
        if 'sensor_id' in data:
            form = SensorModelForm(data)
        else:
            form = RelayModelForm(data)
        if form.is_valid():
            form.save()
            return render(request, 'home.html', context)
    return render(request, 'home.html', context)


def update_chart(request):
    update = request.GET.get("update_chart") or "undefined"
    if update:
        # not yet implemented
        s = Sensor()
        data = s.read(sensor_id=0, mode='once')
        timestamp = str(data.timestamp.hour) + ":" + str(data.timestamp.minute) + ":" + str(data.timestamp.second)
        # data = randomize_test_data()
        send_data = {'temperature': data.temperature, 'humidity': data.humidity, 'time': timestamp}
        return JsonResponse(send_data)


def randomize_test_data():
    temperature = "{0:.2f}".format(random.uniform(15, 25))
    humidity = "{0:.2f}".format(random.uniform(50, 90))
    cur_time = datetime.now()
    timestamp = "{:02d}:{:02d}:{:02d}".format(int(cur_time.hour), int(cur_time.minute), int(cur_time.second))
    return {'temperature': temperature, 'humidity': humidity, 'timestamp': timestamp}


def delete_relay(request):
    relay_id = request.POST
    RelaySettings.objects.get(relay_id=relay_id['delete_id']).delete()
    context = {'relay': RelaySettings.objects.all(), 'relay_form': RelayModelForm}
    return render(request, 'home.html', context)


def delete_sensor(request):
    sensor_id = request.POST
    SensorSettings.objects.get(sensor_id=sensor_id['delete_id']).delete()
    context = {'relay': RelaySettings.objects.all(), 'relay_form': RelayModelForm}
    return render(request, 'home.html', context)


def switch_relay(request):
    r_id = request.GET.get('relay_id')
    relay = RelaySettings.objects.get(relay_id=r_id)
    GPIO.setup(relay.GPIO_pin, GPIO.OUT)
    if relay.state is False:
        GPIO.output(relay.GPIO_pin, 1)
        relay.state = True
        relay.save()
        return JsonResponse({'state': 1})
    else:
        GPIO.output(relay.GPIO_pin, 0)
        relay.state = False
        relay.save()
        return JsonResponse({'state': 0})


def check_relay_state():
    GPIO.setmode(GPIO.BCM)
    for relay in RelaySettings.objects.all():
        pin = relay.GPIO_pin
        GPIO.setup(pin, GPIO.OUT)
        if GPIO.input(pin) == 0 and relay.state is True:
            relay.state = False
            relay.save()
        if GPIO.input(pin) == 1 and relay.state is False:
            relay.state = True
            relay.save()
