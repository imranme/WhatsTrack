# group_extractor/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.group_input_view, name='group_input'),
    path('api/save-members/', views.save_members_api, name='save_members_api'),
]
