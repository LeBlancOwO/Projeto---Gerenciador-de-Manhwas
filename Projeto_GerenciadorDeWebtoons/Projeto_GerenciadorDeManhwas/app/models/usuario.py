from app.db import DatabaseConnection
from werkzeug.security import generate_password_hash, check_password_hash


class Usuario:
    """Model responsável pelo gerenciamento de usuários, autenticação, penalidades e exclusão."""

    def __init__(self, nome, email, username, senha, tipo="usuario", foto=None, suspenso=0, strikes=0):
        self.nome = nome
        self.email = email
        self.username = username
        self.senha = senha
        self.tipo = tipo
        self.foto = foto
        self.suspenso = suspenso
        self.strikes = strikes

    @staticmethod
    def Criar_tabela():
        """Cria a tabela Usuarios e garante as colunas foto, suspenso e strikes (penalidades)."""
        with DatabaseConnection() as db:
            db.cursor.execute("""
                CREATE TABLE IF NOT EXISTS Usuarios(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome VARCHAR(100) NOT NULL,
                    email VARCHAR(100) NOT NULL UNIQUE,
                    username VARCHAR(100) NOT NULL UNIQUE,
                    senha_hash TEXT NOT NULL,
                    tipo TEXT NOT NULL,
                    foto TEXT,
                    suspenso INTEGER DEFAULT 0,
                    strikes INTEGER DEFAULT 0
                )
            """)
            db.cursor.execute("PRAGMA table_info(Usuarios)")
            colunas = [col["name"] for col in db.cursor.fetchall()]
            if "foto" not in colunas:
                db.cursor.execute("ALTER TABLE Usuarios ADD COLUMN foto TEXT")
            if "suspenso" not in colunas:
                db.cursor.execute("ALTER TABLE Usuarios ADD COLUMN suspenso INTEGER DEFAULT 0")
            if "strikes" not in colunas:
                db.cursor.execute("ALTER TABLE Usuarios ADD COLUMN strikes INTEGER DEFAULT 0")

    def Salvar(self):
        """Insere um novo usuário salvando apenas o hash criptográfico da senha."""
        senha_hash = generate_password_hash(self.senha)
        with DatabaseConnection() as db:
            db.cursor.execute("""
                INSERT INTO Usuarios
                (nome, email, username, senha_hash, tipo, foto, suspenso, strikes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.nome,
                self.email,
                self.username,
                senha_hash,
                self.tipo,
                self.foto,
                self.suspenso,
                self.strikes,
            ))

    @staticmethod
    def Autenticar(email, senha):
        """Busca o usuário pelo e-mail e valida a senha usando check_password_hash."""
        with DatabaseConnection() as db:
            db.cursor.execute("SELECT * FROM Usuarios WHERE email = ?", (email,))
            usuario = db.cursor.fetchone()

            if usuario is None:
                return None
            if check_password_hash(usuario["senha_hash"], senha):
                return usuario
            return None

    @staticmethod
    def Buscar_Id(id_usuario):
        """Retorna os dados do usuário pelo ID."""
        with DatabaseConnection() as db:
            db.cursor.execute("SELECT * FROM Usuarios WHERE id = ?", (id_usuario,))
            return db.cursor.fetchone()

    @staticmethod
    def Buscar_Por_Email_Ou_Username(email, username):
        """Verifica se já existe usuário cadastrado com o mesmo e-mail ou username."""
        with DatabaseConnection() as db:
            db.cursor.execute(
                "SELECT id FROM Usuarios WHERE email = ? OR username = ?",
                (email, username),
            )
            return db.cursor.fetchone()

    @staticmethod
    def BuscarPorEmailEUsername(email, username):
        """Localiza o usuário validando e-mail e username juntos para redefinição de senha."""
        with DatabaseConnection() as db:
            db.cursor.execute(
                "SELECT * FROM Usuarios WHERE email = ? AND username = ?",
                (email, username),
            )
            return db.cursor.fetchone()

    @staticmethod
    def AtualizarSenha(id_usuario, nova_senha):
        """Atualiza o hash da senha do usuário."""
        nova_hash = generate_password_hash(nova_senha)
        with DatabaseConnection() as db:
            db.cursor.execute(
                "UPDATE Usuarios SET senha_hash = ? WHERE id = ?",
                (nova_hash, id_usuario),
            )

    @staticmethod
    def AtualizarFoto(id_usuario, foto):
        """Atualiza o caminho da foto de perfil do usuário."""
        with DatabaseConnection() as db:
            db.cursor.execute(
                "UPDATE Usuarios SET foto = ? WHERE id = ?",
                (foto, id_usuario),
            )

    @staticmethod
    def AplicarPenalidade(id_usuario):
        """Incrementa em 1 a contagem de penalidades aprovadas e retorna o total atual."""
        with DatabaseConnection() as db:
            db.cursor.execute("""
                UPDATE Usuarios
                SET strikes = COALESCE(strikes, 0) + 1
                WHERE id = ?
            """, (id_usuario,))
            db.cursor.execute("SELECT strikes FROM Usuarios WHERE id = ?", (id_usuario,))
            row = db.cursor.fetchone()
            return row["strikes"] if row else 0

    @staticmethod
    def Excluir(id_usuario):
        """Exclui permanentemente a conta do usuário (e dados vinculados via CASCADE)."""
        with DatabaseConnection() as db:
            db.cursor.execute("DELETE FROM Usuarios WHERE id = ?", (id_usuario,))
            return db.cursor.rowcount