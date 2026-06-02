import os
import sys

# 1. Caminho da pasta principal do seu projeto (onde fica o manage.py)
path = '/home/cesarsilva5/observat-rio-projetos-integradores'
if path not in sys.path:
    sys.path.append(path)

# 2. Configuração do ambiente do Django
# (Aqui dizemos ao Python onde encontrar o seu arquivo settings.py)
os.environ['DJANGO_SETTINGS_MODULE'] = 'projeto_cadastro.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
