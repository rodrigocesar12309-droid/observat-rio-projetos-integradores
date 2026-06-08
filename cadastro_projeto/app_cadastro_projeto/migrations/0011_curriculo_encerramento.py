from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_cadastro_projeto', '0010_topicoforum_respostaforum'),
    ]

    operations = [
        # Campos de currículo no PerfilUsuario
        migrations.AddField(
            model_name='perfilusuario',
            name='cargo',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='perfilusuario',
            name='linkedin',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='perfilusuario',
            name='github',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='perfilusuario',
            name='habilidades',
            field=models.CharField(blank=True, help_text='Separe por vírgula', max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='perfilusuario',
            name='experiencia',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='perfilusuario',
            name='formacao',
            field=models.TextField(blank=True, null=True),
        ),
        # Campos de encerramento no ProjetoUsuario
        migrations.AddField(
            model_name='projetousuario',
            name='encerrado',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='projetousuario',
            name='encerrado_em',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
