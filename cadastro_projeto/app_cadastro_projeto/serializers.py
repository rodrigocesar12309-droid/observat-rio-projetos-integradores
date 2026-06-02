from rest_framework import serializers
from django.contrib.auth.models import User
from .models import PerfilUsuario, ProjetoUsuario


class PerfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerfilUsuario
        fields = ['tipo_usuario', 'matricula', 'telefone', 'ativo']


class UsuarioSerializer(serializers.ModelSerializer):
    perfil = PerfilSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'email', 'perfil']


class ProjetoSerializer(serializers.ModelSerializer):
    usuario = serializers.StringRelatedField()

    class Meta:
        model = ProjetoUsuario
        fields = [
            'id', 'titulo', 'descricao', 'categoria',
            'semestre', 'nota', 'status', 'tags',
            'link_repositorio', 'link_demo', 'criado_em'
        ]