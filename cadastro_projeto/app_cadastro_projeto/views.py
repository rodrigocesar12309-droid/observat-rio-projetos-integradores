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
from .models import PerfilUsuario, ProjetoUsuario, LogAtividade, Empresa, TopicoForum, RespostaForum
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

            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=nome_empresa,
            )
            PerfilUsuario.criar(user=user, tipo_usuario='empresa')
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
        email = (request.POST.get('email') or request.POST.get('username') or '').strip().lower()
        password = request.POST.get('password', '')
        print(f'[LOGIN] email="{email}" password="{password}"')
        user = authenticate(request, username=email, password=password)
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
    next_url = request.POST.get('next') or request.GET.get('next') or 'relatorio_usuarios'
    return redirect(next_url)


@login_required(login_url='home')
def ativar_usuario(request, usuario_id):
    """Reativa um usuário desativado — apenas coordenador."""
    perfil = PerfilUsuario.buscar_por_usuario(request.user)
    if not perfil or perfil.tipo_usuario != 'administracao':
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard')

    usuario = get_object_or_404(User, id=usuario_id)
    usuario.is_active = True
    usuario.save()
    LogAtividade.registrar(request.user, 'update', f'Coordenador reativou {usuario.email}.')
    messages.success(request, f'Usuário {usuario.email} reativado com sucesso!')
    next_url = request.POST.get('next') or request.GET.get('next') or 'relatorio_usuarios'
    return redirect(next_url)


# ─────────────────────────────────────────
# HELPERS — dados para gráficos
# ─────────────────────────────────────────

def _dados_evolucao_mensal(meses=12):
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

    mapa = {}
    cursor = inicio.replace(day=1)
    while cursor <= hoje.replace(day=1):
        mapa[cursor] = {'em_avaliacao': 0, 'aprovado': 0, 'reprovado': 0}
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
    labels     = [f"{MESES_PT[m.month-1]}/{str(m.year)[2:]}" for m in meses_ord]
    submetidos = [mapa[m]['em_avaliacao'] + mapa[m]['aprovado'] + mapa[m].get('reprovado', 0) for m in meses_ord]
    aprovados  = [mapa[m]['aprovado'] for m in meses_ord]
    reprovados = [mapa[m].get('reprovado', 0) for m in meses_ord]

    return {'labels': labels, 'submetidos': submetidos, 'aprovados': aprovados, 'reprovados': reprovados}


def _dados_status():
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
    qs = (
        ProjetoUsuario.objects
        .filter(ativo=True)
        .exclude(categoria='')
        .values('categoria')
        .annotate(total=Count('id'))
        .order_by('-total')[:6]
    )
    return {'labels': [r['categoria'] for r in qs], 'valores': [r['total'] for r in qs]}


def _dados_por_semestre():
    qs = (
        ProjetoUsuario.objects
        .filter(ativo=True)
        .exclude(semestre='')
        .values('semestre')
        .annotate(total=Count('id'))
        .order_by('semestre')[:6]
    )
    return {'labels': [r['semestre'] for r in qs], 'valores': [r['total'] for r in qs]}


