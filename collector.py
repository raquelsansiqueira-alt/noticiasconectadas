from datetime import datetime, timezone
from urllib.parse import quote_plus, urlparse, parse_qs
from zoneinfo import ZoneInfo
import feedparser
from googlenewsdecoder import gnewsdecoder
from config import TERMOS, VEICULOS, MAX_RESULTS_PER_QUERY
from database import salvar

def _link_original(link):
    query = parse_qs(urlparse(link).query)
    if query.get("url"):
        return query["url"][0]
    if "news.google.com" in link:
        try:
            resultado = gnewsdecoder(link)
            if resultado.get("status"):
                return resultado["decoded_url"]
        except Exception:
            pass
    return link

def _data(entry):
    fuso_brasilia = ZoneInfo("America/Sao_Paulo")
    parsed = entry.get("published_parsed")
    if parsed:
        data_utc = datetime(*parsed[:6], tzinfo=timezone.utc)
        return data_utc.astimezone(fuso_brasilia).isoformat()
    return datetime.now(fuso_brasilia).isoformat()

def coletar():
    novas = 0
    erros = []
    # Uma consulta por termo, agregando todos os domínios, reduz requisições.
    sites = " OR ".join(f"site:{d}" for d in VEICULOS.values())
    for termo in TERMOS:
        consulta = quote_plus(f'"{termo}" ({sites}) when:2d')
        url = f"https://news.google.com/rss/search?q={consulta}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
        feed = feedparser.parse(url)
        if getattr(feed, "bozo", False) and not feed.entries:
            erros.append(termo)
            continue
        for entry in feed.entries[:MAX_RESULTS_PER_QUERY]:
            titulo = entry.get("title", "").strip()
            fonte = entry.get("source", {}).get("title", "")
            veiculo = next((n for n in VEICULOS if n.lower() in fonte.lower()), fonte or "Imprensa")
            item = {
                "titulo": titulo,
                "link": _link_original(entry.get("link", "")),
                "veiculo": veiculo,
                "publicado": _data(entry),
                "termos": termo,
            }
            if item["link"]:
                novas += salvar(item)
    return {"novas": novas, "erros": erros}
