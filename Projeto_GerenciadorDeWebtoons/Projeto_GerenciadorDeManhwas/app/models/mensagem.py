from datetime import datetime
from app.db import DatabaseConnection


class Mensagem:
    """Model responsável pelo canal de mensagens e atualizações do usuário."""

    def __init__(self, usuario_id, categoria, titulo, conteudo, data_envio=None):
        self.usuario_id = usuario_id
        self.categoria = categoria
        self.titulo = titulo
        self.conteudo = conteudo
        self.data_envio = data_envio or datetime.now().strftime("%d/%m/%Y %H:%M")

    @staticmethod
    def Criar_tabela():
        """Cria a tabela Mensagens vinculada ao usuário."""
        with DatabaseConnection() as db:
            db.cursor.execute("""
                CREATE TABLE IF NOT EXISTS Mensagens(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario_id INTEGER NOT NULL,
                    categoria TEXT NOT NULL,
                    titulo TEXT NOT NULL,
                    conteudo TEXT NOT NULL,
                    lida INTEGER DEFAULT 0,
                    data_envio TEXT NOT NULL,
                    FOREIGN KEY (usuario_id) REFERENCES Usuarios(id) ON DELETE CASCADE
                )
            """)

    def Salvar(self):
        """Salva uma nova mensagem no canal do usuário."""
        with DatabaseConnection() as db:
            db.cursor.execute("""
                INSERT INTO Mensagens
                (usuario_id, categoria, titulo, conteudo, data_envio)
                VALUES (?, ?, ?, ?, ?)
            """, (
                self.usuario_id,
                self.categoria,
                self.titulo,
                self.conteudo,
                self.data_envio,
            ))

    @staticmethod
    def ListarPorUsuario(usuario_id):
        """Lista todas as mensagens de atualizações do usuário."""
        with DatabaseConnection() as db:
            db.cursor.execute("""
                SELECT *
                FROM Mensagens
                WHERE usuario_id = ? AND categoria = 'atualizacoes'
                ORDER BY id DESC
            """, (usuario_id,))
            return db.cursor.fetchall()

    @staticmethod
    def MarcarTodasComoLidas(usuario_id):
        """Marca as mensagens do usuário como lidas."""
        with DatabaseConnection() as db:
            db.cursor.execute("""
                UPDATE Mensagens
                SET lida = 1
                WHERE usuario_id = ? AND categoria = 'atualizacoes'
            """, (usuario_id,))

    @staticmethod
    def ContarNaoLidas(usuario_id):
        """Retorna o total de mensagens não lidas do usuário."""
        with DatabaseConnection() as db:
            db.cursor.execute("""
                SELECT COUNT(*) AS total
                FROM Mensagens
                WHERE usuario_id = ? AND categoria = 'atualizacoes' AND lida = 0
            """, (usuario_id,))
            row = db.cursor.fetchone()
            return row["total"] if row else 0
