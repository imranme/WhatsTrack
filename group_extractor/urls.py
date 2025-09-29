from django.urls import path
from .views import group_input_view

urlpatterns = [
    path('', group_input_view, name='group_input'),
]
