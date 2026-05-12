# 📚 Observatório de Projetos Integradores
 
> Sistema web centralizado para submissão e avaliação de Projetos Integradores do curso de ADS – Senac/Fecomércio/Sesc.
 
---
 
## 📋 Descrição do Sistema
 
O **Observatório de Projetos Integradores** é uma plataforma web desenvolvida para centralizar o envio, a avaliação e a consulta dos Projetos Integradores (PIs) do curso de Análise e Desenvolvimento de Sistemas (ADS). O sistema substitui o processo atual de envio por e-mail e Teams, eliminando problemas de desorganização, perda de arquivos e dificuldade no controle de versões.
 
---
 
## 🎯 Objetivo
 
Centralizar a submissão e avaliação dos Projetos Integradores em uma única plataforma, criando também um portfólio digital dos alunos acessível a empresas parceiras para identificação e recrutamento de novos talentos.
 
---
 
## 👥 Partes Interessadas (Stakeholders)
 
| Perfil | Funcionalidades |
|---|---|
| **Aluno** | Submissão de projetos, criação de portfólio profissional |
| **Professor** | Avaliação de projetos por rubrica, filtro por turma |
| **Coordenador/Adm** | Gestão de usuários, relatórios, visão estratégica |
| **Empresa Parceira** | Consulta de projetos, identificação de talentos |
 
---
 
## ⚙️ Funcionalidades
 
### Painel do Aluno
- Submeter novo projeto (Create)
- Visualizar seus projetos (Read)
- Editar/atualizar arquivos do projeto (Update)
- Excluir projeto (Delete)
### Painel do Professor
- Visualizar todos os projetos
- Filtrar projetos por turma
- Avaliar projetos com rubrica
- Registrar quem realizou a avaliação
### Painel Administrativo (Coordenador)
- Gestão de usuários
- Gestão de projetos
- Acompanhamento geral dos PIs
- Geração de relatórios
### Portfólio Público (Empresas Parceiras)
- Visualização dos projetos desenvolvidos pelos alunos
- Identificação de talentos
- Recrutamento de estudantes
---
 
## 🔧 Tecnologias Utilizadas
 
- **Linguagem:** Python
- **Frameworks:** Django / Flask
- **Front-end:** HTML5, CSS3, Bootstrap
- **Banco de Dados:** A definir (MySQL / PostgreSQL / SQLite)
- **Versionamento:** Git & GitHub
- **Gerenciamento:** Trello
> As tecnologias podem ser ajustadas ao longo do projeto conforme necessidades técnicas identificadas pela equipe.
 
---
 
## 🗄️ Banco de Dados
 
- Modelo Conceitual: `docs/modelo-conceitual.png`
- Modelo Lógico: `docs/modelo-logico.png`
- CRUD implementado diretamente no sistema via ORM
---
 
## 📏 Regras de Negócio
 
1. O cadastro de novos usuários só pode ser realizado pelo **Administrador/Coordenador**.
2. Cada aluno só visualiza e edita seus próprios projetos.
3. Professores podem visualizar projetos de **todas as turmas**, mas filtram por turma.
4. A avaliação de um projeto deve registrar **qual professor** a realizou.
5. O portfólio público exibe apenas projetos **aprovados/publicados**.
6. Todos os dados dos usuários devem seguir as diretrizes da **LGPD**.
---
 
## 🚀 Como Executar o Projeto
 
```bash
# 1. Clone o repositório
git clone https://github.com/rodrigocesar12309-droid/projeto-integrador-senac.git
 
# 2. Acesse a pasta do projeto
cd projeto-integrador-senac
 
# 3. Crie e ative o ambiente virtual
python -m venv venv
source venv/bin/activate       # Linux/macOS
venv\Scripts\activate          # Windows
 
# 4. Instale as dependências
pip install -r requirements.txt
 
# 5. Execute as migrações do banco de dados
python manage.py migrate
 
# 6. Inicie o servidor
python manage.py runserver
```
 
Acesse em: `http://localhost:8000`
 
---
 
## 📁 Estrutura do Repositório
 
```
projeto-integrador-senac/
│
├── docs/                  # Documentação, modelos de BD, requisitos
├── static/                # Arquivos estáticos (CSS, JS, imagens)
├── templates/             # Templates HTML
├── app/                   # Módulo principal da aplicação
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── forms.py
├── requirements.txt
├── manage.py
└── README.md
```
 
---
 
## 📄 Documentação
 
A documentação completa do projeto (requisitos, casos de uso, protótipos) está disponível em: `docs/`
 
