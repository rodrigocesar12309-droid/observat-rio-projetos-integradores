import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cadastro_projeto.settings')
django.setup()

from django.contrib.auth.models import User
from app_cadastro_projeto.models import PerfilUsuario

# Cria usuario admin limpo
User.objects.filter(username='senac@admin.com').delete()
u = User.objects.create_user(
    username='senac@admin.com',
    email='senac@admin.com',
    password='senac2026',
    first_name='Coordenador Senac'
)
PerfilUsuario.objects.create(user=u, tipo_usuario='administracao')
print('CRIADO: senac@admin.com / senac2026 / tipo: administracao')

# Testa o login
from django.contrib.auth import authenticate
r = authenticate(username='senac@admin.com', password='senac2026')
print('TESTE LOGIN:', 'OK' if r else 'FALHOU')
