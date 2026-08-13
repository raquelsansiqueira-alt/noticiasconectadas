import sqlite3
from contextlib import contextmanager
from config import DATABASE

SCHEMA = """
CREATE TABLE IF NOT EXISTS noticias (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  titulo TEXT NOT NULL,
  link TEXT NOT NULL UNIQUE,
  veiculo TEXT NOT NULL,
  publicado TEXT,
  coletado TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  termos TEXT NOT NULL DEFAULT '',
  favorito INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_noticias_publicado ON noticias(publicado);
CREATE INDEX IF NOT EXISTS idx_noticias_veiculo ON noticias(veiculo);
"""

@contextmanager
def conectar():
    DATABASE.parent.mkdir(exist_ok=True)
    con = sqlite3.connect(DATABASE)
    con.row_factory = sqlite3.Row
    try:
        yield con
        con.commit()
    finally:
        con.close()

def inicializar():
    with conectar() as con:
        con.executescript(SCHEMA)

def salvar(noticia):
    with conectar() as con:
        cur = con.execute(
            "INSERT OR IGNORE INTO noticias(titulo, link, veiculo, publicado, termos) VALUES(?,?,?,?,?)",
            (noticia["titulo"], noticia["link"], noticia["veiculo"], noticia["publicado"], noticia["termos"]),
        )
        return cur.rowcount

