from django.urls import path

from . import views

app_name = 'menu'

urlpatterns = [
    path('foods/<int:food_id>/', views.food_detail, name='food_detail'),
]
