from datetime import datetime
from app.db import DatabaseConnection


class Comentario:
    """Model responsável pelos comentários dos leitores em obras e capítulos."""

    def __init__(self, texto, usuario_id, capitulo_id=None, obra_id=None, data_criacao=None):
        self.texto = texto
        self.usuario_id = usuario_id
        self.capitulo_id = capitulo_id
        self.obra_id = obra_id
        self.data_criacao = data_criacao or datetime.now().strftime("%d/%m/%Y %H:%M")

    @staticmethod
    def Criar_tabela():
        """Cria a tabela Comentarios com capitulo_id opcional e migra tabelas antigas se necessário."""
        with DatabaseConnection() as db:
            db.cursor.execute("""
                CREATE TABLE IF NOT EXISTS Comentarios(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    texto TEXT NOT NULL,
                    data_criacao TEXT NOT NULL,
                    capitulo_id INTEGER,
                    obra_id INTEGER,
                    usuario_id INTEGER NOT NULL,
                    FOREIGN KEY (capitulo_id) REFERENCES Capitulos(id) ON DELETE CASCADE,
                    FOREIGN KEY (obra_id) REFERENCES Obras(id) ON DELETE CASCADE,
                    FOREIGN KEY (usuario_id) REFERENCES Usuarios(id) ON DELETE CASCADE
                )
            """)
            db.cursor.execute("PRAGMA table_info(Comentarios)")
            colunas = db.cursor.fetchall()
            nomes = [col["name"] for col in colunas]
            cap_notnull = any(col["name"] == "capitulo_id" and col["notnull"] == 1 for col in colunas)

            if cap_notnull:
                db.cursor.execute("""
                    CREATE TABLE Comentarios_nova(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        texto TEXT NOT NULL,
                        data_criacao TEXT NOT NULL,
                        capitulo_id INTEGER,
                        obra_id INTEGER,
                        usuario_id INTEGER NOT NULL,
                        FOREIGN KEY (capitulo_id) REFERENCES Capitulos(id) ON DELETE CASCADE,
                        FOREIGN KEY (obra_id) REFERENCES Obras(id) ON DELETE CASCADE,
                        FOREIGN KEY (usuario_id) REFERENCES Usuarios(id) ON DELETE CASCADE
                    )
                """)
                if "obra_id" in nomes:
                    db.cursor.execute("""
                        INSERT INTO Comentarios_nova (id, texto, data_criacao, capitulo_id, obra_id, usuario_id)
                        SELECT id, texto, data_criacao, capitulo_id, obra_id, usuario_id FROM Comentarios
                    """)
                else:
                    db.cursor.execute("""
                        INSERT INTO Comentarios_nova (id, texto, data_criacao, capitulo_id, obra_id, usuario_id)
                        SELECT id, texto, data_criacao, capitulo_id, NULL, usuario_id FROM Comentarios
                    """)
                db.cursor.execute("DROP TABLE Comentarios")
                db.cursor.execute("ALTER TABLE Comentarios_nova RENAME TO Comentarios")
            elif "obra_id" not in nomes:
                db.cursor.execute("ALTER TABLE Comentarios ADD COLUMN obra_id INTEGER")

    def Salvar(self):
        """Salva um novo comentário (de obra ou de capítulo) no banco."""
        with DatabaseConnection() as db:
            db.cursor.execute("""
                INSERT INTO Comentarios (texto, data_criacao, capitulo_id, obra_id, usuario_id)
                VALUES (?, ?, ?, ?, ?)
            """, (self.texto, self.data_criacao, self.capitulo_id, self.obra_id, self.usuario_id))

    @staticmethod
    def BuscarPorId(id_comentario):
        """Busca um comentário pelo ID."""
        with DatabaseConnection() as db:
            db.cursor.execute("SELECT * FROM Comentarios WHERE id = ?", (id_comentario,))
            return db.cursor.fetchone()

    @staticmethod
    def ListarPorCapitulo(capitulo_id):
        """Lista os comentários de um capítulo trazendo username e foto do autor."""
        with DatabaseConnection() as db:
            db.cursor.execute("""
                SELECT c.*, u.username, u.foto
                FROM Comentarios c
                INNER JOIN Usuarios u ON u.id = c.usuario_id
                WHERE c.capitulo_id = ?
                ORDER BY c.id DESC
            """, (capitulo_id,))
            return db.cursor.fetchall()

    @staticmethod
    def ListarPorObra(obra_id):
        """Lista os comentários gerais de uma obra trazendo username e foto do autor."""
        with DatabaseConnection() as db:
            db.cursor.execute("""
                SELECT c.*, u.username, u.foto
                FROM Comentarios c
                INNER JOIN Usuarios u ON u.id = c.usuario_id
                WHERE c.obra_id = ? AND c.capitulo_id IS NULL
                ORDER BY c.id DESC
            """, (obra_id,))
            return db.cursor.fetchall()

    @staticmethod
    def Excluir(id_comentario, usuario_id):
        """Exclui um comentário validando se ele pertence ao usuário autenticado."""
        with DatabaseConnection() as db:
            db.cursor.execute("""
                DELETE FROM Comentarios
                WHERE id = ? AND usuario_id = ?
            """, (id_comentario, usuario_id))
            return db.cursor.rowcount
