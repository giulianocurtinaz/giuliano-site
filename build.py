#!/usr/bin/env python3
"""Gera o site estático de giuliano.curtinaz.com.br.

Uso:
    python build.py            -> gera a pasta _site/
    python build.py --servir   -> gera e abre um servidor em http://localhost:8000

Conteúdo: cada arquivo em conteudo/ vira uma página.
  conteudo/certificados.md        -> _site/certificados.html
  conteudo/jobs/infonotas.md      -> _site/jobs/infonotas.html
O topo de cada .md tem um bloco "---" com título e descrição.
A linha do tempo da página inicial fica em dados/trajetoria.json.
"""
import datetime
import html
import json
import re
import shutil
import sys
import unicodedata
from pathlib import Path

import markdown

RAIZ = Path(__file__).parent
CONTEUDO = RAIZ / "conteudo"
SAIDA = RAIZ / "_site"
URL = "https://giuliano.curtinaz.com.br"

NAV = [
    ("index.html", "Início"),
    ("jobs.html", "Trajetória"),
    ("competencias.html", "Competências"),
    ("tccs.html", "Formação"),
    ("certificados.html", "Certificados"),
]

# Endereços antigos do Google Sites que precisam continuar funcionando
REDIRECIONAR = {
    "about-me.html": "index.html",
    "competências.html": "competencias.html",
    "competências/amo-fazer.html": "competencias.html#amo-fazer",
    "competências/como-trabalho.html": "competencias.html#como-trabalho",
    "competências/know-how.html": "competencias.html#know-how",
    "competências/apoio-à-gestão.html": "competencias.html#apoio-a-gestao",
    "competências/sistemas.html": "competencias.html#sistemas",
    "competencias/amo-fazer.html": "competencias.html#amo-fazer",
    "competencias/como-trabalho.html": "competencias.html#como-trabalho",
    "competencias/know-how.html": "competencias.html#know-how",
    "competencias/apoio-a-gestao.html": "competencias.html#apoio-a-gestao",
    "competencias/sistemas.html": "competencias.html#sistemas",
    "jobs/histórico.html": "jobs.html#trajetoria",
    "jobs/historico.html": "jobs.html#trajetoria",
    "jobs/governança.html": "jobs/governanca.html",
    "tccs/análise-de-balanço.html": "tccs/analise-de-balanco.html",
    "tccs/graduação-ulbra-2011.html": "tccs/graduacao-ulbra-2011.html",
}


def ler_md(caminho: Path):
    texto = caminho.read_text(encoding="utf-8")
    meta = {}
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", texto, re.S)
    if m:
        for linha in m.group(1).splitlines():
            if ":" in linha:
                k, v = linha.split(":", 1)
                meta[k.strip()] = v.strip()
        texto = texto[m.end():]
    return meta, texto


def para_html(texto: str) -> str:
    return markdown.markdown(
        texto,
        extensions=["attr_list", "md_in_html", "tables", "sane_lists", "smarty"],
        extension_configs={"smarty": {"smart_quotes": False}},
        output_format="html5",
    )


def relativizar(conteudo_html: str, prefixo: str) -> str:
    """Troca links "/pagina.html" por caminhos relativos (funciona abrindo o arquivo direto)."""
    def troca(m):
        attr, alvo = m.group(1), m.group(2)
        if alvo.startswith("//"):
            return m.group(0)
        alvo = alvo.lstrip("/")
        if alvo == "" or alvo.startswith("#"):
            alvo = "index.html" + alvo
        return f'{attr}="{prefixo}{alvo}"'
    return re.sub(r'(href|src|poster|data-grande)="(/[^"]*)"', troca, conteudo_html)


def nav_html(atual: str) -> str:
    itens = []
    secao = atual.split("/")[0]
    for alvo, nome in NAV:
        ativo = alvo == atual or (alvo.removesuffix(".html") == secao and "/" in atual)
        aria = ' aria-current="page"' if ativo else ""
        itens.append(f'<li><a href="/{alvo}"{aria}>{nome}</a></li>')
    return "\n".join(itens)


