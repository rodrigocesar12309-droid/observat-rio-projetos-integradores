from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'), # Sua página inicial com o login
    path('cadastro/', views.cadastrar_usuario, name='cadastro'), # Nova página de cadastro
]