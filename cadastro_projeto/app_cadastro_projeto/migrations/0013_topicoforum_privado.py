from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_cadastro_projeto', '0012_alter_projetousuario_conceito'),
    ]

    operations = [
        migrations.AddField(
            model_name='topicoforum',
            name='privado',
            field=models.BooleanField(
                default=False,
                help_text='Somente coordenadores e professores podem ver',
            ),
        ),
    ]