def trajetoria_html() -> str:
    dados = json.loads((RAIZ / "dados" / "trajetoria.json").read_text(encoding="utf-8"))
    paradas = []
    for p in dados:
        paradas.append(
            '<li class="parada">'
            f'<span class="ano">{html.escape(p["ano"])}</span>'
            f'<span class="lugar">{html.escape(p["onde"])}</span>'
            f'<span class="feito">{html.escape(p["o_que"])}</span>'
            "</li>"
        )
    return '<ol class="rota" aria-label="Trajetória profissional e acadêmica">' + "".join(paradas) + "</ol>"


def montar(pagina_rel: str, meta: dict, corpo: str, modelo: str) -> str:
    profundidade = pagina_rel.count("/")
    prefixo = "../" * profundidade
    if pagina_rel == "404.html":  # servida em qualquer endereço: precisa de caminhos absolutos
        prefixo = "/"
    titulo = meta.get("titulo", "Giuliano Curtinaz")
    titulo_aba = "Giuliano Curtinaz" if pagina_rel == "index.html" else f"{titulo} | Giuliano Curtinaz"
    descricao = meta.get("descricao", "Ciência de dados, controladoria e sistemas para logística.")
    endereco = URL + "/" + ("" if pagina_rel == "index.html" else pagina_rel.removesuffix(".html"))
    pagina = (
        modelo.replace("{{titulo_aba}}", html.escape(titulo_aba))
        .replace("{{descricao}}", html.escape(descricao))
        .replace("{{url}}", endereco)
        .replace("{{nav}}", nav_html(pagina_rel))
        .replace("{{classe}}", meta.get("classe", "pagina"))
        .replace("{{ano}}", str(datetime.date.today().year))
        .replace("{{conteudo}}", corpo)
    )
    return relativizar(pagina, prefixo)


def redirecionamento(destino: str, prefixo: str) -> str:
    alvo = prefixo + destino
    return (
        '<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">'
        f'<meta http-equiv="refresh" content="0; url={alvo}">'
        f'<link rel="canonical" href="{URL}/{destino}"><meta name="robots" content="noindex">'
        f'<title>Página movida</title></head><body><p>Esta página mudou de endereço: '
        f'<a href="{alvo}">abrir a nova página</a>.</p></body></html>'
    )


def gerar():
    if SAIDA.exists():
        shutil.rmtree(SAIDA)
    shutil.copytree(RAIZ / "assets", SAIDA / "assets")
    for extra in ["CNAME", "robots.txt"]:
        if (RAIZ / extra).exists():
            shutil.copy(RAIZ / extra, SAIDA / extra)

    modelo = (RAIZ / "modelos" / "base.html").read_text(encoding="utf-8")
    paginas = []
    for md in sorted(CONTEUDO.rglob("*.md")):
        rel = md.relative_to(CONTEUDO).with_suffix(".html").as_posix()
        meta, texto = ler_md(md)
        corpo = para_html(texto)
        corpo = corpo.replace("<p>{{trajetoria}}</p>", trajetoria_html())
        destino = SAIDA / rel
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(montar(rel, meta, corpo, modelo), encoding="utf-8")
        if meta.get("sitemap", "sim") != "nao":
            paginas.append(rel)

    for antigo, novo in REDIRECIONAR.items():
        antigo = unicodedata.normalize("NFC", antigo)
        destino = SAIDA / antigo
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(redirecionamento(novo, "../" * antigo.count("/")), encoding="utf-8")

    hoje = datetime.date.today().isoformat()
    urls = "".join(
        f"<url><loc>{URL}/{'' if p == 'index.html' else p.removesuffix('.html')}</loc><lastmod>{hoje}</lastmod></url>"
        for p in paginas if p != "404.html"
    )
    (SAIDA / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>'
        f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>',
        encoding="utf-8",
    )
    print(f"Pronto: {len(paginas)} páginas e {len(REDIRECIONAR)} redirecionamentos em {SAIDA}")


if __name__ == "__main__":
    gerar()
    if "--servir" in sys.argv:
        import functools
        import http.server
        import webbrowser
        porta = 8000
        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(SAIDA))
        print(f"Abrindo http://localhost:{porta}  (Ctrl+C para parar)")
        webbrowser.open(f"http://localhost:{porta}")
        http.server.ThreadingHTTPServer(("localhost", porta), handler).serve_forever()
