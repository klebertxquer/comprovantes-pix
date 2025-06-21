import sqlite3

def criar_banco():
    conn = sqlite3.connect('comprovantes.db')
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
    conn.close()

def salvar_no_banco(dados):
    conn = sqlite3.connect('comprovantes.db')
    c = conn.cursor()
    c.execute("""
        INSERT INTO comprovantes (data, valor, pagador, destinatario,
        instituicao_origem, instituicao_destino, id_transacao)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        dados["data"], dados["valor"], dados["pagador"],
        dados["destinatario"], dados["instituicao_origem"],
        dados["instituicao_destino"], dados["id_transacao"]
    ))
    conn.commit()
    conn.close()

def obter_todos():
    conn = sqlite3.connect('comprovantes.db')
    c = conn.cursor()
    c.execute("SELECT * FROM comprovantes")
    rows = c.fetchall()
    conn.close()
    return rows
