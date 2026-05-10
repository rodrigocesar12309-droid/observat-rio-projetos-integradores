# 🚧 Sistema de Cadastro de Projetos Integradores — Senac PE  
**Case Acadêmico · Senac PE**

---

## 📋 Sobre o Projeto
Aplicação web para **cadastro, gerenciamento e avaliação de projetos integradores** dos alunos do Senac Pernambuco.  

O sistema permite:
- Cadastro de usuários (restrito a **administração** e **professor**)  
- Painel do aluno com CRUD de projetos  
- Dashboard com indicadores de desempenho (aprovados, em avaliação, média de notas)  
- Organização por semestre, categoria e status  
- Registro de atividades (logs de login, criação, edição e exclusão)  

---

## 👥 Time
| Responsável | Função | Componente/Arquivo |
|--------------|--------|--------------------|
| **Rodrigo César** | Gestor | Configuração geral, views, models |
| **Wictor Eduardo** | UI/UX Designer | Templates HTML, CSS, responsividade |
| **Filipe Araújo** | Desenvolvedor Front-end | Integração Django + JS, formulários |

---

## 🗂️ Estrutura de Código
cadastro_projetos/

├── app_cadastro_projeto/

│   ├── models.py        → Rodrigo (modelagem de dados)

│   ├── views.py         → Rodrigo (lógica de negócio e restrições)

│   ├── forms.py         → Filipe (formulários de cadastro/edição)

│   ├── templates/
│   │   ├── dashboard.html   → Wictor (UI/UX)

│   │   ├── cadastro.html    → formulário de novos usuários

│   │   └── editar_projeto.html

│   └── static/
│       └── css/             → Wictor (estilos globais)

├── manage.py

├── requirements.txt

└── README.md


---

## 🚀 Como Rodar

### Pré-requisitos
- Python 3.11+  
- Django 5.x  
- SQLite (padrão)

### Instalação
```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/cadastro-projetos.git
cd cadastro-projetos

# 2. Crie o ambiente virtual
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Rode o servidor
python manage.py runserver

Acesse: http://localhost:8000 (localhost in Bing)

📦 Dependências Principais
Django — Framework principal

Bootstrap — Estilização e responsividade

SQLite — Banco de dados padrão

Pillow — Upload de imagens de perfil

Cadastro de Usuário (restrito a admin/professor)
      ↓
views.py (cadastrar_usuario)
      ↓
models.PerfilUsuario + User
      ↓
Dashboard (CRUD de projetos)
🤝 Colaborações
Rodrigo + Filipe: lógica de cadastro e restrição de usuários

Wictor + Filipe: integração dos formulários com UI responsiva

Rodrigo + Wictor: dashboard com indicadores visuais

🧠 Licença
Este projeto é de uso acadêmico e foi desenvolvido para fins educacionais no Senac Pernambuco.


---

Esse formato segue o padrão dos melhores projetos Django no GitHub — com seções bem delimitadas, blocos de código e ícones para facilitar a leitura.  

Quer que eu adicione também uma seção de **[badges e status do projeto](ca://s?q=Adicionar_badges_e_status_no_README_GitHub)** (como versão do Python, build, licença e autor)?
