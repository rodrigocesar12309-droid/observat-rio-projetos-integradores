from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_cadastro_projeto', '0007_empresa'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='projetousuario',
            name='nota',
        ),
        migrations.AddField(
            model_name='projetousuario',
            name='conceito',
            field=models.CharField(
                blank=True,
                choices=[
                    ('Excelente', 'Excelente'),
                    ('Bom', 'Bom'),
                    ('Suficiente', 'Suficiente'),
                    ('Insuficiente', 'Insuficiente'),
                ],
                max_length=20,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='projetousuario',
            name='comentario_professor',
            field=models.TextField(
                blank=True,
                null=True,
                verbose_name='Comentário do Professor',
            ),
        ),
    ]
