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
        existente = con.execute(
            "SELECT id, termos FROM noticias WHERE link=?", (noticia["link"],)
        ).fetchone()
        if existente:
            termos = [t.strip() for t in existente["termos"].split(",") if t.strip()]
            if noticia["termos"] not in termos:
                termos.append(noticia["termos"])
                con.execute("UPDATE noticias SET termos=? WHERE id=?", (", ".join(termos), existente["id"]))
            return 0
        cur = con.execute(
            "INSERT OR IGNORE INTO noticias(titulo, link, veiculo, publicado, termos) VALUES(?,?,?,?,?)",
            (noticia["titulo"], noticia["link"], noticia["veiculo"], noticia["publicado"], noticia["termos"]),
        )
        return cur.rowcount

def metricas_dashboard():
    with conectar() as con:
        total_hoje = con.execute(
            "SELECT COUNT(*) FROM noticias WHERE substr(publicado,1,10)=date('now','localtime')"
        ).fetchone()[0]
        ultimas_24h = con.execute(
            "SELECT COUNT(*) FROM noticias WHERE datetime(publicado) >= datetime('now','-24 hours')"
        ).fetchone()[0]
        por_veiculo = con.execute(
            "SELECT veiculo, COUNT(*) total FROM noticias GROUP BY veiculo ORDER BY total DESC, veiculo"
        ).fetchall()
        por_dia = con.execute(
            """WITH RECURSIVE dias(data) AS (
                 SELECT date('now','localtime','-6 days')
                 UNION ALL SELECT date(data,'+1 day') FROM dias WHERE data < date('now','localtime')
               )
               SELECT dias.data, COUNT(n.id) total
               FROM dias LEFT JOIN noticias n ON substr(n.publicado,1,10)=dias.data
               GROUP BY dias.data ORDER BY dias.data"""
        ).fetchall()
        todas_tags = con.execute("SELECT termos FROM noticias").fetchall()
    contagem = {}
    for linha in todas_tags:
        for termo in linha["termos"].split(","):
            termo = termo.strip()
            if termo:
                contagem[termo] = contagem.get(termo, 0) + 1
    assuntos = sorted(contagem.items(), key=lambda item: (-item[1], item[0]))[:8]
    graficos = {
        "veiculos_labels": [item["veiculo"] for item in por_veiculo],
        "veiculos_valores": [item["total"] for item in por_veiculo],
        "assuntos_labels": [item[0] for item in assuntos],
        "assuntos_valores": [item[1] for item in assuntos],
        "dias_labels": [item["data"] for item in por_dia],
        "dias_valores": [item["total"] for item in por_dia],
    }
    return {"hoje": total_hoje, "ultimas_24h": ultimas_24h,
            "por_veiculo": por_veiculo, "assuntos": assuntos,
            "por_dia": por_dia, "graficos": graficos}