def _dados_radar():
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

    if perfil and perfil.tipo_usuario == 'administracao':
        projetos = ProjetoUsuario.objects.filter(ativo=True).select_related('usuario')
        melhores_projetos = projetos.exclude(conceito__isnull=True).exclude(conceito='').order_by('conceito')[:3]
        form_cadastro = CadastroForm()

        total_projetos  = projetos.count()
        total_alunos    = PerfilUsuario.objects.filter(tipo_usuario='aluno', ativo=True).count()
        em_avaliacao    = projetos.filter(status='em_avaliacao').count()
        aprovados_count = projetos.filter(status='aprovado').count()
        conceito_final  = obter_conceito_predominante(projetos)

        contexto = {
            'usuario': request.user,
            'perfil': perfil,
            'projetos': projetos.order_by('-criado_em')[:20],
            'melhores_projetos': melhores_projetos,
            'form': form_cadastro,
            'total_projetos':    total_projetos,
            'total_alunos':      total_alunos,
            'em_avaliacao':      em_avaliacao,
            'aprovados':         aprovados_count,
            'reprovados':        projetos.filter(status='reprovado').count(),
            'media_conceito':    conceito_final,
            'alunos':            PerfilUsuario.objects.filter(tipo_usuario='aluno', ativo=True).select_related('user'),
            'professores':       PerfilUsuario.objects.filter(tipo_usuario='professor', ativo=True).select_related('user')[:6],
            'professores_count': PerfilUsuario.objects.filter(tipo_usuario='professor', ativo=True).count(),
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
            'alunos': PerfilUsuario.objects.filter(tipo_usuario='aluno', ativo=True).select_related('user'),
            'alunos_count': PerfilUsuario.objects.filter(tipo_usuario='aluno', ativo=True).count(),
            'graf_categorias': json.dumps(_dados_por_categoria()),
        }
        return render(request, 'usuarios/dashboard_empresa.html', contexto)

    elif perfil and perfil.tipo_usuario == 'professor':
        projetos = ProjetoUsuario.objects.filter(ativo=True).select_related('usuario')
        contexto = {
            'usuario': request.user,
            'projetos': projetos,
            'total': projetos.count(),
            'pendentes': projetos.filter(status='em_avaliacao').count(),
            'avaliados': projetos.exclude(status='em_avaliacao').count(),
            'topicos_recentes': TopicoForum.objects.filter(ativo=True).select_related('autor').order_by('-criado_em')[:4],
        }
        return render(request, 'usuarios/dashboard_professor.html', contexto)

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
            'topicos_recentes': TopicoForum.objects.filter(ativo=True).select_related('autor').order_by('-criado_em')[:5],
            'nao_lidas': TopicoForum.objects.filter(ativo=True).count(),
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
# AVALIAR PROJETO (apenas professores)
# ─────────────────────────────────────────

@login_required(login_url='home')
def painel_avaliacao(request):
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


# ─────────────────────────────────────────
# RELATÓRIO USUÁRIOS
# ─────────────────────────────────────────

@login_required(login_url='home')
def relatorio_usuarios(request):
    perfil = PerfilUsuario.buscar_por_usuario(request.user)
    if not perfil or perfil.tipo_usuario != 'administracao':
        messages.error(request, 'Acesso negado: apenas coordenadores podem visualizar o relatório.')
        return redirect('dashboard')

    usuarios = PerfilUsuario.objects.select_related('user').all()
    projetos = ProjetoUsuario.objects.filter(ativo=True)

    # Dados para gráficos
    total_alunos     = PerfilUsuario.objects.filter(tipo_usuario='aluno', ativo=True).count()
    total_professores= PerfilUsuario.objects.filter(tipo_usuario='professor', ativo=True).count()
    total_coord      = PerfilUsuario.objects.filter(tipo_usuario='administracao', ativo=True).count()
    total_empresas   = PerfilUsuario.objects.filter(tipo_usuario='empresa', ativo=True).count()
    total_projetos   = projetos.count()
    aprovados        = projetos.filter(status='aprovado').count()
    em_avaliacao     = projetos.filter(status='em_avaliacao').count()
    reprovados       = projetos.filter(status='reprovado').count()

    return render(request, 'usuarios/relatorio_usuarios.html', {
        'usuario': request.user,
        'usuarios': usuarios,
        'total_alunos':      total_alunos,
        'total_professores': total_professores,
        'total_coord':       total_coord,
        'total_empresas':    total_empresas,
        'total_projetos':    total_projetos,
        'aprovados':         aprovados,
        'em_avaliacao':      em_avaliacao,
        'reprovados':        reprovados,
        'graf_usuarios': json.dumps({
            'labels': ['Alunos', 'Professores', 'Coordenadores', 'Empresas'],
            'valores': [total_alunos, total_professores, total_coord, total_empresas],
        }),
        'graf_projetos': json.dumps({
            'labels': ['Aprovados', 'Em Avaliação', 'Reprovados'],
            'valores': [aprovados, em_avaliacao, reprovados],
        }),
        'graf_evolucao_12m': json.dumps(_dados_evolucao_mensal(12)),
        'graf_evolucao_6m':  json.dumps(_dados_evolucao_mensal(6)),
        'graf_evolucao_3m':  json.dumps(_dados_evolucao_mensal(3)),
        'graf_categoria': json.dumps(_dados_por_categoria()),
        'graf_semestre':  json.dumps(_dados_por_semestre()),
    })


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


# ─────────────────────────────────────────
# FÓRUM
# ─────────────────────────────────────────

