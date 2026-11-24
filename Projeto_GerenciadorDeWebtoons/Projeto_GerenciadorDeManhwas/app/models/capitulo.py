from datetime import datetime
from app.db import DatabaseConnection


class Capitulo:
    """Model responsável pelos capítulos vinculados a cada obra."""

    def __init__(self, numero, titulo, conteudo, obra_id, usuario_id, data_lancamento=None):
        self.numero = numero
        self.titulo = titulo
        self.conteudo = conteudo
        self.obra_id = obra_id
        self.usuario_id = usuario_id
        self.data_lancamento = data_lancamento or datetime.now().strftime("%d/%m/%Y")

    @staticmethod
    def Criar_tabela():
        """Cria a tabela Capitulos e garante a coluna data_lancamento."""
        with DatabaseConnection() as db:
            db.cursor.execute("""
                CREATE TABLE IF NOT EXISTS Capitulos(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero INTEGER NOT NULL,
                    titulo VARCHAR(150) NOT NULL,
                    conteudo TEXT NOT NULL,
                    data_lancamento TEXT NOT NULL,
                    obra_id INTEGER NOT NULL,
                    usuario_id INTEGER NOT NULL,
                    FOREIGN KEY (obra_id) REFERENCES Obras(id) ON DELETE CASCADE,
                    FOREIGN KEY (usuario_id) REFERENCES Usuarios(id) ON DELETE CASCADE
                )
            """)
            db.cursor.execute("PRAGMA table_info(Capitulos)")
            colunas = [col["name"] for col in db.cursor.fetchall()]
            if "data_lancamento" not in colunas:
                db.cursor.execute("ALTER TABLE Capitulos ADD COLUMN data_lancamento TEXT")

    @staticmethod
    def ProximoNumero(obra_id):
        """Retorna o próximo número sequencial para a obra (usado automaticamente ao criar)."""
        with DatabaseConnection() as db:
            db.cursor.execute(
                "SELECT COALESCE(MAX(numero), 0) + 1 AS prox FROM Capitulos WHERE obra_id = ?",
                (obra_id,),
            )
            row = db.cursor.fetchone()
            return row["prox"] if row else 1

    def Salvar(self):
        """Insere um novo capítulo no banco de dados."""
        with DatabaseConnection() as db:
            db.cursor.execute("""
                INSERT INTO Capitulos
                (numero, titulo, conteudo, data_lancamento, obra_id, usuario_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                self.numero,
                self.titulo,
                self.conteudo,
                self.data_lancamento,
                self.obra_id,
                self.usuario_id
            ))

    @staticmethod
    def ListarPorObra(obra_id):
        """Lista todos os capítulos de uma obra em ordem de criação/sequência."""
        with DatabaseConnection() as db:
            db.cursor.execute("""
                SELECT *
                FROM Capitulos
                WHERE obra_id = ?
                ORDER BY numero ASC, id ASC
            """, (obra_id,))
            return db.cursor.fetchall()

    @staticmethod
    def BuscarPorId(id_capitulo):
        """Busca um capítulo pelo ID."""
        with DatabaseConnection() as db:
            db.cursor.execute("SELECT * FROM Capitulos WHERE id = ?", (id_capitulo,))
            return db.cursor.fetchone()

    @staticmethod
    def BuscarPorIdEUsuario(id_capitulo, usuario_id):
        """Busca um capítulo garantindo que pertença ao usuário informado."""
        with DatabaseConnection() as db:
            db.cursor.execute(
                "SELECT * FROM Capitulos WHERE id = ? AND usuario_id = ?",
                (id_capitulo, usuario_id),
            )
            return db.cursor.fetchone()

    @staticmethod
    def Atualizar(id_capitulo, usuario_id, titulo, conteudo):
        """Atualiza título e conteúdo do capítulo validando o dono."""
        with DatabaseConnection() as db:
            db.cursor.execute("""
                UPDATE Capitulos
                SET titulo = ?, conteudo = ?
                WHERE id = ? AND usuario_id = ?
            """, (titulo, conteudo, id_capitulo, usuario_id))

    @staticmethod
    def Excluir(id_capitulo, usuario_id):
        """Exclui o capítulo validando o dono."""
        with DatabaseConnection() as db:
            db.cursor.execute(
                "DELETE FROM Capitulos WHERE id = ? AND usuario_id = ?",
                (id_capitulo, usuario_id),
            )
            return db.cursor.rowcount
