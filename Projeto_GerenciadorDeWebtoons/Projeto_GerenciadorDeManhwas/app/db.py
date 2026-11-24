import sqlite3
import os

# Caminho absoluto até a raiz do projeto para localizar o arquivo do banco SQLite
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "app", "banco_sistema.db")


class DatabaseConnection:
    """Gerenciador de contexto (Aula 15) para conexão segura com o SQLite3."""

    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def __enter__(self):
        # Abre a conexão, configura retorno como dicionário (Row) e ativa chaves estrangeiras
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Salva (commit) se não houve erro; desfaz (rollback) em caso de exceção; e fecha a conexão
        if exc_type is None:
            self.conn.commit()
        else:
            self.conn.rollback()
        self.conn.close()
