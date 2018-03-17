from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^update_chart/$', views.update_chart, name='update_chart'),
    url(r'^delete_relais/$', views.delete_relais, name='delete_relais'),
    url(r'^delete_sensor/$', views.delete_sensor, name='delete_sensor'),
    url(r'^switch_relais/$', views.switch_relais, name='switch_relais')
]
