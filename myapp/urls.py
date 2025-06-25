from django.urls import path
from . import views

urlpatterns = [
    path('unauthorized_employees/', views.unauthorized_employees, name='unauthorized_employees'),
    path('projects/', views.projects, name='projects'), 
]