@login_required(login_url='home')
def forum_lista(request):
    """Lista todos os tópicos do fórum."""
    perfil = PerfilUsuario.buscar_por_usuario(request.user)
    # Empresa não acessa o fórum
    if perfil and perfil.tipo_usuario == 'empresa':
        messages.error(request, 'Acesso não permitido.')
        return redirect('dashboard')

    categoria = request.GET.get('categoria', '')
    busca = request.GET.get('busca', '')

    topicos = TopicoForum.objects.filter(ativo=True).select_related('autor').prefetch_related('respostas')
    if categoria:
        topicos = topicos.filter(categoria=categoria)
    if busca:
        topicos = topicos.filter(titulo__icontains=busca)

    return render(request, 'usuarios/forum_lista.html', {
        'topicos': topicos,
        'perfil': perfil,
        'usuario': request.user,
        'categoria': categoria,
        'busca': busca,
        'total': topicos.count(),
    })


@login_required(login_url='home')
def forum_topico(request, topico_id):
    """Exibe um tópico e suas respostas."""
    perfil = PerfilUsuario.buscar_por_usuario(request.user)
    if perfil and perfil.tipo_usuario == 'empresa':
        return redirect('dashboard')

    topico = get_object_or_404(TopicoForum, id=topico_id, ativo=True)
    respostas = topico.respostas.filter(ativo=True).select_related('autor')

    if request.method == 'POST':
        conteudo = request.POST.get('conteudo', '').strip()
        if conteudo:
            RespostaForum.objects.create(
                topico=topico,
                autor=request.user,
                conteudo=conteudo,
            )
            messages.success(request, 'Resposta enviada!')
            return redirect('forum_topico', topico_id=topico_id)
        else:
            messages.error(request, 'Escreva algo antes de enviar.')

    return render(request, 'usuarios/forum_topico.html', {
        'topico': topico,
        'respostas': respostas,
        'perfil': perfil,
        'usuario': request.user,
    })


@login_required(login_url='home')
def forum_novo_topico(request):
    """Cria um novo tópico."""
    perfil = PerfilUsuario.buscar_por_usuario(request.user)
    if perfil and perfil.tipo_usuario == 'empresa':
        return redirect('dashboard')

    if request.method == 'POST':
        titulo = request.POST.get('titulo', '').strip()
        conteudo = request.POST.get('conteudo', '').strip()
        categoria = request.POST.get('categoria', 'duvida')
        fixado = request.POST.get('fixado') == 'on'

        # Só professor/admin pode fixar
        pode_fixar = perfil and perfil.tipo_usuario in ['professor', 'administracao']

        if titulo and conteudo:
            topico = TopicoForum.objects.create(
                autor=request.user,
                titulo=titulo,
                conteudo=conteudo,
                categoria=categoria,
                fixado=fixado if pode_fixar else False,
            )
            messages.success(request, 'Tópico criado com sucesso!')
            return redirect('forum_topico', topico_id=topico.id)
        else:
            messages.error(request, 'Preencha o título e o conteúdo.')

    return render(request, 'usuarios/forum_novo_topico.html', {
        'perfil': perfil,
        'usuario': request.user,
    })


@login_required(login_url='home')
def forum_deletar_topico(request, topico_id):
    """Deleta (desativa) um tópico — apenas autor ou admin/professor."""
    perfil = PerfilUsuario.buscar_por_usuario(request.user)
    topico = get_object_or_404(TopicoForum, id=topico_id)
    pode = (topico.autor == request.user or
            (perfil and perfil.tipo_usuario in ['professor', 'administracao']))
    if pode and request.method == 'POST':
        topico.ativo = False
        topico.save()
        messages.success(request, 'Tópico removido.')
    return redirect('forum_lista')


@login_required(login_url='home')
def forum_deletar_resposta(request, resposta_id):
    """Deleta uma resposta — apenas autor ou admin/professor."""
    perfil = PerfilUsuario.buscar_por_usuario(request.user)
    resposta = get_object_or_404(RespostaForum, id=resposta_id)
    pode = (resposta.autor == request.user or
            (perfil and perfil.tipo_usuario in ['professor', 'administracao']))
    if pode and request.method == 'POST':
        resposta.ativo = False
        resposta.save()
        messages.success(request, 'Resposta removida.')
    return redirect('forum_topico', topico_id=resposta.topico_id)


# ─────────────────────────────────────────
# ENCERRAR PROJETO (apenas admin)
# ─────────────────────────────────────────

