from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_cadastro_projeto', '0008_projetousuario_conceito_comentario'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projetousuario',
            name='conceito',
            field=models.CharField(
                blank=True,
                choices=[
                    ('Ótimo', 'Ótimo'),
                    ('Excelente', 'Excelente'),
                    ('Bom', 'Bom'),
                    ('Suficiente', 'Suficiente'),
                    ('Insuficiente', 'Insuficiente'),
                ],
                max_length=20,
                null=True,
            ),
        ),
    ]
