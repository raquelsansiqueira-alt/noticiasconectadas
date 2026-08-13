import csv
import io
from flask import Flask, Response, flash, redirect, render_template, request, url_for
from collector import coletar
from config import SECRET_KEY, TERMOS, VEICULOS
from database import conectar, inicializar

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY
inicializar()

def consultar(args):
    sql = "SELECT * FROM noticias WHERE 1=1"
    params = []
    if args.get("q"):
        sql += " AND (titulo LIKE ? OR termos LIKE ?)"
        params += [f'%{args["q"]}%', f'%{args["q"]}%']
    if args.get("veiculo"):
        sql += " AND veiculo = ?"
        params.append(args["veiculo"])
    if args.get("termo"):
        sql += " AND termos LIKE ?"
        params.append(f'%{args["termo"]}%')
    if args.get("favoritos") == "1":
        sql += " AND favorito = 1"
    sql += " ORDER BY COALESCE(publicado, coletado) DESC LIMIT 500"
    with conectar() as con:
        return con.execute(sql, params).fetchall()

@app.get("/")
def index():
    noticias = consultar(request.args)
    with conectar() as con:
        total = con.execute("SELECT COUNT(*) FROM noticias").fetchone()[0]
        favoritos = con.execute("SELECT COUNT(*) FROM noticias WHERE favorito=1").fetchone()[0]
    return render_template("index.html", noticias=noticias, termos=TERMOS,
                           veiculos=VEICULOS, total=total, favoritos=favoritos)

@app.post("/atualizar")
def atualizar():
    resultado = coletar()
    flash(f'{resultado["novas"]} notícia(s) nova(s) encontrada(s).')
    if resultado["erros"]:
        flash("Algumas consultas não responderam; tente novamente depois.", "warning")
    return redirect(url_for("index"))

@app.post("/favorito/<int:noticia_id>")
def favorito(noticia_id):
    with conectar() as con:
        con.execute("UPDATE noticias SET favorito = 1-favorito WHERE id=?", (noticia_id,))
    return redirect(request.referrer or url_for("index"))

@app.get("/exportar.csv")
def exportar_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Título", "Veículo", "Publicado", "Termos", "Link"])
    for n in consultar(request.args):
        writer.writerow([n["titulo"], n["veiculo"], n["publicado"], n["termos"], n["link"]])
    return Response("\ufeff" + output.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=clipping-stf.csv"})

@app.get("/saude")
def saude():
    return {"status": "ok"}

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

