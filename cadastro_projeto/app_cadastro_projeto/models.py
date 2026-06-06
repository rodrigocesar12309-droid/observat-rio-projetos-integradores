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

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projetos_usuario')
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    categoria = models.CharField(max_length=100, blank=True)
    semestre = models.CharField(max_length=20, blank=True)
    nota = models.FloatField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='em_avaliacao')
    tags = models.CharField(max_length=200, blank=True, help_text='Separe por vírgula. Ex: React,Node.js')
    link_repositorio = models.URLField(blank=True, null=True)
    link_demo = models.URLField(blank=True, null=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True, null=True)
    atualizado_em = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        ordering = ['-criado_em']

    def __str__(self):
        return f"{self.titulo} - {self.usuario.first_name}"

    def get_tags_lista(self):
        return [t.strip() for t in self.tags.split(',') if t.strip()]

    def get_conceito(self):
        if self.nota is None:
            return '-'
        if self.nota >= 9.0: return 'Excelente'
        elif self.nota >= 7.0: return 'Bom'
        elif self.nota >= 5.0: return 'Suficiente'
        else: return 'Insuficiente'