@login_required(login_url='home')
def encerrar_projeto(request, projeto_id):
    perfil = PerfilUsuario.buscar_por_usuario(request.user)
    if not perfil or perfil.tipo_usuario != 'administracao':
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard')

    projeto = get_object_or_404(ProjetoUsuario, id=projeto_id)

    # Só pode encerrar projetos já avaliados
    if projeto.status == 'em_avaliacao':
        messages.error(request, 'Não é possível encerrar um projeto que ainda não foi avaliado.')
        return redirect('dashboard')

    if request.method == 'POST':
        projeto.encerrado = True
        projeto.encerrado_em = timezone.now()
        projeto.save()
        LogAtividade.registrar(
            request.user, 'update',
            f'Admin encerrou o projeto "{projeto.titulo}" do aluno {projeto.usuario.first_name}.'
        )
        messages.success(request, f'Projeto "{projeto.titulo}" encerrado com sucesso.')

    return redirect('dashboard')


@login_required(login_url='home')
def reabrir_projeto(request, projeto_id):
    perfil = PerfilUsuario.buscar_por_usuario(request.user)
    if not perfil or perfil.tipo_usuario != 'administracao':
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard')

    projeto = get_object_or_404(ProjetoUsuario, id=projeto_id)
    if request.method == 'POST':
        projeto.encerrado = False
        projeto.encerrado_em = None
        projeto.save()
        messages.success(request, f'Projeto "{projeto.titulo}" reaberto.')

    return redirect('dashboard')


# ─────────────────────────────────────────
# CURRÍCULO DO ALUNO (salvar + ver pela empresa)
# ─────────────────────────────────────────

@login_required(login_url='home')
def salvar_curriculo(request):
    """Aluno salva seu currículo no banco."""
    if request.method == 'POST':
        perfil = get_object_or_404(PerfilUsuario, user=request.user)
        perfil.user.first_name = request.POST.get('nome', perfil.user.first_name)
        perfil.user.save()
        perfil.cargo       = request.POST.get('cargo', '')
        perfil.bio         = request.POST.get('bio', '')
        perfil.telefone    = request.POST.get('telefone', '')
        perfil.linkedin    = request.POST.get('linkedin', '') or None
        perfil.github      = request.POST.get('github', '') or None
        perfil.habilidades = request.POST.get('habilidades', '')
        perfil.experiencia = request.POST.get('experiencia', '')
        perfil.formacao    = request.POST.get('formacao', '')
        perfil.save()
        messages.success(request, 'Currículo salvo com sucesso!')
    return redirect('dashboard')


@login_required(login_url='home')
def ver_curriculo_aluno(request, usuario_id):
    """Empresa visualiza o currículo de um aluno vinculado a um projeto."""
    perfil_empresa = PerfilUsuario.buscar_por_usuario(request.user)
    if not perfil_empresa or perfil_empresa.tipo_usuario not in ['empresa', 'administracao']:
        messages.error(request, 'Acesso restrito.')
        return redirect('dashboard')

    aluno = get_object_or_404(User, id=usuario_id)

    # Verifica se o aluno tem ao menos um projeto ativo/encerrado
    tem_projeto = ProjetoUsuario.objects.filter(usuario=aluno, ativo=True).exists()
    if not tem_projeto:
        messages.error(request, 'Este aluno não possui projetos cadastrados.')
        return redirect('dashboard')

    try:
        perfil_aluno = aluno.perfil
    except Exception:
        messages.error(request, 'Perfil do aluno não encontrado.')
        return redirect('dashboard')

    projetos = ProjetoUsuario.objects.filter(usuario=aluno, ativo=True)

    # Processa habilidades e experiência na view (template não suporta .split())
    habilidades_lista = []
    if perfil_aluno.habilidades:
        habilidades_lista = [h.strip() for h in perfil_aluno.habilidades.split(',') if h.strip()]

    experiencia_lista = []
    if perfil_aluno.experiencia:
        for linha in perfil_aluno.experiencia.splitlines():
            if linha.strip():
                partes = [p.strip() for p in linha.split('|')]
                experiencia_lista.append(partes)

    formacao_lista = []
    if perfil_aluno.formacao:
        for linha in perfil_aluno.formacao.splitlines():
            if linha.strip():
                partes = [p.strip() for p in linha.split('|')]
                formacao_lista.append(partes)

    return render(request, 'usuarios/curriculo_aluno.html', {
        'aluno': aluno,
        'perfil': perfil_aluno,
        'projetos': projetos,
        'habilidades_lista': habilidades_lista,
        'experiencia_lista': experiencia_lista,
        'formacao_lista': formacao_lista,
    })


