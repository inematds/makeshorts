---
name: makeshorts
description: >-
  Fábrica de SHORTS ponta a ponta (Reels/TikTok/YouTube Shorts/Kwai): tema → 3 roteiros com gancho +
  gancho secundário → mídia (gravação humana, voz local ou avatar HeyGen) → b-roll real do site/GitHub →
  edição vertical 1080x1920 → portão de QA → legenda/hashtags → agendamento no Metricool → funil
  "comente PALAVRA" → DM. Gatilho: "/makeshorts", "faz um short sobre X", "fábrica de shorts",
  "lote de shorts da semana", "publica esse short". Orquestra skills existentes, não substitui.
---

# makeshorts — fábrica de shorts

Você orquestra a produção de um short vertical do tema até o post agendado. **Não reinvente etapas
que outras skills já fazem** — chame-as pelo nome. O que é próprio desta skill: a fórmula de roteiro
(`references/roteiro.md`), a especificação visual (`references/spec-visual.md`), o portão de QA
(`scripts/qa_short.py`) e as regras de publicação (`references/publicar.md`).

## Modos

Descubra o modo pelo pedido; se não der, pergunte em texto livre (nunca menu).

| Modo | Entrada | Caminho |
|---|---|---|
| **1 · Roteiro** | tema, link ou transcrição | só gera os 3 roteiros (`references/roteiro.md`) |
| **2 · Humano** | clipe gravado (vertical ou não) | edição → QA → publicar |
| **3 · IA (sem gravar)** | tema/link | roteiro → voz local **ou** avatar → b-roll → edição → QA → publicar |
| **4 · Publicar** | MP4 pronto | QA → legenda → Metricool |
| **5 · Lote** | "N shorts da semana" | modo 3 em série, um por dia, agendados |

## Pipeline (modo 3 completo)

1. **Roteiro** — siga `references/roteiro.md`: 3 versões, ~75 palavras (≈30 s), gancho em 3 s, gancho
   secundário de curiosidade, entrega em 3 passos, CTA "comente PALAVRA". Fatos só de fonte oficial
   (site/GitHub do tema) — abra e confira antes de escrever. Para o tom INEMA, a skill
   **`roteirista-inema`** pode refinar a versão escolhida. **Mostre as 3 e deixe o usuário escolher.**
2. **Voz / rosto** — três opções, da mais barata para a mais cara:
   - **Gravação humana** (20–30 s no celular): o usuário grava, você edita (modo 2).
   - **Voz sintética:** `python3 $MS/scripts/voz.py --arquivo roteiro.txt --out <ws>/voz/narracao.wav`
     — o backend vem de `MS_VOZ` (`inemavox` local/GPU, `edge` grátis sem GPU, `openai`, `elevenlabs`).
     Voz padrão local: `rachel`; para a voz do Nei, `INEMAVOX_REF=.../nei2.wav`.
   - **Avatar HeyGen (gasta crédito):** skill **`avatar-heygen-nei`** (escolha de look) sobre
     **`heygen-cli`**. **Confirme o custo com o usuário antes de renderizar.**
   Legendas precisam de transcrição com tempo por palavra:
   `python3 $MS/scripts/transcreve.py --in <ws>/voz/narracao.wav --outdir <ws>/transcricao`
   (backend em `MS_TRANSCRICAO`: `inemavox` local, `groq`, `openai`).
3. **B-roll real** — enquanto a voz/avatar renderiza: capture o site e o GitHub do tema com rolagem
   suave (skills **`agent-browser`** / **`website-intelligence`**), demos/GIFs oficiais. Mostrar a
   ferramenta funcionando vence card de texto. Imagem gerada só se faltar material real
   (flux2-klein local via `inemaimg`).
4. **Edição** — vertical 1080x1920 seguindo `references/spec-visual.md`. Motores, em ordem:
   - avatar/fala 16:9 → **`reel-edita-inema`** (reel empilhado INEMA);
   - clipe vertical cru → **`reel-edita-inematds`** (corta silêncio/repetição, PiP, b-roll, SFX);
   - composição livre → **`hyperframes`** + **`general-video`**;
   - legendas palavra-a-palavra → **`embedded-captions`**.
   SFX e música: inemavox (`sfx_v1.py --query whoosh --outdir <ws>/sfx`). **Shorts didáticos não levam
   música de fundo** — só SFX curtos.
5. **Portão de QA (obrigatório)** —
   `python3 $MS/.claude/skills/makeshorts/scripts/qa_short.py final.mp4 --caption legenda.txt`
   Exit 1 = não publica: corrija e rode de novo. Depois olhe 3 frames (0 s, meio, fim) para checar
   texto sobre rosto e legenda legível — o script não vê isso.
6. **Publicar** — `references/publicar.md`: legenda, ≤ 5 hashtags específicas, rótulo de IA quando
   houver avatar/voz sintética, agendamento via Metricool MCP.
7. **Funil** — o CTA "comente PALAVRA" só converte se a automação de DM estiver ligada:
   `references/funil-dm.md`.

## Onde está o quê (`$MS`)

`$MS` = raiz do repo makeshorts. Se a skill foi instalada por symlink:
`MS=$(readlink -f ~/.claude/skills/makeshorts)/../../..`. Lá estão `scripts/` (voz, transcrição),
`config/makeshorts.env.example` e o `.env` do usuário.

**Backends são configuração, não código:** leia `$MS/.env` (ou `~/.config/makeshorts/.env`) antes de
começar e siga o que está lá. Numa VPS sem GPU o normal é `MS_VOZ=edge|openai|elevenlabs`,
`MS_TRANSCRICAO=groq|openai`, `MS_IMAGEM=nenhuma`. Backend pago só roda se o usuário autorizou
aquele serviço explicitamente.

## Workspace

`~/projetos/output/makeshorts/<AAAA-MM-DD>-<slug>/` com `roteiro.md`, `voz/`, `broll/`, `edicao/`,
`final.mp4`, `legenda.txt`, `qa.json`. Nunca sobrescreva o bruto do usuário.

## Regras duras

- **Nenhuma API sem autorização explícita** (HeyGen, Metricool publicar, qualquer outra). Transcrição
  e voz são locais (inemavox). Avatar e post agendado: descreva o que vai acontecer e espere o "sim".
- **Só fatos verificados** no roteiro; nada de número inventado.
- **Não parecer anúncio** da ferramenta: é mini-tutorial que entrega valor.
- **Rótulo de IA** ligado em todo post com avatar ou voz clonada.
- Mostre o resultado (contact sheet / frames) antes de publicar; o usuário decide.
