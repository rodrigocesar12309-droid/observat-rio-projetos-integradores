
from django.urls import path
from app_cadastro_projeto import views
urlpatterns = [
    path('', views.home, name='home'),
]
