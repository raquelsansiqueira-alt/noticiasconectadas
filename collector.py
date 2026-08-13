from datetime import datetime, timezone
from urllib.parse import quote_plus, urlparse, parse_qs
import feedparser
from config import TERMOS, VEICULOS, MAX_RESULTS_PER_QUERY
from database import salvar

def _link_original(link):
    query = parse_qs(urlparse(link).query)
    return query.get("url", [link])[0]

def _data(entry):
    parsed = entry.get("published_parsed")
    if parsed:
        return datetime(*parsed[:6], tzinfo=timezone.utc).isoformat()
    return datetime.now(timezone.utc).isoformat()

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

