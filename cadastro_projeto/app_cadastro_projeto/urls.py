from django.urls import path
from . import views

urlpatterns = [
    # Tela de login / inicial
    path('', views.home, name='home'),
    
    # Cadastro de usuários (apenas admin)
    path('cadastro/', views.cadastrar_usuario, name='cadastro'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('usuarios/', views.gerenciar_usuarios, name='gerenciar_usuarios'),
    path('relatorio/usuarios/', views.relatorio_usuarios, name='relatorio_usuarios'),
    path('usuarios/editar/<int:usuario_id>/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/desativar/<int:usuario_id>/', views.desativar_usuario, name='desativar_usuario'),



    
    # Logout
    path('logout/', views.fazer_logout, name='logout'),
    
    # Perfil
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),
    path('perfil/desativar/', views.desativar_conta, name='desativar_conta'),
    
    # CRUD de Projetos
    path('projetos/criar/', views.criar_projeto, name='criar_projeto'),
    path('projetos/editar/<int:projeto_id>/', views.editar_projeto, name='editar_projeto'),
    path('projetos/deletar/<int:projeto_id>/', views.deletar_projeto, name='deletar_projeto'),
    
    # API REST
    path('api/usuarios/', views.api_usuarios, name='api_usuarios'),
    path('api/projetos/', views.api_projetos, name='api_projetos'),
    path('api/projetos/<int:projeto_id>/', views.api_projeto_detalhe, name='api_projeto_detalhe'),
]
