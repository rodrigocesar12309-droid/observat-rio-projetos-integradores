from django.urls import path
from . import views

urlpatterns = [
    # Tela de login / inicial
    path('', views.home, name='home'),
    
    # Rota que o modal do Administrador usa para enviar os dados de cadastro
    path('cadastro/', views.cadastrar_usuario, name='cadastro'),
    
    # Rota ÚNICA do Dashboard (a view decide se renderiza o dashboard.html ou dashboard_admin.html)
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Sistema de logout
    path('logout/', views.fazer_logout, name='logout'),
    
    # Rotas de Perfil
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),
    path('perfil/desativar/', views.desativar_conta, name='desativar_conta'),
    
    # CRUD de Projetos
    path('projetos/criar/', views.criar_projeto, name='criar_projeto'),
    path('projetos/editar/<int:projeto_id>/', views.editar_projeto, name='editar_projeto'),
    path('projetos/deletar/<int:projeto_id>/', views.deletar_projeto, name='deletar_projeto'),
    
    # Endpoints da API REST
    path('api/usuarios/', views.api_usuarios, name='api_usuarios'),
    path('api/projetos/', views.api_projetos, name='api_projetos'),
    path('api/projetos/<int:projeto_id>/', views.api_projeto_detalhe, name='api_projeto_detalhe'),
]