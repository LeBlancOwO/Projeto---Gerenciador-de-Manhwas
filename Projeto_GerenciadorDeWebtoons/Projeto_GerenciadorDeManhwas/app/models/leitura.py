from datetime import datetime
from app.db import DatabaseConnection


class Leitura:
    """Model responsável por registrar quais capítulos cada usuário já leu."""

    @staticmethod
    def Criar_tabela():
        """Cria a tabela Leituras evitando duplicidade entre usuario_id e capitulo_id."""
        with DatabaseConnection() as db:
            db.cursor.execute("""
                CREATE TABLE IF NOT EXISTS Leituras(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario_id INTEGER NOT NULL,
                    capitulo_id INTEGER NOT NULL,
                    data_leitura TEXT NOT NULL,
                    UNIQUE(usuario_id, capitulo_id),
                    FOREIGN KEY (usuario_id) REFERENCES Usuarios(id) ON DELETE CASCADE,
                    FOREIGN KEY (capitulo_id) REFERENCES Capitulos(id) ON DELETE CASCADE
                )
            """)

    @staticmethod
    def Registrar(usuario_id, capitulo_id):
        """Registra a leitura de um capítulo pelo usuário (ignora se já tiver sido lido)."""
        data_leitura = datetime.now().strftime("%d/%m/%Y %H:%M")
        with DatabaseConnection() as db:
            db.cursor.execute("""
                INSERT OR IGNORE INTO Leituras (usuario_id, capitulo_id, data_leitura)
                VALUES (?, ?, ?)
            """, (usuario_id, capitulo_id, data_leitura))

    @staticmethod
    def ListarCapitulosLidosPorUsuarioEObra(usuario_id, obra_id):
        """Retorna um conjunto (set) com os IDs dos capítulos já lidos pelo usuário na obra."""
        with DatabaseConnection() as db:
            db.cursor.execute("""
                SELECT l.capitulo_id
                FROM Leituras l
                INNER JOIN Capitulos c ON c.id = l.capitulo_id
                WHERE l.usuario_id = ? AND c.obra_id = ?
            """, (usuario_id, obra_id))
            return {row["capitulo_id"] for row in db.cursor.fetchall()}
