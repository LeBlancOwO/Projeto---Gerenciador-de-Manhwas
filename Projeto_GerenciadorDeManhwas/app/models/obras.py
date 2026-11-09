import sqlite3

class Obras:

    def __init__(self, titulo, autor, status):
        self.titulo = titulo
        self.autor = autor
        self.status = status

    @staticmethod
    def Conectar():
        return sqlite3.connect("banco.db")

    @staticmethod
    def Criar_tabela():

        conn = Obras.Conectar()
        cursor = conn.cursor()

        cursor.execute(""" 
            CREATE TABLE IF NOT EXISTS Obras(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo vARCHAR(150) NOT NULL,
            autor VARCHAR(100) NOT NULL,
            status text NOT NULL
            )
        """)

        conn.commit()
        conn.close()

    def Salvar(self):
        conn = Obras.Conectar()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO Obras
            (titulo, autor, status)
            VALUES (?, ?, ?)
        """, (
            self.titulo,
            self.autor,
            self.status
        ))

        conn.commit()
        conn.close()

    @staticmethod
    def Listar():

        conn = Obras.Conectar()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM Obras
        """)

        dados = cursor.fetchall()

        conn.close()

        return dados