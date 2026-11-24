from app.db import DatabaseConnection

# Status permitidos para as obras
STATUS_VALIDOS = ("Em andamento", "Concluído", "Abandonada", "Hiatus")

# Lista abrangente e padronizada de tags para manhwas, mangás e webtoons
TAGS_PADRAO = (
    "Ação",
    "Artes Marciais",
    "Aventura",
    "Comédia",
    "Cultivo",
    "Drama",
    "Escolar",
    "Esportes",
    "Fantasia",
    "Fantasia Sombria",
    "Histórico",
    "Horror",
    "Isekai",
    "Josei",
    "Magia",
    "Mecha",
    "Mistério",
    "Monstros",
    "Murim",
    "Psicológico",
    "Reencarnação",
    "Regressão",
    "Romance",
    "Sci-Fi",
    "Seinen",
    "Shoujo",
    "Shounen",
    "Sistema",
    "Slice of Life",
    "Sobrenatural",
    "Superpoderes",
    "Suspense",
    "Terror",
    "Torre / Masmorra",
    "Tragédia",
    "Yaoi",
    "Yuri",
)


class Obras:
    """Model responsável pelo gerenciamento das obras (manhwas) e moderação."""

    def __init__(self, titulo, sinopse, capa, status, usuario_id, tags=""):
        self.titulo = titulo
        self.sinopse = sinopse
        self.capa = capa
        self.status = status
        self.usuario_id = usuario_id
        self.tags = tags

    @staticmethod
    def Criar_tabela():
        """Cria a tabela Obras e garante colunas adicionadas em atualizações."""
        with DatabaseConnection() as db:
            db.cursor.execute("""
                CREATE TABLE IF NOT EXISTS Obras(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    titulo VARCHAR(150) NOT NULL UNIQUE,
                    sinopse TEXT NOT NULL,
                    capa TEXT,
                    status TEXT NOT NULL,
                    tags TEXT,
                    aprovada INTEGER DEFAULT 0,
                    justificativa TEXT,
                    usuario_id INTEGER NOT NULL,
                    FOREIGN KEY (usuario_id)
                    REFERENCES Usuarios(id)
                    ON DELETE CASCADE
                )
            """)
            db.cursor.execute("PRAGMA table_info(Obras)")
            colunas = [col["name"] for col in db.cursor.fetchall()]
            if "justificativa" not in colunas:
                db.cursor.execute("ALTER TABLE Obras ADD COLUMN justificativa TEXT")
            if "tags" not in colunas:
                db.cursor.execute("ALTER TABLE Obras ADD COLUMN tags TEXT")

    def Salvar(self):
        """Cadastra uma nova obra no banco (inicia com aprovada = 0 para análise)."""
        with DatabaseConnection() as db:
            db.cursor.execute("""
                INSERT INTO Obras
                (titulo, sinopse, capa, status, tags, usuario_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                self.titulo,
                self.sinopse,
                self.capa,
                self.status,
                self.tags,
                self.usuario_id
            ))

    @staticmethod
    def Listar(busca=None, status=None, tags_incluir=None, tags_excluir=None):
        """Lista obras aprovadas filtrando por título, status, tags desejadas e tags excluídas."""
        with DatabaseConnection() as db:
            query = "SELECT * FROM Obras WHERE aprovada = 1"
            params = []

            if busca:
                query += " AND titulo LIKE ?"
                params.append(f"%{busca}%")
            if status:
                query += " AND status = ?"
                params.append(status)
            for tag in (tags_incluir or []):
                query += " AND tags LIKE ?"
                params.append(f"%{tag}%")
            for tag in (tags_excluir or []):
                query += " AND (tags IS NULL OR tags NOT LIKE ?)"
                params.append(f"%{tag}%")

            query += " ORDER BY id DESC"
            db.cursor.execute(query, tuple(params))
            return db.cursor.fetchall()

    @staticmethod
    def ListarLidasPorUsuario(usuario_id, busca=None, status=None, tags_incluir=None, tags_excluir=None):
        """Lista apenas as obras lidas pelo usuário aplicando filtros de busca, status e tags."""
        with DatabaseConnection() as db:
            query = """
                SELECT DISTINCT o.*
                FROM Obras o
                INNER JOIN Capitulos c ON c.obra_id = o.id
                INNER JOIN Leituras l ON l.capitulo_id = c.id
                WHERE l.usuario_id = ?
            """
            params = [usuario_id]

            if busca:
                query += " AND o.titulo LIKE ?"
                params.append(f"%{busca}%")
            if status:
                query += " AND o.status = ?"
                params.append(status)
            for tag in (tags_incluir or []):
                query += " AND o.tags LIKE ?"
                params.append(f"%{tag}%")
            for tag in (tags_excluir or []):
                query += " AND (o.tags IS NULL OR o.tags NOT LIKE ?)"
                params.append(f"%{tag}%")

            query += " ORDER BY o.id DESC"
            db.cursor.execute(query, tuple(params))
            return db.cursor.fetchall()

    @staticmethod
    def ListarPendentes():
        """Lista todas as obras aguardando aprovação do administrador."""
        with DatabaseConnection() as db:
            db.cursor.execute("""
                SELECT *
                FROM Obras
                WHERE aprovada = 0
                ORDER BY id DESC
            """)
            return db.cursor.fetchall()

    @staticmethod
    def BuscarPorId(id_obra):
        """Busca uma obra pelo ID trazendo também o username do autor."""
        with DatabaseConnection() as db:
            db.cursor.execute("""
                SELECT o.*, u.username AS autor_username
                FROM Obras o
                INNER JOIN Usuarios u ON u.id = o.usuario_id
                WHERE o.id = ?
            """, (id_obra,))
            return db.cursor.fetchone()

    @staticmethod
    def BuscarPorIdEUsuario(id_obra, usuario_id):
        """Busca uma obra garantindo que ela pertença ao usuário informado."""
        with DatabaseConnection() as db:
            db.cursor.execute(
                "SELECT * FROM Obras WHERE id = ? AND usuario_id = ?",
                (id_obra, usuario_id),
            )
            return db.cursor.fetchone()

    @staticmethod
    def BuscarPorTitulo(titulo, excluir_id=None):
        """Verifica se já existe outra obra com o mesmo título."""
        with DatabaseConnection() as db:
            if excluir_id is not None:
                db.cursor.execute(
                    "SELECT id FROM Obras WHERE titulo = ? AND id != ?",
                    (titulo, excluir_id),
                )
            else:
                db.cursor.execute(
                    "SELECT id FROM Obras WHERE titulo = ?",
                    (titulo,),
                )
            return db.cursor.fetchone()

    @staticmethod
    def Aprovar(id_obra):
        """Marca a obra como aprovada (aprovada = 1) e limpa eventual justificativa."""
        with DatabaseConnection() as db:
            db.cursor.execute(
                "UPDATE Obras SET aprovada = 1, justificativa = NULL WHERE id = ?",
                (id_obra,),
            )

    @staticmethod
    def Desaprovar(id_obra, justificativa):
        """Marca a obra como rejeitada (aprovada = -1) salvando a justificativa do admin."""
        with DatabaseConnection() as db:
            db.cursor.execute(
                "UPDATE Obras SET aprovada = -1, justificativa = ? WHERE id = ?",
                (justificativa, id_obra),
            )

    @staticmethod
    def AtualizarStatus(id_obra, usuario_id, status):
        """Atualiza o status da obra (usado ao publicar capítulos) validando o dono."""
        with DatabaseConnection() as db:
            db.cursor.execute(
                "UPDATE Obras SET status = ? WHERE id = ? AND usuario_id = ?",
                (status, id_obra, usuario_id),
            )

    @staticmethod
    def Atualizar(id_obra, usuario_id, titulo, sinopse, status, tags, capa=None):
        """Atualiza os dados da obra validando o dono e reenvia para análise."""
        with DatabaseConnection() as db:
            if capa:
                db.cursor.execute("""
                    UPDATE Obras
                    SET titulo = ?, sinopse = ?, status = ?, tags = ?, capa = ?, aprovada = 0, justificativa = NULL
                    WHERE id = ? AND usuario_id = ?
                """, (titulo, sinopse, status, tags, capa, id_obra, usuario_id))
            else:
                db.cursor.execute("""
                    UPDATE Obras
                    SET titulo = ?, sinopse = ?, status = ?, tags = ?, aprovada = 0, justificativa = NULL
                    WHERE id = ? AND usuario_id = ?
                """, (titulo, sinopse, status, tags, id_obra, usuario_id))

    @staticmethod
    def Excluir(id_obra, usuario_id):
        """Exclui a obra validando se ela pertence ao usuário autenticado."""
        with DatabaseConnection() as db:
            db.cursor.execute(
                "DELETE FROM Obras WHERE id = ? AND usuario_id = ?",
                (id_obra, usuario_id),
            )
            return db.cursor.rowcount

    @staticmethod
    def MinhasObras(usuario_id):
        """Lista todas as obras criadas pelo usuário autenticado."""
        with DatabaseConnection() as db:
            db.cursor.execute(
                "SELECT * FROM Obras WHERE usuario_id = ? ORDER BY id DESC",
                (usuario_id,),
            )
            return db.cursor.fetchall()
