# SE-RII Flight Planner — PWA

Uma só base de código (HTML/JS puro, sem build), instalável no ecrã inicial em Android e iOS, e funciona **offline** depois da primeira visita.

## Conteúdo

| Ficheiro | Função |
|---|---|
| `index.html` | A app completa (motor de cálculo incluído) |
| `airports.js` | Base de aeródromos europeus (gerada — ver abaixo) |
| `tools/build_airports.py` | Gerador de `airports.js` a partir dos CSV da OurAirports |
| `manifest.webmanifest` | Nome, ícones e modo standalone (o que a torna "instalável") |
| `sw.js` | Service worker — cache offline (stale-while-revalidate) |
| `icons/` | Ícones 192/512, maskable (Android) e apple-touch-icon (iOS) |

## Publicar (obrigatório: HTTPS)

### Opção A — GitHub Pages (grátis, permanente)
1. Cria uma conta em github.com (se ainda não tiveres).
2. **New repository** → nome p. ex. `serii-planner` → Public → Create.
3. **Add file → Upload files** → arrasta TODOS os ficheiros desta pasta
   (mantém a subpasta `icons/`) → Commit.
4. **Settings → Pages** → em "Source" escolhe `Deploy from a branch`,
   branch `main`, pasta `/ (root)` → Save.
5. Em 1–2 minutos a app fica em
   `https://<o-teu-user>.github.io/serii-planner/`.

### Opção B — Netlify / Cloudflare Pages
Arrasta a pasta inteira para o painel de deploy — sai um URL HTTPS na hora.

## Instalar

**Android (Chrome):** abre o URL → aparece o aviso "Adicionar ao ecrã principal"
(ou menu ⋮ → *Instalar app*). Fica com ícone e abre em ecrã inteiro.

**iOS/iPadOS (Safari — tem de ser o Safari):** abre o URL → botão **Partilhar** →
**Adicionar ao ecrã principal** → Adicionar. Ícone próprio, ecrã inteiro, e
com o service worker funciona offline (iOS 16.4+).

## Atualizar a app

1. Substitui o `index.html` pela versão nova (commit no GitHub / novo deploy).
2. **Importante:** em `sw.js`, muda `serii-planner-v1` para `v2` (e assim
   sucessivamente) — é isso que diz aos telemóveis para irem buscar a versão nova.
3. **Regra de versões:** a versão da app `1.N.x` (constante `APP` no `index.html`,
   mostrada na vista *About*) acompanha a cache do service worker `serii-planner-vN`
   — p. ex. `1.6.0` ↔ `serii-planner-v6`. Ao publicar, incrementam-se as duas no
   mesmo commit.
4. Nos dispositivos, basta abrir a app duas vezes: a primeira descarrega em
   segundo plano, a segunda já mostra a nova versão.

## Notas
- Tudo roda no dispositivo; não há servidor nem dados enviados a lado nenhum.
- Valores de planeamento — o AFM e a documentação oficial prevalecem sempre.
