from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^new/$', views.new, name='new'),
    url(r'^resource/(?P<resource_id>\d+)$', views.resource, name='resource'),

    url(r'^new/action$', views.create_resource, name='create_resource'),
    url(r'^resource/update/(?P<resource_id>\d+)$', views.update_resource, name='update_resource'),
    url(r'^resource/create/(?P<resource_id>\d+)$', views.create_reservation, name='create_reservation'),
    url(r'^reservation/delete/(?P<reservation_id>\d+)$', views.delete_reservation, name='delete_reservation'),
]
