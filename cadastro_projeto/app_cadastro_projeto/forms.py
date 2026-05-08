from django import forms
from django.contrib.auth.models import User

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
    
    # Campo oculto para receber a seleção dos botões (Aluno, Professor, etc.) via JS
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