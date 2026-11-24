from app.db import DatabaseConnection


class Acompanhamento:
    """Model responsável por registrar quais obras cada usuário está acompanhando."""

    @staticmethod
    def Criar_tabela():
        """Cria a tabela Acompanhamentos evitando duplicidade entre usuario_id e obra_id."""
        with DatabaseConnection() as db:
            db.cursor.execute("""
                CREATE TABLE IF NOT EXISTS Acompanhamentos(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario_id INTEGER NOT NULL,
                    obra_id INTEGER NOT NULL,
                    UNIQUE(usuario_id, obra_id),
                    FOREIGN KEY (usuario_id) REFERENCES Usuarios(id) ON DELETE CASCADE,
                    FOREIGN KEY (obra_id) REFERENCES Obras(id) ON DELETE CASCADE
                )
            """)

    @staticmethod
    def EstaAcompanhando(usuario_id, obra_id):
        """Verifica se o usuário já acompanha a obra."""
        with DatabaseConnection() as db:
            db.cursor.execute("""
                SELECT id FROM Acompanhamentos
                WHERE usuario_id = ? AND obra_id = ?
            """, (usuario_id, obra_id))
            return db.cursor.fetchone() is not None

    @staticmethod
    def Alternar(usuario_id, obra_id):
        """Começa a acompanhar se não acompanhava, ou deixa de acompanhar se já acompanhava."""
        with DatabaseConnection() as db:
            db.cursor.execute("""
                SELECT id FROM Acompanhamentos
                WHERE usuario_id = ? AND obra_id = ?
            """, (usuario_id, obra_id))
            existente = db.cursor.fetchone()
            if existente:
                db.cursor.execute("DELETE FROM Acompanhamentos WHERE id = ?", (existente["id"],))
                return False
            db.cursor.execute("""
                INSERT INTO Acompanhamentos (usuario_id, obra_id)
                VALUES (?, ?)
            """, (usuario_id, obra_id))
            return True

    @staticmethod
    def ListarSeguidores(obra_id):
        """Retorna os IDs dos usuários que acompanham uma obra."""
        with DatabaseConnection() as db:
            db.cursor.execute("""
                SELECT usuario_id FROM Acompanhamentos
                WHERE obra_id = ?
            """, (obra_id,))
            return [row["usuario_id"] for row in db.cursor.fetchall()]
