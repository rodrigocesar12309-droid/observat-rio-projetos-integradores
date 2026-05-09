from django import forms
from django.contrib.auth.models import User
from .models import PerfilUsuario


class CadastroForm(forms.ModelForm):
    nome_completo = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': 'Digite seu nome completo',
            'style': 'padding: 12px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 14px; outline: none; transition: border 0.2s;'
        })
    )
    matricula = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Sua matrícula (se houver)',
            'style': 'padding: 12px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 14px; outline: none;'
        })
    )
    telefone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'placeholder': '(81) 99999-9999',
            'style': 'padding: 12px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 14px; outline: none;'
        })
    )
    tipo_usuario = forms.CharField(
        widget=forms.HiddenInput(),
        initial='aluno'
    )

    class Meta:
        model = User
        fields = ['email', 'password']
        widgets = {
            'email': forms.EmailInput(attrs={
                'placeholder': 'seu@email.com',
                'style': 'padding: 12px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 14px; outline: none;'
            }),
            'password': forms.PasswordInput(attrs={
                'placeholder': '••••••',
                'style': 'padding: 12px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 14px; outline: none;'
            }),
        }


class AtualizarPerfilForm(forms.ModelForm):
    nome_completo = forms.CharField(
        max_length=150,
        label='Nome Completo',
        widget=forms.TextInput(attrs={
            'placeholder': 'Digite seu nome completo',
            'style': 'padding: 12px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 14px; outline: none;'
        })
    )
    telefone = forms.CharField(
        max_length=20,
        required=False,
        label='Telefone',
        widget=forms.TextInput(attrs={
            'placeholder': '(81) 99999-9999',
            'style': 'padding: 12px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 14px; outline: none;'
        })
    )
    matricula = forms.CharField(
        max_length=50,
        required=False,
        label='Matrícula',
        widget=forms.TextInput(attrs={
            'placeholder': 'Sua matrícula (se houver)',
            'style': 'padding: 12px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 14px; outline: none;'
        })
    )
    tipo_usuario = forms.ChoiceField(
        choices=PerfilUsuario.OPCOES_PERFIL,
        label='Tipo de Perfil',
        widget=forms.Select(attrs={
            'style': 'padding: 12px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 14px; outline: none;'
        })
    )

    class Meta:
        model = PerfilUsuario
        fields = ['tipo_usuario', 'matricula', 'telefone']

    # Injeta o nome_completo do User no form ao carregar
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['nome_completo'].initial = self.instance.user.first_name