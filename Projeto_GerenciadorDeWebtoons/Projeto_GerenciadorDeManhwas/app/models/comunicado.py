from datetime import datetime
from app.db import DatabaseConnection


class Comunicado:
    """Model responsável pelos comunicados importantes publicados pelo administrador na tela inicial."""

    def __init__(self, titulo, conteudo, admin_id, data_publicacao=None):
        self.titulo = titulo
        self.conteudo = conteudo
        self.admin_id = admin_id
        self.data_publicacao = data_publicacao or datetime.now().strftime("%d/%m/%Y %H:%M")

    @staticmethod
    def Criar_tabela():
        """Cria a tabela Comunicados vinculada ao administrador autor."""
        with DatabaseConnection() as db:
            db.cursor.execute("""
                CREATE TABLE IF NOT EXISTS Comunicados(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    titulo VARCHAR(150) NOT NULL,
                    conteudo TEXT NOT NULL,
                    data_publicacao TEXT NOT NULL,
                    admin_id INTEGER NOT NULL,
                    FOREIGN KEY (admin_id) REFERENCES Usuarios(id) ON DELETE CASCADE
                )
            """)

    def Salvar(self):
        """Salva um novo comunicado no banco de dados."""
        with DatabaseConnection() as db:
            db.cursor.execute("""
                INSERT INTO Comunicados (titulo, conteudo, data_publicacao, admin_id)
                VALUES (?, ?, ?, ?)
            """, (self.titulo, self.conteudo, self.data_publicacao, self.admin_id))

    @staticmethod
    def Listar():
        """Lista os comunicados mais recentes com o username do administrador."""
        with DatabaseConnection() as db:
            db.cursor.execute("""
                SELECT c.*, u.username AS admin_username
                FROM Comunicados c
                INNER JOIN Usuarios u ON u.id = c.admin_id
                ORDER BY c.id DESC
                LIMIT 5
            """)
            return db.cursor.fetchall()

    @staticmethod
    def Excluir(id_comunicado):
        """Exclui um comunicado pelo ID."""
        with DatabaseConnection() as db:
            db.cursor.execute("DELETE FROM Comunicados WHERE id = ?", (id_comunicado,))
            return db.cursor.rowcount
