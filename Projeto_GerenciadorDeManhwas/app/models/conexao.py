import sqlite3

class Conexao:

    BANCO = "banco.db"

    @classmethod
    def conectar(cls):
        return sqlite3.connect(cls.BANCO)
    
    def __enter__(self):
        self.conn = self.conectar()
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.conn.close()