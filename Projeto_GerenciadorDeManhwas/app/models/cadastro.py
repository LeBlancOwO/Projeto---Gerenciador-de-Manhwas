from app.models.conexao import Conexao
import sqlite3

class Cadastro:

    def __init__(self, nome, email, usuario, senha):
        self.nome = nome
        self.email = email
        self.usuario = usuario
        self.senha = senha

    @staticmethod
    def Criar_tabela():

        with Conexao() as cursor:

            cursor.execute(""" 
                CREATE TABLE IF NOT EXISTS Cadastro(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome vARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL,
                usuario VARCHAR(100) NOT NULL,
                senha VARCHAR(50) NOT NULL
                )
            """)

    def Salvar(self):

        with Conexao() as cursor:

            cursor.execute("""
                INSERT INTO Cadastro
                (nome, email, usuario, senha)
                VALUES (?, ?, ?, ?)
            """, (
                self.nome,
                self.email,
                self.usuario,
                self.senha
            ))

    @staticmethod
    def Autenticar(email, senha):

        with Conexao() as cursor:

            cursor.execute("""
                SELECT *
                FROM Cadastro
                WHERE email = ?
                AND senha = ?
            """,(email, senha))

            cadastro = cursor.fetchone()

        return cadastro