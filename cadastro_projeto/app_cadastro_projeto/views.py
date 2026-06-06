from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, Avg
from django.db.models.functions import TruncMonth
from django.utils import timezone
import json
import datetime

from .forms import CadastroForm, AtualizarPerfilForm, CadastroEmpresaLoginForm
from .models import PerfilUsuario, ProjetoUsuario, LogAtividade, Empresa
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import UsuarioSerializer, ProjetoSerializer


# ─────────────────────────────────────────
# CADASTRAR EMPRESA COM LOGIN (coordenador)
# ─────────────────────────────────────────

@login_required(login_url='home')
def cadastrar_empresa_login(request):
    """Coordenador cria uma empresa E seu login de acesso ao sistema."""
    perfil = PerfilUsuario.buscar_por_usuario(request.user)
    if not perfil or perfil.tipo_usuario != 'administracao':
        messages.error(request, 'Acesso negado: apenas coordenadores podem cadastrar empresas.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = CadastroEmpresaLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            nome_empresa = form.cleaned_data['nome_empresa']
            cnpj = form.cleaned_data['cnpj']

            # Cria o User Django
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=nome_empresa,
            )
            # Cria o perfil como empresa
            PerfilUsuario.criar(user=user, tipo_usuario='empresa')
            # Cria o registro no model Empresa
            Empresa.objects.create(nome=nome_empresa, cnpj=cnpj)

            LogAtividade.registrar(
                request.user, 'create',
                f'Coordenador cadastrou empresa "{nome_empresa}" com login {email}.'
            )
            messages.success(request, f'Empresa "{nome_empresa}" cadastrada com login de acesso!')
            return redirect('dashboard')
        else:
            for field, erros in form.errors.items():
                for erro in erros:
                    messages.error(request, f'{erro}')
    else:
        form = CadastroEmpresaLoginForm()

    return redirect('dashboard')

def obter_conceito_predominante(projetos_qs):
    """Retorna o conceito mais frequente entre os projetos avaliados."""
    avaliados = projetos_qs.exclude(conceito__isnull=True).exclude(conceito='')
    if not avaliados.exists():
        return '-'
    from django.db.models import Count
    mais_comum = (
        avaliados.values('conceito')
        .annotate(total=Count('id'))
        .order_by('-total')
        .first()
    )
    return mais_comum['conceito'] if mais_comum else '-'

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
        messages.error(request, 'Acesso negado.')
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
# HELPERS — dados para gráficos
# ─────────────────────────────────────────

def _dados_evolucao_mensal(meses=12):
    """
    Retorna labels e séries de projetos criados por mês
    nos últimos `meses` meses, separados por status.
    """
    hoje = timezone.now().date()
    inicio = hoje.replace(day=1) - datetime.timedelta(days=30 * (meses - 1))

    qs = (
        ProjetoUsuario.objects
        .filter(criado_em__date__gte=inicio)
        .annotate(mes=TruncMonth('criado_em'))
        .values('mes', 'status')
        .annotate(total=Count('id'))
        .order_by('mes')
    )

    # monta mapa {mes: {status: count}}
    mapa = {}
    cursor = inicio.replace(day=1)
    while cursor <= hoje.replace(day=1):
        mapa[cursor] = {'em_avaliacao': 0, 'aprovado': 0, 'reprovado': 0}
        # avança um mês
        if cursor.month == 12:
            cursor = cursor.replace(year=cursor.year + 1, month=1)
        else:
            cursor = cursor.replace(month=cursor.month + 1)

    for row in qs:
        chave = row['mes'].date().replace(day=1)
        if chave in mapa:
            mapa[chave][row['status']] = row['total']

    meses_ord = sorted(mapa.keys())
    MESES_PT = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez']
    labels      = [f"{MESES_PT[m.month-1]}/{str(m.year)[2:]}" for m in meses_ord]
    submetidos  = [mapa[m]['em_avaliacao'] + mapa[m]['aprovado'] + mapa[m].get('reprovado', 0) for m in meses_ord]
    aprovados   = [mapa[m]['aprovado']   for m in meses_ord]
    reprovados  = [mapa[m].get('reprovado', 0) for m in meses_ord]

    return {'labels': labels, 'submetidos': submetidos, 'aprovados': aprovados, 'reprovados': reprovados}


