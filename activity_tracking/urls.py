from django.urls import path

from . import views

app_name = 'activity_tracking'

urlpatterns = [
    path('heartbeat/', views.heartbeat, name='heartbeat'),
    path('event/', views.client_event, name='event'),
]