## 🎨 Protótipo
 
O protótipo visual do sistema foi desenvolvido no Figma e pode ser acessado pelo link abaixo:
 
🔗 [Acessar Protótipo no Figma](https://www.figma.com/make/6UaE4T1ZRB7Mpm61Qn9u3D/Observat%C3%B3rio-de-Projetos-Integradores?fullscreen=1&t=nB54wIyAlGkIHngc-1)
 
---
 
## 📜 Licença
 
Este projeto foi desenvolvido para fins acadêmicos no curso de **Análise e Desenvolvimento de Sistemas – Senac/Fecomércio/Sesc**.
 
---
 
---
 
# 📚 Integrative Projects Observatory — English Version
 
> A centralized web system for submitting and evaluating Integrative Projects for the ADS program – Senac/Fecomércio/Sesc.
 
---
 
## 📋 System Description
 
The **Integrative Projects Observatory** is a web platform built to centralize the submission, evaluation, and browsing of Integrative Projects (IPs) from the Systems Analysis and Development (ADS) program. It replaces the current process of sending files via email and Teams, eliminating disorganization, file loss, and version control difficulties.
 
---
 
## 🎯 Objective
 
Centralize the submission and evaluation of Integrative Projects in a single platform, while also creating a digital portfolio for students that is accessible to partner companies for talent identification and recruitment.
 
---
 
## 👥 Stakeholders
 
| Profile | Features |
|---|---|
| **Student** | Project submission, professional portfolio creation |
| **Teacher** | Project evaluation with rubric, class filtering |
| **Coordinator/Admin** | User management, reports, strategic overview |
| **Partner Company** | Browse projects, talent identification |
 
---
 
## ⚙️ Features
 
### Student Panel
- Submit a new project (Create)
- View own projects (Read)
- Edit/update project files (Update)
- Delete project (Delete)
### Teacher Panel
- View all projects
- Filter projects by class
- Evaluate projects using a rubric
- Record who performed the evaluation
### Admin Panel (Coordinator)
- User management
- Project management
- General IP tracking
- Report generation
### Public Portfolio (Partner Companies)
- Browse student-developed projects
- Talent identification
- Student recruitment
---
 
## 🔧 Technologies Used
 
- **Language:** Python
- **Frameworks:** Django / Flask
- **Front-end:** HTML5, CSS3, Bootstrap
- **Database:** TBD (MySQL / PostgreSQL / SQLite)
- **Version Control:** Git & GitHub
- **Project Management:** Trello
> Technologies may be adjusted throughout the project as needed by the team.
 
---
 
## 📏 Business Rules
 
1. New user registration can only be performed by the **Administrator/Coordinator**.
2. Each student can only view and edit their own projects.
3. Teachers can view projects from **all classes** but may filter by class.
4. Every project evaluation must record **which teacher** performed it.
5. The public portfolio displays only **approved/published** projects.
6. All user data must comply with **Brazilian Data Protection Law (LGPD)**.
---
 
## 🚀 How to Run the Project
 
```bash
# 1. Clone the repository
git clone https://github.com/rodrigocesar12309-droid/projeto-integrador-senac.git
 
# 2. Navigate to the project folder
cd projeto-integrador-senac
 
# 3. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate       # Linux/macOS
venv\Scripts\activate          # Windows
 
# 4. Install dependencies
pip install -r requirements.txt
 
# 5. Run database migrations
python manage.py migrate
 
# 6. Start the development server
python manage.py runserver
```
 
Access at: `http://localhost:8000`
 
---
 
## 📁 Repository Structure
 
```
projeto-integrador-senac/
│
├── docs/                  # Documentation, DB models, requirements
├── static/                # Static files (CSS, JS, images)
├── templates/             # HTML templates
├── app/                   # Main application module
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── forms.py
├── requirements.txt
├── manage.py
└── README.md
```
 
---
 
## 📄 Documentation
 
Full project documentation (requirements, use cases, prototypes) is available in: `docs/`
 
## 🎨 Prototype
 
The visual prototype was designed in Figma and can be accessed at the link below:
 
🔗 [View Figma Prototype](https://www.figma.com/make/6UaE4T1ZRB7Mpm61Qn9u3D/Observat%C3%B3rio-de-Projetos-Integradores?fullscreen=1&t=nB54wIyAlGkIHngc-1)
 
---
 
## 📜 License
 
This project was developed for academic purposes as part of the **Systems Analysis and Development – Senac/Fecomércio/Sesc** program.
 

