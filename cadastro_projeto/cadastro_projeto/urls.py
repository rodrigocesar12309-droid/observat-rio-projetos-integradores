from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app_cadastro_projeto.urls')),  # inclui as rotas do app
]
