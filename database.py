import sqlite3

DB_PATH = "comprovantes_pix.db"

def criar_banco():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS comprovantes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT,
                valor TEXT,
                pagador TEXT,
                destinatario TEXT,
                instituicao_origem TEXT,
                instituicao_destino TEXT,
                id_transacao TEXT
            )
        """)
        conn.commit()

def salvar_no_banco(dados):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("""
            INSERT INTO comprovantes (
                data, valor, pagador, destinatario,
                instituicao_origem, instituicao_destino, id_transacao
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            dados.get("data"),
            dados.get("valor"),
            dados.get("pagador"),
            dados.get("destinatario"),
            dados.get("instituicao_origem"),
            dados.get("instituicao_destino"),
            dados.get("id_transacao")
        ))
        conn.commit()

def obter_todos():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM comprovantes")
        return c.fetchall()