def _dados_status():
    """Contagem de projetos por status para o doughnut."""
    qs = (
        ProjetoUsuario.objects
        .filter(ativo=True)
        .values('status')
        .annotate(total=Count('id'))
    )
    mapa = {r['status']: r['total'] for r in qs}
    return [
        mapa.get('em_avaliacao', 0),
        mapa.get('aprovado', 0),
        mapa.get('reprovado', 0),
    ]


def _dados_por_categoria():
    """Top 6 categorias com mais projetos."""
    qs = (
        ProjetoUsuario.objects
        .filter(ativo=True)
        .exclude(categoria='')
        .values('categoria')
        .annotate(total=Count('id'))
        .order_by('-total')[:6]
    )
    labels = [r['categoria'] for r in qs]
    valores = [r['total'] for r in qs]
    return {'labels': labels, 'valores': valores}


def _dados_por_semestre():
    """Projetos agrupados por semestre."""
    qs = (
        ProjetoUsuario.objects
        .filter(ativo=True)
        .exclude(semestre='')
        .values('semestre')
        .annotate(total=Count('id'))
        .order_by('semestre')[:6]
    )
    labels = [r['semestre'] for r in qs]
    valores = [r['total'] for r in qs]
    return {'labels': labels, 'valores': valores}


def _dados_radar():
    """Contagem por conceito para o gráfico radar."""
    qs = ProjetoUsuario.objects.filter(ativo=True).exclude(conceito__isnull=True).exclude(conceito='')
    total = qs.count() or 1

    excelente  = qs.filter(conceito='Excelente').count()
    bom        = qs.filter(conceito='Bom').count()
    suficiente = qs.filter(conceito='Suficiente').count()
    insuf      = qs.filter(conceito='Insuficiente').count()
    aprovados  = qs.filter(status='aprovado').count()
    total_proj = ProjetoUsuario.objects.filter(ativo=True).count() or 1

    def pct(v): return round((v / total) * 10, 1)

    return [pct(excelente), pct(bom), pct(suficiente), pct(aprovados), pct(total - insuf), round((aprovados / total_proj) * 10, 1)]


# ─────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────

