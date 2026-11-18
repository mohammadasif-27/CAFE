from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("add-food/", views.add_food, name="add_food"),
    path("edit-food/<int:food_id>/", views.edit_food, name="edit_food"),
    path("delete-food/<int:food_id>/", views.delete_food, name="delete_food"),
    path("orders/<int:order_id>/complete/", views.complete_order, name="complete_order"),
    path("analytics/", views.analytics, name="analytics"),
]