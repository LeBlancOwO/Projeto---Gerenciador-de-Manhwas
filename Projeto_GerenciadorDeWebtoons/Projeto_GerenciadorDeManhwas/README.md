# Gerenciador de Manhwas (Scan)

Aplicação web MPA (Multi-Page Application) desenvolvida em Python, Flask, Jinja2 e SQLite3 seguindo a arquitetura MVC com Blueprints para a disciplina **Laboratório de Programação 1 (SPOLBP1)**.

## Funcionalidades
- **Autenticação de Usuários:** Cadastro, Login e Logout com hash seguro (`werkzeug.security`), sessão no servidor e middleware `@login_required` com `g.usuario`.
- **Gerenciamento de Obras (Manhwas):** Cadastro (com upload de capa), listagem pública com filtro por título/status, listagem pessoal ("Minhas Obras"), edição e exclusão validando o dono do registro.
- **Moderação (Admin):** Aprovação e desaprovação de obras com justificativa.
- **Gerenciamento de Capítulos:** Cadastro, listagem, edição e exclusão de capítulos vinculados a cada obra, validando o dono.
- **Recursos Extras:** Alternância de tema claro/escuro via cookies (`max_age=30 dias`), flash messages categorizadas, páginas de erro personalizadas (`404` e `403`) e logs com `app.logger`.

## Como executar
1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
2. Inicialize o banco de dados:
   ```bash
   python iniciar_bd.py
   ```
3. Inicie o servidor Flask:
   ```bash
   python run.py
   ```
4. Acesse `http://127.0.0.1:5000` no navegador.

## Credenciais de Teste (`iniciar_bd.py`)
- **Administrador:** `todopoderoso@admin.com` / `admin123`
- **Usuário comum:** `leitor@scan.com` / `123456`