@login_required(login_url='home')
def dashboard(request):
    perfil = PerfilUsuario.buscar_por_usuario(request.user)

    # 1. Painel de Administração
    if perfil and perfil.tipo_usuario == 'administracao':
        projetos = ProjetoUsuario.objects.filter(ativo=True).select_related('usuario')
        melhores_projetos = projetos.exclude(conceito__isnull=True).exclude(conceito='').order_by('conceito')[:3]
        form_cadastro = CadastroForm()

        total_projetos   = projetos.count()
        total_alunos     = PerfilUsuario.objects.filter(tipo_usuario='aluno', ativo=True).count()
        em_avaliacao     = projetos.filter(status='em_avaliacao').count()
        aprovados_count  = projetos.filter(status='aprovado').count()

        conceito_final = obter_conceito_predominante(projetos)

        contexto = {
            'usuario': request.user,
            'perfil': perfil,
            'projetos': projetos.order_by('-criado_em')[:20],
            'melhores_projetos': melhores_projetos,
            'form': form_cadastro,
            'total_projetos':  total_projetos,
            'total_alunos':    total_alunos,
            'em_avaliacao':    em_avaliacao,
            'aprovados':       aprovados_count,
            'media_conceito':  conceito_final,
            'graf_evolucao_12m': json.dumps(_dados_evolucao_mensal(12)),
            'graf_evolucao_6m':  json.dumps(_dados_evolucao_mensal(6)),
            'graf_evolucao_3m':  json.dumps(_dados_evolucao_mensal(3)),
            'graf_status':       json.dumps(_dados_status()),
            'graf_categoria':    json.dumps(_dados_por_categoria()),
            'graf_semestre':     json.dumps(_dados_por_semestre()),
            'graf_radar':        json.dumps(_dados_radar()),
            'total_doughnut':    total_projetos,
        }
        return render(request, 'usuarios/dashboard_admin.html', contexto)

    # 2. Painel da Empresa
    elif perfil and perfil.tipo_usuario == 'empresa':
        projetos = ProjetoUsuario.objects.filter(ativo=True).select_related('usuario')
        categorias = (
            ProjetoUsuario.objects.filter(ativo=True)
            .exclude(categoria='')
            .values_list('categoria', flat=True)
            .distinct()
            .order_by('categoria')
        )
        cat_filtro = request.GET.get('categoria', '')
        busca = request.GET.get('busca', '')
        if cat_filtro:
            projetos = projetos.filter(categoria=cat_filtro)
        if busca:
            projetos = projetos.filter(titulo__icontains=busca)
        contexto = {
            'usuario': request.user,
            'perfil': perfil,
            'projetos': projetos,
            'categorias': categorias,
            'cat_filtro': cat_filtro,
            'busca': busca,
            'total': projetos.count(),
            'aprovados': projetos.filter(status='aprovado').count(),
        }
        return render(request, 'usuarios/dashboard_empresa.html', contexto)

    # 3. Painel do professor
    elif perfil and perfil.tipo_usuario == 'professor':
        projetos = ProjetoUsuario.objects.filter(ativo=True).select_related('usuario')
        contexto = {
            'usuario': request.user,
            'projetos': projetos,
            'total': projetos.count(),
            'pendentes': projetos.filter(status='em_avaliacao').count(),
            'avaliados': projetos.exclude(status='em_avaliacao').count(),
        }
        return render(request, 'usuarios/dashboard_professor.html', contexto)

    # 4. Painel do Aluno (Padrão)
    else:
        projetos = ProjetoUsuario.objects.filter(usuario=request.user, ativo=True)
        melhores_projetos = projetos.exclude(conceito__isnull=True).exclude(conceito='').order_by('conceito')[:3]

        total        = projetos.count()
        aprovados    = projetos.filter(status='aprovado').count()
        em_avaliacao = projetos.filter(status='em_avaliacao').count()
        conceito_final = obter_conceito_predominante(projetos)

        contexto = {
            'usuario': request.user,
            'perfil': perfil,
            'projetos': projetos,
            'melhores_projetos': melhores_projetos,
            'total': total,
            'aprovados': aprovados,
            'em_avaliacao': em_avaliacao,
            'media_conceito': conceito_final,
            'form': None,
        }
        return render(request, 'usuarios/dashboard_aluno.html', contexto)


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
# AVALIAR PROJETO(apenas professores)
# ─────────────────────────────────────────
@login_required(login_url='home')
def painel_avaliacao(request):
    # Verifica se o usuário é professor (assumindo que você tem essa lógica)
    perfil = PerfilUsuario.buscar_por_usuario(request.user)
    if not perfil or perfil.tipo_usuario != 'professor':
        messages.error(request, 'Acesso restrito a professores.')
        return redirect('dashboard')

    projetos = ProjetoUsuario.objects.filter(ativo=True).select_related('usuario')

    contexto = {
        'usuario': request.user,
        'projetos': projetos,
        'total': projetos.count(),
        'pendentes': projetos.filter(status='em_avaliacao').count(),
        'avaliados': projetos.exclude(status='em_avaliacao').count(),
    }
    return render(request, 'usuarios/painel_avaliacao.html', contexto)


@login_required(login_url='home')
def avaliar_projeto(request, projeto_id):
    perfil = PerfilUsuario.buscar_por_usuario(request.user)
    if not perfil or perfil.tipo_usuario != 'professor':
        messages.error(request, 'Acesso restrito a professores.')
        return redirect('dashboard')

    projeto = get_object_or_404(ProjetoUsuario, id=projeto_id)

    if request.method == 'POST':
        conceito = request.POST.get('conceito', '').strip()
        comentario = request.POST.get('comentario_professor', '').strip()

        if conceito not in ['Ótimo', 'Excelente', 'Bom', 'Suficiente', 'Insuficiente']:
            messages.error(request, 'Selecione um conceito válido.')
            return render(request, 'usuarios/avaliar_projeto.html', {'projeto': projeto})

        projeto.conceito = conceito
        projeto.comentario_professor = comentario
        projeto.status = 'aprovado' if conceito in ['Ótimo', 'Excelente', 'Bom', 'Suficiente'] else 'reprovado'
        projeto.save()

        LogAtividade.registrar(
            request.user, 'update',
            f'Projeto "{projeto.titulo}" avaliado com conceito {conceito}.'
        )
        messages.success(request, 'Avaliação salva com sucesso!')
        return redirect('painel_avaliacao')

    return render(request, 'usuarios/avaliar_projeto.html', {'projeto': projeto})


# ─────────────────────────
# RELATÓRIO USUÁRIOS
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
# EDITAR USUÁRIO
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
    serializer = UsuarioSerializer(usuarios, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_projetos(request):
    projetos = ProjetoUsuario.objects.filter(ativo=True)
    serializer = ProjetoSerializer(projetos, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_projeto_detalhe(request, projeto_id):
    projeto = get_object_or_404(ProjetoUsuario, id=projeto_id)
    serializer = ProjetoSerializer(projeto)
    return Response(serializer.data)