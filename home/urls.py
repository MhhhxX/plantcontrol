from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^update_chart/$', views.update_chart, name='update_chart'),
    url(r'^delete_relay/$', views.delete_relay, name='delete_relay'),
    url(r'^delete_sensor/$', views.delete_sensor, name='delete_sensor'),
    url(r'^switch_relay/$', views.switch_relay, name='switch_relay')
]
