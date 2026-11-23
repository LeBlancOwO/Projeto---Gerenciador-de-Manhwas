from app.models.conexao import Conexao
import sqlite3

class Obras:

    def __init__(self, titulo, autor, status):
        self.titulo = titulo
        self.autor = autor
        self.status = status

    @staticmethod
    def Criar_tabela():

        with Conexao() as cursor:

            cursor.execute(""" 
                CREATE TABLE IF NOT EXISTS Obras(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo vARCHAR(150) NOT NULL,
                autor VARCHAR(100) NOT NULL,
                status text NOT NULL
                )
            """)

    def Salvar(self):

        with Conexao() as cursor:

            cursor.execute("""
                INSERT INTO Obras
                (titulo, autor, status)
                VALUES (?, ?, ?)
            """, (
                self.titulo,
                self.autor,
                self.status
            ))

    @staticmethod
    def Listar():

        with Conexao() as cursor:

            cursor.execute("""
                SELECT *
                FROM Obras
            """)

            dados = cursor.fetchall()

        return dados