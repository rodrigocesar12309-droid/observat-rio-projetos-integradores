from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CadastroForm

def home(request):
    # Renderiza a tela de login/inicial (home.html)
    return render(request, 'usuarios/home.html')

def cadastrar_usuario(request):
    if request.method == 'POST':
        form = CadastroForm(request.POST)
        if form.is_valid():
            # Cria o objeto User mas não salva ainda no banco (commit=False)
            user = form.save(commit=False)
            
            # O Django exige um 'username'. Vamos usar o e-mail como username.
            user.username = form.cleaned_data['email']
            user.email = form.cleaned_data['email']
            
            # Criptografa a senha antes de salvar
            user.set_password(form.cleaned_data['password'])
            user.first_name = form.cleaned_data['nome_completo']
            user.save()
            
            # Captura os dados adicionais enviados
            tipo = form.cleaned_data['tipo_usuario']
            matricula = form.cleaned_data['matricula']
            telefone = form.cleaned_data['telefone']
            
            # Opcional: Você pode imprimir no terminal para testar se os dados chegaram
            print(f"Novo Usuário: {user.first_name} | Tipo: {tipo} | Matrícula: {matricula} | Tel: {telefone}")
            
            messages.success(request, f"Cadastro de {tipo.capitalize()} realizado com sucesso!")
            return redirect('home') # Redireciona de volta para a tela de login (home)
    else:
        form = CadastroForm()
        
    return render(request, 'usuarios/cadastro.html', {'form': form})
