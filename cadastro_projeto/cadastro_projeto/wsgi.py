import os
import sys

# Adiciona o caminho do projeto ao Python path
path = '/home/cesarsilva5/observat-rio-projetos-integradores/cadastro_projeto'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cadastro_projeto.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
