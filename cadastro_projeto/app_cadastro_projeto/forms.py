from django import forms
from django.contrib.auth.models import User
from .models import PerfilUsuario, Empresa

# Opções de tipo de usuário (sem empresa — empresa tem form próprio)
TIPOS_USUARIO = [
    ('aluno', 'Aluno'),
    ('professor', 'Professor'),
    ('administracao', 'Coordenador'),
]


class EmpresaForm(forms.ModelForm):
    """Cadastra apenas os dados da empresa no model Empresa."""
    class Meta:
        model = Empresa
        fields = ['nome', 'cnpj']
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Razão social da empresa'}),
            'cnpj': forms.TextInput(attrs={'placeholder': '00.000.000/0000-00'}),
        }


class CadastroEmpresaLoginForm(forms.Form):
    """
    Formulário que o coordenador usa para criar uma empresa + login de acesso.
    Cria um User com tipo_usuario='empresa' e vincula ao model Empresa.
    """
    nome_empresa = forms.CharField(
        max_length=200,
        label='Nome da Empresa',
        widget=forms.TextInput(attrs={'placeholder': 'Razão social'}),
    )
    cnpj = forms.CharField(
        max_length=18,
        label='CNPJ',
        widget=forms.TextInput(attrs={'placeholder': '00.000.000/0000-00'}),
    )
    email = forms.EmailField(
        label='E-mail de acesso',
        widget=forms.EmailInput(attrs={'placeholder': 'empresa@email.com'}),
    )
    password = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={'placeholder': '••••••••'}),
    )

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(username=email).exists():
            raise forms.ValidationError('Este e-mail já está cadastrado.')
        return email

    def clean_cnpj(self):
        cnpj = self.cleaned_data['cnpj'].strip()
        if Empresa.objects.filter(cnpj=cnpj).exists():
            raise forms.ValidationError('Este CNPJ já está cadastrado.')
        return cnpj


class CadastroForm(forms.ModelForm):
    nome_completo = forms.CharField(max_length=150)
    matricula = forms.CharField(max_length=50, required=False)
    telefone = forms.CharField(max_length=20, required=False)
    tipo_usuario = forms.ChoiceField(choices=TIPOS_USUARIO, label='Tipo de Usuário')

    class Meta:
        model = User
        fields = ['email', 'password']
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'seu@email.com'}),
            'password': forms.PasswordInput(attrs={'placeholder': '••••••'}),
        }


class AtualizarPerfilForm(forms.ModelForm):
    nome_completo = forms.CharField(max_length=150, label='Nome Completo')
    telefone = forms.CharField(max_length=20, required=False, label='Telefone')
    matricula = forms.CharField(max_length=50, required=False, label='Matrícula')
    tipo_usuario = forms.ChoiceField(choices=PerfilUsuario.OPCOES_PERFIL, label='Tipo de Perfil')

    class Meta:
        model = PerfilUsuario
        fields = ['tipo_usuario', 'matricula', 'telefone']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['nome_completo'].initial = self.instance.user.first_name
