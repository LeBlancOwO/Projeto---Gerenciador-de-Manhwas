from app.models.usuario import Usuario
from app.models.obras import Obras
from app.models.capitulo import Capitulo
from app.models.leitura import Leitura
from app.models.comentario import Comentario
from app.models.mensagem import Mensagem
from app.models.acompanhamento import Acompanhamento
from app.models.comunicado import Comunicado

# Cria todas as tabelas do sistema caso ainda não existam
Usuario.Criar_tabela()
Obras.Criar_tabela()
Capitulo.Criar_tabela()
Leitura.Criar_tabela()
Comentario.Criar_tabela()
Mensagem.Criar_tabela()
Acompanhamento.Criar_tabela()
Comunicado.Criar_tabela()

# Cadastra o usuário administrador inicial (ignora se já existir)
try:
    admin = Usuario(
        "Todo poderoso adm",
        "todopoderoso@admin.com",
        "Todo poderoso ;-;",
        "admin123",
        "admin"
    )
    admin.Salvar()
except Exception:
    pass

# Cadastra um usuário leitor de teste inicial (ignora se já existir)
try:
    leitor = Usuario(
        "Leitor Teste",
        "leitor@scan.com",
        "leitor_teste",
        "123456",
        "usuario"
    )
    leitor.Salvar()
except Exception:
    pass

print("Banco iniciado com sucesso.")