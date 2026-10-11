# giuliano.curtinaz.com.br

Site pessoal (portfólio) de Giuliano Curtinaz. Ele é publicado no GitHub Pages pelo próprio GitHub a cada `push` na branch `main`.

## Onde editar

| O que | Arquivo |
|---|---|
| Texto de qualquer página | `conteudo/*.md` (cada arquivo vira uma página com o mesmo nome) |
| Linha do tempo da página inicial | `dados/trajetoria.json` |
| Menu do topo e endereços antigos redirecionados | `build.py` (listas `NAV` e `REDIRECIONAR`) |
| Visual (cores, fontes, espaçamentos) | `assets/css/estilo.css` |
| Cabeçalho e rodapé de todas as páginas | `modelos/base.html` |
| Imagens e arquivos para download | `assets/img/` e `assets/arquivos/` |

O topo de cada `.md` tem `titulo:` (aparece na aba do navegador) e `descricao:` (aparece no Google e quando alguém compartilha o link).

## Ver no seu computador antes de publicar

```powershell
pip install markdown
python build.py --servir
```

Abre `http://localhost:8000` no navegador. A pasta `_site/` é gerada automaticamente e não vai para o GitHub.

## Publicar

```powershell
git add -A
git commit -m "Atualiza o site"
git push
```

Em 1 a 2 minutos o GitHub gera e publica o site (aba **Actions** do repositório).

## Privacidade

- O e-mail não aparece no código da página: ele é montado só quando o visitante clica em "Mostrar e-mail".
- As fontes ficam no próprio site, então o visitante não faz nenhuma chamada ao Google. O site não usa cookies nem rastreadores.
- Nos certificados, as assinaturas e os dados pessoais (RG, data de nascimento) estão cobertos. As imagens originais, sem as tarjas, **não** fazem parte deste repositório.
- A página `jobs/infonotas` contém a Política de Privacidade do app Infonotas e deve continuar neste endereço: é o link que costuma ser informado na Google Play como política do app.
