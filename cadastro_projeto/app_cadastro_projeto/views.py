from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import CadastroForm, AtualizarPerfilForm
from .models import PerfilUsuario, Projeto, LogAtividade


def obter_conceito(nota):
    if nota >= 9.0:
        return "Excelente"
    elif nota >= 7.0:
        return "Bom"
    elif nota >= 5.0:
        return "Suficiente"
    else:
        return "Insuficiente"


# ─────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        email_login = request.POST.get('username')
        senha_login = request.POST.get('password')

        user = authenticate(request, username=email_login, password=senha_login)

        if user is not None:
            login(request, user)
            # ✅ LOG - Login
            LogAtividade.registrar(user, 'login', f'{user.email} fez login.')
            return redirect('dashboard')
        else:
            messages.error(request, "E-mail ou senha incorretos.")

    return render(request, 'usuarios/home.html')


def fazer_logout(request):
    # ✅ LOG - Logout
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

            # ✅ CREATE - Cria o perfil vinculado ao usuário
            PerfilUsuario.criar(
                user=user,
                tipo_usuario=form.cleaned_data.get('tipo_usuario', 'aluno'),
                matricula=form.cleaned_data.get('matricula'),
                telefone=form.cleaned_data.get('telefone'),
            )

            # ✅ LOG - Cadastro
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
    media_numerica = 9.3
    conceito_final = obter_conceito(media_numerica)

    # ✅ READ - Busca perfil e logs do usuário
    perfil = PerfilUsuario.buscar_por_usuario(request.user)
    logs = LogAtividade.objects.filter(usuario=request.user).order_by('-data')[:5]

    contexto = {
        'usuario': request.user,
        'perfil': perfil,
        'media_conceito': conceito_final,
        'logs_recentes': logs,
    }
    return render(request, 'usuarios/dashboard.html', contexto)


# ─────────────────────────────────────────
# UPDATE - Editar Perfil
# ─────────────────────────────────────────

@login_required(login_url='home')
def editar_perfil(request):
    perfil = get_object_or_404(PerfilUsuario, user=request.user)

    if request.method == 'POST':
        form = AtualizarPerfilForm(request.POST, instance=perfil)
        if form.is_valid():
            # ✅ UPDATE - Atualiza os dados do perfil
            perfil.atualizar(
                tipo_usuario=form.cleaned_data.get('tipo_usuario'),
                matricula=form.cleaned_data.get('matricula'),
                telefone=form.cleaned_data.get('telefone'),
            )

            # Atualiza nome no User também
            request.user.first_name = form.cleaned_data.get('nome_completo', request.user.first_name)
            request.user.save()

            # ✅ LOG - Update
            LogAtividade.registrar(request.user, 'update', f'Perfil de {request.user.email} atualizado.')

            messages.success(request, "Perfil atualizado com sucesso!")
            return redirect('dashboard')
    else:
        form = AtualizarPerfilForm(instance=perfil)

    return render(request, 'usuarios/editar_perfil.html', {'form': form, 'perfil': perfil})


# ─────────────────────────────────────────
# DELETE - Desativar Conta
# ─────────────────────────────────────────

@login_required(login_url='home')
def desativar_conta(request):
    if request.method == 'POST':
        perfil = get_object_or_404(PerfilUsuario, user=request.user)

        # ✅ LOG - Delete (registra antes de desativar)
        LogAtividade.registrar(request.user, 'delete', f'Conta de {request.user.email} desativada.')

        # ✅ DELETE - Soft delete (não apaga do banco, apenas desativa)
        perfil.desativar()

        logout(request)
        messages.success(request, "Sua conta foi desativada.")
        return redirect('home')

    return render(request, 'usuarios/confirmar_exclusao.html')