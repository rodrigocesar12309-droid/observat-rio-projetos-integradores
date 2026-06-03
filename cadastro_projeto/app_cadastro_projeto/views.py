from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import CadastroForm, AtualizarPerfilForm
from .models import PerfilUsuario, ProjetoUsuario, LogAtividade
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import UsuarioSerializer, ProjetoSerializer


def obter_conceito(nota):
    if nota >= 9.0: return "Excelente"
    elif nota >= 7.0: return "Bom"
    elif nota >= 5.0: return "Suficiente"
    else: return "Insuficiente"


# ─────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
        if user is not None:
            login(request, user)
            LogAtividade.registrar(user, 'login', f'{user.email} fez login.')
            return redirect('dashboard')
        else:
            messages.error(request, "E-mail ou senha incorretos.")
    return render(request, 'usuarios/home.html')


def fazer_logout(request):
    if request.user.is_authenticated:
        LogAtividade.registrar(request.user, 'logout', f'{request.user.email} saiu do sistema.')
    logout(request)
    return redirect('home')


# ─────────────────────────────────────────
# CADASTRO E GERENCIAMENTO DE USUÁRIOS
# ─────────────────────────────────────────

@login_required(login_url='home')
def cadastrar_usuario(request):
    perfil = PerfilUsuario.buscar_por_usuario(request.user)
    if not perfil or perfil.tipo_usuario != 'administracao':
        messages.error(request, 'Acesso negado: apenas coordenadores podem cadastrar usuários.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = CadastroForm(request.POST)
        email = request.POST.get('email', '').strip().lower()
        tipo_usuario = request.POST.get('tipo_usuario', 'aluno')

        if User.objects.filter(username=email).exists():
            messages.error(request, 'Este e-mail já está cadastrado!')
            return redirect('dashboard')

        if form.is_valid():
            user = form.save(commit=False)
            user.username = email
            user.email = email
            user.set_password(form.cleaned_data['password'])
            user.first_name = form.cleaned_data['nome_completo']
            user.save()

            PerfilUsuario.criar(
                user=user,
                tipo_usuario=tipo_usuario,
                matricula=form.cleaned_data.get('matricula'),
                telefone=form.cleaned_data.get('telefone'),
            )

            LogAtividade.registrar(request.user, 'create', f'Coordenador {request.user.email} cadastrou {user.email} como {tipo_usuario}.')
            messages.success(request, f'Usuário {user.first_name} ({tipo_usuario}) cadastrado com sucesso!')
        else:
            messages.error(request, 'Erro ao cadastrar usuário.')
    return redirect('dashboard')


@login_required(login_url='home')
def gerenciar_usuarios(request):
    perfil = PerfilUsuario.buscar_por_usuario(request.user)
    if not perfil or perfil.tipo_usuario != 'administracao':
        messages.error(request, 'Acesso negado: apenas coordenadores podem gerenciar usuários.')
        return redirect('dashboard')

    usuarios = PerfilUsuario.objects.select_related('user').all()
    return render(request, 'usuarios/gerenciar_usuarios.html', {'usuarios': usuarios})


@login_required(login_url='home')
def desativar_usuario(request, usuario_id):
    perfil = PerfilUsuario.buscar_por_usuario(request.user)
    if not perfil or perfil.tipo_usuario != 'administracao':
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard')

    usuario = get_object_or_404(User, id=usuario_id)
    usuario.is_active = False
    usuario.save()
    LogAtividade.registrar(request.user, 'delete', f'Coordenador desativou {usuario.email}.')
    messages.success(request, f'Usuário {usuario.email} desativado com sucesso!')
    return redirect('gerenciar_usuarios')


# ─────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────

@login_required(login_url='home')
def dashboard(request):
    perfil = PerfilUsuario.buscar_por_usuario(request.user)

    if perfil and perfil.tipo_usuario == 'administracao':
        projetos = ProjetoUsuario.objects.filter(ativo=True)
        melhores_projetos = projetos.exclude(nota__isnull=True).order_by('-nota')[:3]
        form_cadastro = CadastroForm()
        template_alvo = 'usuarios/dashboard_admin.html'
    else:
        projetos = ProjetoUsuario.objects.filter(usuario=request.user, ativo=True)
        melhores_projetos = projetos.exclude(nota__isnull=True).order_by('-nota')[:3]
        form_cadastro = None
        template_alvo = 'usuarios/dashboard.html'

    total = projetos.count()
    aprovados = projetos.filter(status='aprovado').count()
    em_avaliacao = projetos.filter(status='em_avaliacao').count()

    notas = [p.nota for p in projetos if p.nota is not None]
    media_numerica = sum(notas) / len(notas) if notas else 0
    conceito_final = obter_conceito(media_numerica) if notas else '-'

    contexto = {
        'usuario': request.user,
        'perfil': perfil,
        'projetos': projetos,
        'melhores_projetos': melhores_projetos,
        'total': total,
        'aprovados': aprovados,
        'em_avaliacao': em_avaliacao,
        'media_conceito': conceito_final,
        'form': form_cadastro,
    }
    return render(request, template_alvo, contexto)


# ─────────────────────────────────────────
# CRUD PROJETOS
# ─────────────────────────────────────────

@login_required(login_url='home')
def criar_projeto(request):
    if request.method == 'POST':
        ProjetoUsuario.objects.create(
            usuario=request.user,
            titulo=request.POST.get('titulo'),
            descricao=request.POST.get('descricao'),
            categoria=request.POST.get('categoria', ''),
            semestre=request.POST.get('semestre', ''),
            tags=request.POST.get('tags', ''),
            link_repositorio=request.POST.get('link_repositorio') or None,
            link_demo=request.POST.get('link_demo') or None,
        )
        LogAtividade.registrar(request.user, 'create', 'Projeto criado.')
        messages.success(request, 'Projeto criado com sucesso!')
    return redirect('dashboard')


@login_required(login_url='home')
def editar_projeto(request, projeto_id):
    projeto = get_object_or_404(ProjetoUsuario, id=projeto_id, usuario=request.user)
    if request.method == 'POST':
        projeto.titulo = request.POST.get('titulo', projeto.titulo)
        projeto.descricao = request.POST.get('descricao', projeto.descricao)
        projeto.categoria = request.POST.get('categoria', projeto.categoria)
        projeto.semestre = request.POST.get('semestre', projeto.semestre)
        projeto.tags = request.POST.get('tags', projeto.tags)
        projeto.link_repositorio = request.POST.get('link_repositorio') or None
        projeto.link_demo = request.POST.get('link_demo') or None
        projeto.save()
        LogAtividade.registrar(request.user, 'update', f'Projeto "{projeto.titulo}" editado.')
        messages.success(request, 'Projeto atualizado com sucesso!')
        return redirect('dashboard')
    return render(request, 'usuarios/editar_projeto.html', {'projeto': projeto})


@login_required(login_url='home')
def deletar_projeto(request, projeto_id):
    projeto = get_object_or_404(ProjetoUsuario, id=projeto_id, usuario=request.user)
    if request.method == 'POST':
        projeto.ativo = False
        projeto.save()
        LogAtividade.registrar(request.user, 'delete', f'Projeto "{projeto.titulo}" removido.')
        messages.success(request, 'Projeto removido.')
    return redirect('dashboard')


# ─────────────────────────────────────────
# PERFIL
# ─────────────────────────────────────────

@login_required(login_url='home')
def editar_perfil(request):
    perfil = get_object_or_404(PerfilUsuario, user=request.user)
    if request.method == 'POST':
        form = AtualizarPerfilForm(request.POST, instance=perfil)
        if form.is_valid():
            form.save()
            LogAtividade.registrar(request.user, 'update', 'Perfil atualizado.')
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('dashboard')
    else:
        form = AtualizarPerfilForm(instance=perfil)
    return render(request, 'usuarios/editar_perfil.html', {'form': form, 'perfil': perfil})


@login_required(login_url='home')
def desativar_conta(request):
    if request.method == 'POST':
        usuario = request.user
        usuario.is_active = False
        usuario.save()
        LogAtividade.registrar(usuario, 'delete', f'Conta {usuario.email} desativada.')
        logout(request)
        messages.success(request, 'Conta desativada com sucesso.')
        return redirect('home')
    return render(request, 'usuarios/desativar_conta.html')

# ─────────────────────────────────────────
# RELATÓRIO USUARIOS
# ─────────────────────────────────────────

@login_required(login_url='home')
def relatorio_usuarios(request):
    perfil = PerfilUsuario.buscar_por_usuario(request.user)
    if not perfil or perfil.tipo_usuario != 'administracao':
        messages.error(request, 'Acesso negado: apenas coordenadores podem visualizar o relatório.')
        return redirect('dashboard')

    usuarios = PerfilUsuario.objects.select_related('user').all()
    return render(request, 'usuarios/relatorio_usuarios.html', {'usuarios': usuarios})
# ─────────────────────────────────────────
# EDITAR USUARIO
# ─────────────────────────────────────────
@login_required(login_url='home')
def editar_usuario(request, usuario_id):
    perfil_coord = PerfilUsuario.buscar_por_usuario(request.user)
    if not perfil_coord or perfil_coord.tipo_usuario != 'administracao':
        messages.error(request, 'Acesso negado: apenas coordenadores podem editar usuários.')
        return redirect('dashboard')

    usuario = get_object_or_404(User, id=usuario_id)
    perfil = get_object_or_404(PerfilUsuario, user=usuario)

    if request.method == 'POST':
        form = AtualizarPerfilForm(request.POST, instance=perfil)
        if form.is_valid():
            form.save()
            usuario.first_name = form.cleaned_data.get('nome_completo', usuario.first_name)
            usuario.save()
            LogAtividade.registrar(request.user, 'update', f'Coordenador editou {usuario.email}.')
            messages.success(request, f'Usuário {usuario.email} atualizado com sucesso!')
            return redirect('relatorio_usuarios')
    else:
        form = AtualizarPerfilForm(instance=perfil)

    return render(request, 'usuarios/editar_usuario.html', {'form': form, 'usuario': usuario})



# ─────────────────────────────────────────
# API REST
# ─────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_usuarios(request):
    usuarios = User.objects.all()
    serializer = UsuarioSerializer(
        usuarios,
        many=True
    )
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_projetos(request):
    projetos = ProjetoUsuario.objects.filter(
        ativo=True
    )

    serializer = ProjetoSerializer(
        projetos,
        many=True
    )

    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_projeto_detalhe(request, projeto_id):
    projeto = get_object_or_404(
        ProjetoUsuario,
        id=projeto_id
    )

    serializer = ProjetoSerializer(projeto)

    return Response(serializer.data)