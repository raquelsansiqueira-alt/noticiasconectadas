import tempfile
import config
import database

def test_saude(monkeypatch):
    with tempfile.TemporaryDirectory() as pasta:
        monkeypatch.setattr(database, "DATABASE", __import__("pathlib").Path(pasta) / "teste.db")
        database.inicializar()
        from app import app
        cliente = app.test_client()
        resposta = cliente.get("/saude")
        assert resposta.status_code == 200
        assert resposta.json == {"status": "ok"}

