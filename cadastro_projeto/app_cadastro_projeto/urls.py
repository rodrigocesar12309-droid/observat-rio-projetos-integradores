from django.urls import path
from . import views

urlpatterns = [
    # Tela de login / inicial
    path('', views.home, name='home'),

    # Cadastro de usuários (apenas coordenador)
    path('cadastro/', views.cadastrar_usuario, name='cadastro'),

    # Cadastro de empresa com login (apenas coordenador)
    path('cadastro/empresa/', views.cadastrar_empresa_login, name='cadastrar_empresa_login'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('usuarios/', views.gerenciar_usuarios, name='gerenciar_usuarios'),
    path('relatorio/usuarios/', views.relatorio_usuarios, name='relatorio_usuarios'),
    path('usuarios/editar/<int:usuario_id>/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/desativar/<int:usuario_id>/', views.desativar_usuario, name='desativar_usuario'),
    path('usuarios/ativar/<int:usuario_id>/', views.ativar_usuario, name='ativar_usuario'),

    # Avaliar projetos (professor)
    path('avaliacao/', views.painel_avaliacao, name='painel_avaliacao'),
    path('avaliacao/projeto/<int:projeto_id>/', views.avaliar_projeto, name='avaliar_projeto'),

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

    # Fórum
    path('forum/', views.forum_lista, name='forum_lista'),
    path('forum/novo/', views.forum_novo_topico, name='forum_novo_topico'),
    path('forum/topico/<int:topico_id>/', views.forum_topico, name='forum_topico'),
    path('forum/topico/<int:topico_id>/deletar/', views.forum_deletar_topico, name='forum_deletar_topico'),
    path('forum/resposta/<int:resposta_id>/deletar/', views.forum_deletar_resposta, name='forum_deletar_resposta'),

    # Encerrar / reabrir projeto (admin)
    path('projetos/encerrar/<int:projeto_id>/', views.encerrar_projeto, name='encerrar_projeto'),
    path('projetos/reabrir/<int:projeto_id>/', views.reabrir_projeto, name='reabrir_projeto'),

    # Currículo
    path('curriculo/salvar/', views.salvar_curriculo, name='salvar_curriculo'),
    path('curriculo/aluno/<int:usuario_id>/', views.ver_curriculo_aluno, name='ver_curriculo_aluno'),

    # Página de projetos do aluno
    path('meus-projetos/', views.meus_projetos, name='meus_projetos'),

    # Coordenação — páginas do sidebar
    path('coord/projetos/', views.coord_todos_projetos, name='coord_todos_projetos'),
    path('coord/corpo-docente/', views.coord_corpo_docente, name='coord_corpo_docente'),
    path('coord/mensagens/', views.coord_mensagens, name='coord_mensagens'),
]
