from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Empresa(models.Model):
    nome = models.CharField(max_length=200)
    cnpj = models.CharField(max_length=18, unique=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome

class PerfilUsuario(models.Model):
    OPCOES_PERFIL = [
        ('aluno', 'Aluno'),
        ('professor', 'Professor'),
        ('administracao', 'Administração'),
        ('empresa', 'Empresa'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    tipo_usuario = models.CharField(max_length=20, choices=OPCOES_PERFIL, default='aluno')
    matricula = models.CharField(max_length=50, blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    foto = models.ImageField(upload_to='fotos_perfil/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    # Currículo
    cargo = models.CharField(max_length=100, blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    github = models.URLField(blank=True, null=True)
    habilidades = models.CharField(max_length=500, blank=True, null=True, help_text='Separe por vírgula')
    experiencia = models.TextField(blank=True, null=True)
    formacao = models.TextField(blank=True, null=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Perfil de Usuário'
        verbose_name_plural = 'Perfis de Usuários'
        ordering = ['-criado_em']

    def __str__(self):
        return f"{self.user.first_name} ({self.get_tipo_usuario_display()})"

    @classmethod
    def criar(cls, user, tipo_usuario='aluno', matricula=None, telefone=None):
        perfil = cls.objects.create(
            user=user,
            tipo_usuario=tipo_usuario,
            matricula=matricula,
            telefone=telefone,
        )
        return perfil

    @classmethod
    def buscar_por_usuario(cls, user):
        try:
            return cls.objects.get(user=user)
        except cls.DoesNotExist:
            return None

    @classmethod
    def listar_por_tipo(cls, tipo):
        return cls.objects.filter(tipo_usuario=tipo, ativo=True)

    def atualizar(self, **kwargs):
        for campo, valor in kwargs.items():
            if hasattr(self, campo):
                setattr(self, campo, valor)
        self.save()
        return self

    def desativar(self):
        self.ativo = False
        self.save()

    def deletar(self):
        self.user.delete()

    # ✅ Propriedade para checar se é admin facilmente
    @property
    def is_admin(self):
        return self.tipo_usuario == 'administracao'


class Projeto(models.Model):
    STATUS_CHOICES = [
        ('em_andamento', 'Em Andamento'),
        ('concluido', 'Concluído'),
        ('pausado', 'Pausado'),
        ('cancelado', 'Cancelado'),
    ]

    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='em_andamento')
    criado_por = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projetos')
    membros = models.ManyToManyField(User, related_name='projetos_membro', blank=True)
    data_inicio = models.DateField(default=timezone.now)
    data_fim = models.DateField(blank=True, null=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Projeto'
        verbose_name_plural = 'Projetos'
        ordering = ['-criado_em']

    def __str__(self):
        return f"{self.titulo} ({self.get_status_display()})"

    @classmethod
    def criar(cls, titulo, descricao, criado_por, data_inicio=None, data_fim=None):
        return cls.objects.create(
            titulo=titulo,
            descricao=descricao,
            criado_por=criado_por,
            data_inicio=data_inicio or timezone.now(),
            data_fim=data_fim,
        )

    @classmethod
    def buscar_por_id(cls, projeto_id):
        try:
            return cls.objects.get(id=projeto_id, ativo=True)
        except cls.DoesNotExist:
            return None

    @classmethod
    def listar_ativos(cls):
        return cls.objects.filter(ativo=True)

    def atualizar(self, **kwargs):
        for campo, valor in kwargs.items():
            if hasattr(self, campo):
                setattr(self, campo, valor)
        self.save()
        return self

    def desativar(self):
        self.ativo = False
        self.save()

    def deletar(self):
        self.delete()


class LogAtividade(models.Model):
    ACOES = [
        ('create', 'Criação'),
        ('update', 'Atualização'),
        ('delete', 'Exclusão'),
        ('login', 'Login'),
        ('logout', 'Logout'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='logs')
    acao = models.CharField(max_length=20, choices=ACOES)
    descricao = models.TextField()
    data = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Log de Atividade'
        verbose_name_plural = 'Logs de Atividades'
        ordering = ['-data']

    def __str__(self):
        return f"{self.usuario} - {self.get_acao_display()} em {self.data.strftime('%d/%m/%Y %H:%M')}"

    @classmethod
    def registrar(cls, usuario, acao, descricao):
        return cls.objects.create(
            usuario=usuario,
            acao=acao,
            descricao=descricao,
        )


class ProjetoUsuario(models.Model):
    STATUS_CHOICES = [
        ('em_avaliacao', 'Em Avaliação'),
        ('aprovado', 'Aprovado'),
        ('reprovado', 'Reprovado'),
    ]

    CONCEITO_CHOICES = [
        ('Excelente', 'Excelente'),
        ('Ótimo', 'Ótimo'),
        ('Bom', 'Bom'),
        ('Suficiente', 'Suficiente'),
        ('Insuficiente', 'Insuficiente'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projetos_usuario')
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    categoria = models.CharField(max_length=100, blank=True)
    semestre = models.CharField(max_length=20, blank=True)
    conceito = models.CharField(max_length=20, choices=CONCEITO_CHOICES, blank=True, null=True)
    comentario_professor = models.TextField(blank=True, null=True, verbose_name='Comentário do Professor')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='em_avaliacao')
    tags = models.CharField(max_length=200, blank=True, help_text='Separe por vírgula. Ex: React,Node.js')
    link_repositorio = models.URLField(blank=True, null=True)
    link_demo = models.URLField(blank=True, null=True)
    ativo = models.BooleanField(default=True)
    encerrado = models.BooleanField(default=False)
    encerrado_em = models.DateTimeField(blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True, null=True)
    atualizado_em = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        ordering = ['-criado_em']

    def __str__(self):
        return f"{self.titulo} - {self.usuario.first_name}"

    def get_tags_lista(self):
        return [t.strip() for t in self.tags.split(',') if t.strip()]

    def get_conceito_display_color(self):
        cores = {
            'Excelente':    '#5B47E0',
            'Bom':          '#10B89A',
            'Suficiente':   '#F59E0B',
            'Insuficiente': '#F43F5E',
        }
        return cores.get(self.conceito, '#7B7B96')



class TopicoForum(models.Model):
    CATEGORIA_CHOICES = [
        ('duvida', 'Dúvida'),
        ('discussao', 'Discussão'),
        ('aviso', 'Aviso'),
        ('projeto', 'Projeto'),
    ]

    autor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='topicos')
    titulo = models.CharField(max_length=200)
    conteudo = models.TextField()
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES, default='duvida')
    fixado = models.BooleanField(default=False)
   
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fixado', '-criado_em']

    def __str__(self):
        return self.titulo

    def total_respostas(self):
        return self.respostas.filter(ativo=True).count()


class RespostaForum(models.Model):
    topico = models.ForeignKey(TopicoForum, on_delete=models.CASCADE, related_name='respostas')
    autor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='respostas_forum')
    conteudo = models.TextField()
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['criado_em']

    def __str__(self):
        return f'Resposta de {self.autor.first_name} em "{self.topico.titulo}"'
