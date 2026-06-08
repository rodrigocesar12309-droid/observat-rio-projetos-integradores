from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_cadastro_projeto', '0009_alter_projetousuario_conceito'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TopicoForum',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=200)),
                ('conteudo', models.TextField()),
                ('categoria', models.CharField(
                    choices=[('duvida','Dúvida'),('discussao','Discussão'),('aviso','Aviso'),('projeto','Projeto')],
                    default='duvida', max_length=20)),
                ('fixado', models.BooleanField(default=False)),
                ('ativo', models.BooleanField(default=True)),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('atualizado_em', models.DateTimeField(auto_now=True)),
                ('autor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                    related_name='topicos', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-fixado', '-criado_em']},
        ),
        migrations.CreateModel(
            name='RespostaForum',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('conteudo', models.TextField()),
                ('ativo', models.BooleanField(default=True)),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('autor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                    related_name='respostas_forum', to=settings.AUTH_USER_MODEL)),
                ('topico', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                    related_name='respostas', to='app_cadastro_projeto.topicoforum')),
            ],
            options={'ordering': ['criado_em']},
        ),
    ]
