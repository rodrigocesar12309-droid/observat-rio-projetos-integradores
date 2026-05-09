from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import CadastroForm, AtualizarPerfilForm
from .models import PerfilUsuario, ProjetoUsuario, LogAtividade


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
    LogAtividade.registrar(request.user, 'logout', f'{request.user.email} saiu do sistema.')
    logout(request)
    return redirect('home')


# ─────────────────────────────────────────
# CREATE - Cadastro
# ─────────────────────────────────────────

def cadastrar_usuario(request):
    if request.method == 'POST':
        form = CadastroForm(request.POST)
        email = request.POST.get('email')
        if User.objects.filter(username=email).exists():
            messages.error(request, 'Você já tem cadastro no sistema!')
            return render(request, 'usuarios/cadastro.html', {'form': form})
        if form.is_valid():
            user = form.save(commit=False)
            user.username = form.cleaned_data['email']
            user.email = form.cleaned_data['email']
            user.set_password(form.cleaned_data['password'])
            user.first_name = form.cleaned_data['nome_completo']
            user.save()
            PerfilUsuario.criar(
                user=user,
                tipo_usuario=form.cleaned_data.get('tipo_usuario', 'aluno'),
                matricula=form.cleaned_data.get('matricula'),
                telefone=form.cleaned_data.get('telefone'),
            )
            LogAtividade.registrar(user, 'create', f'Usuário {user.email} cadastrado.')
            messages.success(request, "Cadastro realizado com sucesso! Faça login para acessar.")
            return redirect('home')
    else:
        form = CadastroForm()
    return render(request, 'usuarios/cadastro.html', {'form': form})


# ─────────────────────────────────────────
# READ - Dashboard
# ─────────────────────────────────────────

@login_required(login_url='home')
def dashboard(request):
    projetos = ProjetoUsuario.objects.filter(usuario=request.user, ativo=True)
    total = projetos.count()
    aprovados = projetos.filter(status='aprovado').count()
    em_avaliacao = projetos.filter(status='em_avaliacao').count()

    notas = [p.nota for p in projetos if p.nota is not None]
    media_numerica = sum(notas) / len(notas) if notas else 0
    conceito_final = obter_conceito(media_numerica) if notas else '-'

    perfil = PerfilUsuario.buscar_por_usuario(request.user)

    contexto = {
        'usuario': request.user,
        'perfil': perfil,
        'projetos': projetos,
        'total': total,
        'aprovados': aprovados,
        'em_avaliacao': em_avaliacao,
        'media_conceito': conceito_final,
    }
    return render(request, 'usuarios/dashboard.html', contexto)


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
        LogAtividade.registrar(request.user, 'create', f'Projeto criado.')
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
        messages.success(request, 'Projeto atualizado!')
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
            perfil.atualizar(
                tipo_usuario=form.cleaned_data.get('tipo_usuario'),
                matricula=form.cleaned_data.get('matricula'),
                telefone=form.cleaned_data.get('telefone'),
            )
            request.user.first_name = form.cleaned_data.get('nome_completo', request.user.first_name)
            request.user.save()
            LogAtividade.registrar(request.user, 'update', f'Perfil atualizado.')
            messages.success(request, "Perfil atualizado com sucesso!")
            return redirect('dashboard')
    else:
        form = AtualizarPerfilForm(instance=perfil)
    return render(request, 'usuarios/editar_perfil.html', {'form': form, 'perfil': perfil})


@login_required(login_url='home')
def desativar_conta(request):
    if request.method == 'POST':
        perfil = get_object_or_404(PerfilUsuario, user=request.user)
        LogAtividade.registrar(request.user, 'delete', f'Conta de {request.user.email} desativada.')
        perfil.desativar()
        logout(request)
        messages.success(request, "Sua conta foi desativada.")
        return redirect('home')
    return render(request, 'usuarios/confirmar_exclusao.html')