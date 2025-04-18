from django.urls import path
from . import views

urlpatterns = [
    path('generate_status_tag/', views.generate_status_tag, name='generate_status_tag'),
]
