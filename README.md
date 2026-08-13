# STF News Monitor

Painel em Python/Flask para monitorar notícias sobre o STF, o CNJ e os ministros da Corte nos veículos selecionados. A coleta usa os resultados públicos do Google Notícias em RSS e armazena somente título, link, veículo, data e termos relacionados.

## Recursos

- Monitoramento de 10 veículos: G1, Veja, Metrópoles, O Globo, Poder360, Estadão, Valor, Folha, Revista Oeste e CNN Brasil.
- Busca por STF, CNJ e os 11 ministros.
- Banco SQLite e deduplicação por link.
- Pesquisa e filtros por assunto, veículo e favoritos.
- Botões para abrir, copiar e enviar título + link ao WhatsApp.
- Exportação da seleção em CSV.
- Layout responsivo e testes no GitHub Actions.

## Como executar no Windows

1. Instale o Python 3.11 ou mais recente.
2. Extraia este ZIP e abra o Prompt de Comando dentro da pasta.
3. Execute:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

4. Abra `http://127.0.0.1:5000` no navegador.
5. Clique em **Buscar novas notícias**.

No macOS/Linux, ative o ambiente com `source venv/bin/activate`.

## Subir no GitHub

Crie um repositório vazio, abra esta pasta no terminal e execute:

```bash
git init
git add .
git commit -m "Primeira versão do STF News Monitor"
git branch -M main
git remote add origin URL_DO_SEU_REPOSITORIO
git push -u origin main
```

## Observações importantes

- O botão de atualização depende da disponibilidade do RSS público do Google Notícias.
- Alguns links podem levar a páginas com assinatura; o sistema não contorna paywalls.
- A aplicação não reproduz o texto integral das matérias.
- Para uso institucional contínuo, publique em um servidor Python. GitHub Pages sozinho não executa Flask.
- Antes de publicar em produção, altere `SECRET_KEY` em `config.py`.

## Testes

```bash
pytest -q
```

## Docker (opcional)

```bash
docker build -t stf-news-monitor .
docker run --rm -p 5000:5000 stf-news-monitor
```
