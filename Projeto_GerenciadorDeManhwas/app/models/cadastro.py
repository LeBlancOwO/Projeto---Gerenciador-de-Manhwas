import sqlite3

class Cadastro:

    def __init__(self, nome, email, usuario, senha):
        self.nome = nome
        self.email = email
        self.usuario = usuario
        self.senha = senha

    @staticmethod
    def Conectar():
        return sqlite3.connect("banco.db")

    @staticmethod
    def Criar_tabela():
        conn = Cadastro.Conectar()
        cursor = conn.cursor()

        cursor.execute(""" 
            CREATE TABLE IF NOT EXISTS Cadastro(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome vARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL,
            usuario VARCHAR(100) NOT NULL,
            senha VARCHAR(50) NOT NULL
            )
        """)

        conn.commit()
        conn.close()

    def Salvar(self):
        conn = Cadastro.Conectar()
        cursor = conn.cursor()

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

        conn.commit()
        conn.close()

    @staticmethod
    def Autenticar(email, senha):

        conn = Cadastro.Conectar()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM Cadastro
            WHERE email = ?
            AND senha = ?
        """,(email, senha))

        cadastro = cursor.fetchone()

        conn.close()

        return cadastro