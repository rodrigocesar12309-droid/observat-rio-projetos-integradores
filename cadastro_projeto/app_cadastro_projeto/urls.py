from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('cadastro/', views.cadastrar_usuario, name='cadastro'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.fazer_logout, name='logout'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),
    path('perfil/desativar/', views.desativar_conta, name='desativar_conta'),
    path('projetos/criar/', views.criar_projeto, name='criar_projeto'),
    path('projetos/editar/<int:projeto_id>/', views.editar_projeto, name='editar_projeto'),
    path('projetos/deletar/<int:projeto_id>/', views.deletar_projeto, name='deletar_projeto'),
]