# ─────────────────────────────────────────
# COORDENAÇÃO — SIDEBAR PAGES
# ─────────────────────────────────────────

@login_required(login_url='home')
def coord_todos_projetos(request):
    perfil = PerfilUsuario.buscar_por_usuario(request.user)
    if not perfil or perfil.tipo_usuario != 'administracao':
        return redirect('dashboard')

    busca     = request.GET.get('busca', '')
    status_f  = request.GET.get('status', '')
    cat_f     = request.GET.get('categoria', '')

    projetos = ProjetoUsuario.objects.filter(ativo=True).select_related('usuario')
    if busca:
        projetos = projetos.filter(titulo__icontains=busca)
    if status_f:
        projetos = projetos.filter(status=status_f)
    if cat_f:
        projetos = projetos.filter(categoria=cat_f)

    categorias = (ProjetoUsuario.objects.filter(ativo=True)
                  .exclude(categoria='').values_list('categoria', flat=True)
                  .distinct().order_by('categoria'))

    return render(request, 'usuarios/coord_projetos.html', {
        'usuario': request.user,
        'projetos': projetos.order_by('-criado_em'),
        'total': projetos.count(),
        'busca': busca,
        'status_f': status_f,
        'cat_f': cat_f,
        'categorias': categorias,
        'em_avaliacao': projetos.filter(status='em_avaliacao').count(),
        'aprovados': projetos.filter(status='aprovado').count(),
        'reprovados': projetos.filter(status='reprovado').count(),
    })


@login_required(login_url='home')
def coord_corpo_docente(request):
    perfil = PerfilUsuario.buscar_por_usuario(request.user)
    if not perfil or perfil.tipo_usuario != 'administracao':
        return redirect('dashboard')

    professores = PerfilUsuario.objects.filter(
        tipo_usuario='professor', ativo=True
    ).select_related('user')

    return render(request, 'usuarios/coord_corpo_docente.html', {
        'usuario': request.user,
        'professores': professores,
        'total': professores.count(),
        'projetos_count': ProjetoUsuario.objects.filter(ativo=True).count(),
    })


@login_required(login_url='home')
def coord_mensagens(request):
    perfil = PerfilUsuario.buscar_por_usuario(request.user)
    if not perfil or perfil.tipo_usuario != 'administracao':
        return redirect('dashboard')
    # Redireciona para o fórum geral
    return redirect('forum_lista')


# ─────────────────────────────────────────
# MEUS PROJETOS (página dedicada do aluno)
# ─────────────────────────────────────────

@login_required(login_url='home')
def meus_projetos(request):
    perfil = PerfilUsuario.buscar_por_usuario(request.user)

    projetos = ProjetoUsuario.objects.filter(
        usuario=request.user, ativo=True
    ).order_by('-criado_em')

    if request.method == 'POST':
        # Criar novo projeto via formulário inline
        titulo = request.POST.get('titulo', '').strip()
        descricao = request.POST.get('descricao', '').strip()
        if titulo and descricao:
            ProjetoUsuario.objects.create(
                usuario=request.user,
                titulo=titulo,
                descricao=descricao,
                categoria=request.POST.get('categoria', ''),
                semestre=request.POST.get('semestre', ''),
                tags=request.POST.get('tags', ''),
                link_repositorio=request.POST.get('link_repositorio') or None,
                link_demo=request.POST.get('link_demo') or None,
            )
            LogAtividade.registrar(request.user, 'create', 'Projeto criado.')
            messages.success(request, 'Projeto criado com sucesso!')
            return redirect('meus_projetos')
        else:
            messages.error(request, 'Preencha o título e a descrição.')

    total        = projetos.count()
    aprovados    = projetos.filter(status='aprovado').count()
    em_avaliacao = projetos.filter(status='em_avaliacao').count()

    return render(request, 'usuarios/meus_projetos.html', {
        'usuario': request.user,
        'perfil': perfil,
        'projetos': projetos,
        'total': total,
        'aprovados': aprovados,
        'em_avaliacao': em_avaliacao,
    })
