try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print('Can not import RPi.GPIO!')
import random

from django.shortcuts import render, get_object_or_404
from datetime import datetime
from django.template import RequestContext, loader
from django.http import HttpResponse, JsonResponse
from .models import RelaySettings, SensorSettings
from .forms import RelaisModelForm, SensorModelForm
# Create your views here.


def home(request):
    # check_relais_state()
    context = {'relais': RelaySettings.objects.all(), 'relais_form': RelaisModelForm, 'sensor_form': SensorModelForm,
               'sensor': SensorSettings.objects.all()}
    if request.method == 'POST':
        data = request.POST
        if 'sensor_id' in data:
            form = SensorModelForm(data)
        else:
            form = RelaisModelForm(data)
        if form.is_valid():
            form.save()
            return render(request, 'home.html', context)
    return render(request, 'home.html', context)


def update_chart(request):
    update = request.GET.get("update_chart") or "undefined"
    if update:
        # not yet implemented
        # s = Sensor()
        # data = s.read()
        # timestamp = data.timestamp.hour + ":" + data.timestamp.minute + ":" + data.timestamp.second
        data = randomize_test_data()
        send_data = {'temperature': data["temperature"], 'humidity': data["humidity"], 'time': data["timestamp"]}
        return JsonResponse(send_data)


def randomize_test_data():
    temperature = "{0:.2f}".format(random.uniform(15, 25))
    humidity = "{0:.2f}".format(random.uniform(50, 90))
    cur_time = datetime.now()
    timestamp = "{:02d}:{:02d}:{:02d}".format(int(cur_time.hour), int(cur_time.minute), int(cur_time.second))
    return {'temperature': temperature, 'humidity': humidity, 'timestamp': timestamp}


def delete_relais(request):
    relais_id = request.POST
    RelaySettings.objects.get(relais_id=relais_id['delete_id']).delete()
    context = {'relais': RelaySettings.objects.all(), 'relais_form': RelaisModelForm}
    return render(request, 'home.html', context)


def delete_sensor(request):
    sensor_id = request.POST
    SensorSettings.objects.get(sensor_id=sensor_id['delete_id']).delete()
    context = {'relais': RelaySettings.objects.all(), 'relais_form': RelaisModelForm}
    return render(request, 'home.html', context)


def switch_relais(request):
    r_id = request.GET.get('relais_id')
    relais = RelaySettings.objects.get(relais_id=r_id)
    GPIO.setup(relais.GPIO_pin, GPIO.OUT)
    if relais.state is False:
        GPIO.output(relais.GPIO_pin, 1)
        relais.state = True
        relais.save()
        return JsonResponse({'state': 1})
    else:
        GPIO.output(relais.GPIO_pin, 0)
        relais.state = False
        relais.save()
        return JsonResponse({'state': 0})


def check_relais_state():
    GPIO.setmode(GPIO.BCM)
    for relais in RelaySettings.objects.all():
        pin = relais.GPIO_pin
        GPIO.setup(pin, GPIO.OUT)
        if GPIO.input(pin) == 0 and relais.state is True:
            relais.state = False
            relais.save()
        if GPIO.input(pin) == 1 and relais.state is False:
            relais.state = True
            relais.save()
