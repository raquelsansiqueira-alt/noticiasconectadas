from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "instance" / "noticias.db"
SECRET_KEY = "troque-esta-chave-em-producao"
MAX_RESULTS_PER_QUERY = 12

VEICULOS = {
    "G1": "g1.globo.com",
    "Veja": "veja.abril.com.br",
    "Metrópoles": "metropoles.com",
    "O Globo": "oglobo.globo.com",
    "Poder360": "poder360.com.br",
    "Estadão": "estadao.com.br",
    "Valor": "valor.globo.com",
    "Folha": "folha.uol.com.br",
    "Revista Oeste": "revistaoeste.com",
    "CNN Brasil": "cnnbrasil.com.br",
    "UOL": "uol.com.br",
    "DW Brasil": "dw.com",
    "R7": "r7.com",
    "Agência Brasil": "agenciabrasil.ebc.com.br",
    "O Tempo": "otempo.com.br",
    "JOTA": "jota.info",
}

INTERVALO_ATUALIZACAO_MINUTOS = 15

TERMOS = [
    "STF", "Supremo Tribunal Federal", "CNJ",
    "Edson Fachin", "Cármen Lúcia", "Alexandre de Moraes",
    "Nunes Marques", "Luiz Fux", "André Mendonça",
    "Cristiano Zanin", "Gilmar Mendes", "Dias Toffoli", "Flávio Dino",
]
