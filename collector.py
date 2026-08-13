from datetime import datetime, timezone
from urllib.parse import quote_plus, urlparse, parse_qs
from zoneinfo import ZoneInfo

import feedparser
from googlenewsdecoder import gnewsdecoder

from config import TERMOS, VEICULOS, MAX_RESULTS_PER_QUERY
from database import salvar


def _link_original(link):
    """
    Converte o endereço intermediário do Google Notícias
    para o endereço original do veículo.
    """
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
    """
    Converte a data publicada para o horário oficial de Brasília.
    """
    fuso_brasilia = ZoneInfo("America/Sao_Paulo")
    data_publicada = entry.get("published_parsed")

    if data_publicada:
        data_utc = datetime(
            *data_publicada[:6],
            tzinfo=timezone.utc
        )

        return data_utc.astimezone(fuso_brasilia).isoformat()

    return datetime.now(fuso_brasilia).isoformat()


def coletar():
    novas = 0
    erros = []

    # Reúne os domínios dos veículos selecionados em uma única pesquisa.
    sites = " OR ".join(
        f"site:{dominio}"
        for dominio in VEICULOS.values()
    )

    for termo in TERMOS:
        consulta = quote_plus(
            f'"{termo}" ({sites}) when:2d'
        )

        url = (
            "https://news.google.com/rss/search"
            f"?q={consulta}"
            "&hl=pt-BR"
            "&gl=BR"
            "&ceid=BR:pt-419"
        )

        feed = feedparser.parse(url)

        if getattr(feed, "bozo", False) and not feed.entries:
            erros.append(termo)
            continue

        for entry in feed.entries[:MAX_RESULTS_PER_QUERY]:
            titulo = entry.get("title", "").strip()
            fonte = entry.get("source", {}).get("title", "")

            veiculo = next(
                (
                    nome
                    for nome in VEICULOS
                    if nome.lower() in fonte.lower()
                ),
                fonte or "Imprensa"
            )

            link_google = entry.get("link", "")

            noticia = {
                "titulo": titulo,
                "link": _link_original(link_google),
                "veiculo": veiculo,
                "publicado": _data(entry),
                "termos": termo,
            }

            if noticia["link"]:
                novas += salvar(noticia)

    return {
        "novas": novas,
        "erros": erros,
    }
