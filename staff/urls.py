from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("add-food/", views.add_food, name="add_food"),
    path("edit-food/<int:food_id>/", views.edit_food, name="edit_food"),
]