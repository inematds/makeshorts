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
(`references/roteiro.md`), o **contrato de reel** (`references/reel-profiles.json` 1.1.0, explicado em
`references/spec-reel.md`), a especificação visual (`references/spec-visual.md`), os públicos
(`references/publicos.md`), os portões de QA (`scripts/qa_short.py`, `scripts/qa_lote.py`) e as regras de
publicação (`references/publicar.md`). **Por que cada regra existe:** `references/aprendizados-2026-10.md`
(o que falhou em cada projeto até 01/10/2026 e o que as redes premiam).

**Antes de produzir:** confira e registre o tema em `~/projetos/wifi/PRODUCOES-VIDEO.md` (tema, dono, pasta,
estado). Em 28/09/2026 duas sessões fizeram os mesmos 9 shorts em paralelo — o registro evita isso.
**Perfil:** escolha `divulgacao`, `tutorial` ou `mini-aula` (duração, palavras e estrutura no contrato).

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

1. **Roteiro** — siga `references/roteiro.md`: **passo zero** (essência, tese, motivo, elemento demonstrável,
   regra prática) e **oficina de gancho** (5 frases, teste da lacuna, ≤ 9 palavras); 3 versões com ganchos e
   estruturas diferentes, palavras do **perfil** escolhido (divulgação 60–110), gancho falado ≤ 2 s e já escrito na tela do frame 0,
   gancho secundário entre 3 e 8 s, **uma promessa por reel**, CTA único. Fatos só de fonte oficial
   (site/GitHub do tema) — abra e confira antes de escrever. Para o tom INEMA, a skill
   **`roteirista-inema`** pode refinar a versão escolhida. **Mostre as 3 e deixe o usuário escolher.**
2. **Voz / rosto** — três opções, da mais barata para a mais cara:
   - **Gravação humana** (20–30 s no celular): o usuário grava, você edita (modo 2).
   - **Voz sintética:** `python3 $MS/scripts/voz.py --arquivo roteiro.txt --out <ws>/voz/narracao.wav`
     — o backend vem de `MS_VOZ` (`inemavox` local/GPU, `edge` grátis sem GPU, `openai`, `elevenlabs`).
     **Voz padrão: a do Nei** (`INEMAVOX_REF=~/projetos/timesmkt3/media/voice-refs/nei.wav`, validada em
     produção). Nunca voz estrangeira falando PT (`rachel` é inglesa: "inema" virou "enema" em 28/09/2026).
   - **Avatar HeyGen (gasta crédito):** skill **`avatar-heygen-nei`** (escolha de look) sobre
     **`heygen-cli`**. **Confirme o custo com o usuário antes de renderizar.**
   Legendas precisam de transcrição com tempo por palavra:
   `python3 $MS/scripts/transcreve.py --in <ws>/voz/narracao.wav --outdir <ws>/transcricao`
   (backend em `MS_TRANSCRICAO`: `inemavox` local, `groq`, `openai`).
3. **B-roll real** — enquanto a voz/avatar renderiza: capture o site e o GitHub do tema com rolagem
   suave (skills **`agent-browser`** / **`website-intelligence`**), demos/GIFs oficiais e a página do curso no
   inema.club. Mostrar a ferramenta funcionando vence card de texto. **Pelo menos 1 em cada 3 visuais é real.**
   Imagem gerada só para ilustrar (flux2-klein local, seed por alvo): **cena cotidiana crível, no mesmo mundo do
   avatar** — nada de cena impossível nem notícia/entrevista simulada (`spec-visual.md`).
4. **Edição** — vertical 1080x1920 seguindo `spec-reel.md` + `spec-visual.md`. Motores, em ordem:
   - **avatar do Nei (HeyGen) → `~/projetos/explicavideos` 9:16** com `"reel_profile"` na config (2.4.3+):
     shot `hook` visível no frame 0, shot `media` com o print real do site/curso, legenda de até 3 palavras,
     30 fps, −14 LUFS e este QA rodando sozinho no `produce.py`. É o caminho padrão para divulgação INEMA.
   - **avatar + imagens no layout empilhado aprovado → `~/projetos/promoavatar3` (`scripts/montar-reel.py`,
     `templates/empilhado-capa.json`)**, com as condições desta skill: segmentos de 2–3 s (não ~6 s), ≥ 1 prova
     real em cada 3 imagens, palavras da legenda ordenadas (o `legendas.py` de lá ainda gera duração negativa —
     passe `--words` no QA), loudnorm no arquivo final;
   - gravação humana 16:9 → **`reel-edita-inema`**; clipe vertical cru → **`reel-edita-inematds`**;
   - sem rosto e sem crédito de avatar → **`hyperframes`** + **`general-video`**, com prova real (gravação de
     tela/print) — nunca só cards de texto; gravação de 30 s no celular é alternativa melhor que sem rosto;
   - legendas palavra-a-palavra em vídeo pronto → **`embedded-captions`**.
   - **`video-explicativo` NÃO faz reel** (é explicativo 16:9 de 1–3 min).
   SFX e música: inemavox (`sfx_v1.py --query whoosh --outdir <ws>/sfx`). **Reel didático sem música de fundo**;
   SFX só onde reforça uma ação, não em toda troca.
5. **Portão de QA (obrigatório)** —
   `python3 $MS/.claude/skills/makeshorts/scripts/qa_short.py final.mp4 --profile divulgacao --srt legendas.srt --words legendas.json --post legenda.txt --sheet folha.png --report qa.json`
   (`--words` quando a legenda palavra a palavra vem em JSON: reprova palavra com duração ≤ 0, que fica presa na tela).
   **Lote:** `python3 $MS/.claude/skills/makeshorts/scripts/qa_lote.py v1.mp4 v2.mp4 …` avisa capas (quadro 0) repetidas.
   Exit 1 = reprovado: corrija e rode de novo. Medição que falha = reprovado (nunca "OK" por omissão).
   Avisos (frame 0 com pouca informação, trechos parados > 4 s) exigem olhar e justificar.
   **O script não mede gancho, prova, pronúncia nem legenda sobre rosto** — faça a revisão humana de
   `spec-reel.md` (inclui o teste do leitor) antes de mostrar ao Nei.
   **Protótipo:** 1 reel aprovado pelo Nei antes de lote, publicação ou envio.
6. **Publicar** — `references/publicar.md`: legenda, ≤ 5 hashtags específicas, rótulo de IA quando
   houver avatar/voz sintética, agendamento via Metricool MCP.
7. **Funil** — o CTA "comente PALAVRA" só converte se a automação de DM estiver ligada
   (`references/funil-dm.md`). **Em 01/10/2026 não está**: use "manda pra quem…" ou "link na bio".
8. **Medir** — skip rate (Reels), viewed vs swiped away (Shorts), % assistido e envios; 2 ganchos do mesmo
   roteiro via Trial Reels (`publicar.md`). Sem número, nenhuma regra desta skill está provada.

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
- **Nada de depoimento inventado nem bastidor falso**: o vídeo só diz sobre si e sobre o Nei o que aconteceu.
- **Não parecer anúncio** da ferramenta: é mini-tutorial que entrega valor.
- **Rótulo de IA** ligado em todo post com avatar ou voz clonada.
- Mostre o resultado (contact sheet / frames) antes de publicar; o usuário decide.
