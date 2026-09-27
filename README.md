# 🎬 MakeShorts — Fábrica de Shorts com IA

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

[![MakeShorts](guia/assets/banner.jpg)](https://inematds.github.io/makeshorts/guia/)

Do **tema** ao **short publicado** dentro do Claude Code: roteiro em 3 atos, voz ou avatar, b-roll real,
edição vertical 1080x1920, portão de qualidade automático, legenda com hashtags e agendamento nas redes,
e ainda o funil "comente PALAVRA" → DM. Roda na máquina com GPU (tudo local) ou numa **VPS só com APIs**.

## 📖 Guia de uso

Guia completo (landing + passo a passo): **https://inematds.github.io/makeshorts/guia/**

---

## Sumário
1. [O que é](#o-que-é)
2. [Como funciona](#como-funciona)
3. [Estrutura do repositório](#estrutura-do-repositório)
4. [Instalação](#instalação)
5. [Configuração (backends)](#configuração-backends)
6. [Uso — os 5 modos](#uso--os-5-modos)
7. [A fórmula do roteiro](#a-fórmula-do-roteiro)
8. [Especificação visual](#especificação-visual)
9. [Portão de QA](#portão-de-qa)
10. [Publicação e funil de DM](#publicação-e-funil-de-dm)
11. [Rodar numa VPS com APIs (sem voz local)](#rodar-numa-vps-com-apis-sem-voz-local)
12. [Scripts — referência](#scripts--referência)
13. [Solução de problemas](#solução-de-problemas)

---

## O que é

MakeShorts é uma **skill do Claude Code** (`/makeshorts`) com scripts de apoio que transforma um tema,
um link ou um clipe gravado em short pronto para Reels, TikTok, YouTube Shorts e Kwai.

- **Orquestra, não reinventa.** Usa as peças que já existem: HyperFrames para editar, inemavox para voz e
  transcrição local, HeyGen para avatar, Metricool para agendar.
- **Fórmula fixa, tema variável.** Todo short segue gancho → gancho secundário → entrega em 3 passos → CTA.
- **Qualidade medida.** Nada sai sem passar pelo `qa_short.py` (duração, formato, loudness, gancho visual,
  hashtags, CTA).
- **Backends trocáveis.** Voz, transcrição e imagem mudam por uma linha no `.env` — local ou API.

## Como funciona

```
tema / link / clipe
   │
   ├─ 1. ROTEIRO ........ 3 versões, ~75 palavras, fatos só de fonte oficial
   ├─ 2. VOZ / ROSTO .... gravação humana · voz (inemavox | edge | openai | elevenlabs) · avatar HeyGen
   ├─ 3. B-ROLL ......... site e GitHub rolando, demos oficiais (imagem gerada só se faltar)
   ├─ 4. EDIÇÃO ......... 1080x1920, visual em cima / rosto embaixo, legenda palavra a palavra, SFX
   ├─ 5. QA ............. qa_short.py — reprova e volta se falhar
   ├─ 6. PUBLICAR ....... legenda + ≤5 hashtags + rótulo de IA → Metricool (com sua confirmação)
   └─ 7. FUNIL .......... "Comenta IA" → DM automática com o link
```

Skills que o makeshorts chama por nome (instaladas no ambiente INEMA):

| Etapa | Skill / ferramenta |
|---|---|
| Refinar roteiro no tom INEMA | `roteirista-inema` |
| Avatar | `avatar-heygen-nei` → `heygen-cli` |
| Captura de site/GitHub | `agent-browser`, `website-intelligence` |
| Edição de fala 16:9 → reel empilhado | `reel-edita-inema` |
| Edição de clipe vertical cru | `reel-edita-inematds` |
| Composição livre | `hyperframes` + `general-video` |
| Legendas palavra a palavra | `embedded-captions` |
| Agendamento | Metricool MCP |

Fora do ambiente INEMA, o Claude Code segue os mesmos passos usando HyperFrames e ffmpeg direto.

## Estrutura do repositório

```
makeshorts/
├── .claude/skills/makeshorts/        ← a skill
│   ├── SKILL.md                      orquestrador (modos, pipeline, regras)
│   ├── references/
│   │   ├── roteiro.md                fórmula 3 atos + bancos de gancho
│   │   ├── spec-visual.md            checklist de edição
│   │   ├── publicar.md               legenda, hashtags, Metricool
│   │   └── funil-dm.md               "comente PALAVRA" → DM (ManyChat)
│   └── scripts/qa_short.py           portão de qualidade
├── scripts/
│   ├── instalar.sh                   liga a skill + cria .env + checa dependências
│   ├── voz.py                        narração (backend em MS_VOZ)
│   ├── transcreve.py                 transcrição com tempo por palavra (MS_TRANSCRICAO)
│   └── _config.py                    leitura do .env
├── config/makeshorts.env.example     todos os backends e chaves, comentados
├── prompts/README.md                 prompts prontos para usar sem a skill
├── docs/vps.md                       instalação e config numa VPS
├── guia/                             landing + guia (PT, en/, es/)
└── capa/capa.png                     capa do catálogo
```

## Instalação

Pré-requisitos: **Claude Code** (assinatura), `ffmpeg`, `python3`, `node`/`npx`.

```bash
git clone https://github.com/inematds/makeshorts.git
cd makeshorts
bash scripts/instalar.sh --check   # só confere dependências
bash scripts/instalar.sh           # liga ~/.claude/skills/makeshorts e cria .env
npx hyperframes skills update general-video   # motor de edição
```

O `instalar.sh` cria um **symlink** — editar a skill no repo já vale no Claude Code.
Para usar só neste projeto, sem instalar globalmente, basta abrir o Claude Code dentro da pasta
(a skill está em `.claude/skills/`).

## Configuração (backends)

Tudo em **um arquivo**: `.env` na raiz do repo (ou `~/.config/makeshorts/.env`). Modelo comentado em
`config/makeshorts.env.example`. Ordem de leitura: variáveis exportadas → `.env` do repo →
`~/.config/makeshorts/.env` → defaults.

| Variável | Valores | Padrão |
|---|---|---|
| `MS_VOZ` | `inemavox` · `edge` · `openai` · `elevenlabs` | `inemavox` |
| `MS_TRANSCRICAO` | `inemavox` · `groq` · `openai` | `inemavox` |
| `MS_IMAGEM` | `flux-local` · `nenhuma` | `flux-local` |
| `MS_AVATAR` | `heygen` · `nenhum` | `nenhum` |
| `MS_PUBLICAR` | `metricool` · `manual` | `metricool` |
| `MS_SAIDA` | pasta de saída | `~/projetos/output/makeshorts` |
| `INEMAVOX_REF` | .wav de referência da voz clonada local | `rachel.wav` |
| `EDGE_VOZ` | voz Edge (`pt-BR-AntonioNeural`, `pt-BR-FranciscaNeural`…) | Antonio |
| `OPENAI_TTS_MODELO` / `OPENAI_TTS_VOZ` | modelo e voz OpenAI | `gpt-4o-mini-tts` / `onyx` |
| `ELEVENLABS_VOICE_ID` / `ELEVENLABS_MODELO` | sua voz clonada | — / `eleven_multilingual_v2` |
| `GROQ_WHISPER_MODELO` / `OPENAI_WHISPER_MODELO` | modelo Whisper | `whisper-large-v3-turbo` / `whisper-1` |
| `OPENAI_API_KEY`, `ELEVENLABS_API_KEY`, `GROQ_API_KEY`, `HEYGEN_API_KEY` | chaves | vazias |

O `.env` está no `.gitignore`. **Chave nunca vai para o git.**

## Uso — os 5 modos

No Claude Code, chame `/makeshorts` ou fale naturalmente:

| Modo | Exemplo de pedido | Resultado |
|---|---|---|
| **1 · Roteiro** | "makeshorts: 3 roteiros sobre o Claude Code no celular" | 3 versões + títulos + recomendação |
| **2 · Humano** | "edita o short `~/Downloads/clip.mp4`" | short editado + legenda + QA |
| **3 · IA** | "faz um short sobre o site https://…, sem gravar" | roteiro → voz/avatar → b-roll → edição → QA |
| **4 · Publicar** | "publica `final.mp4` no Instagram e TikTok amanhã 18h" | QA → legenda → agendamento (após confirmação) |
| **5 · Lote** | "5 shorts de ferramentas de IA gratuitas da semana, um por dia" | modo 3 em série, agendados |

Cada short vira uma pasta em `MS_SAIDA/<AAAA-MM-DD>-<slug>/`:
`roteiro.md`, `voz/`, `transcricao/`, `broll/`, `edicao/`, `final.mp4`, `legenda.txt`, `qa.json`.

Sem a skill, use os prompts de [`prompts/README.md`](prompts/README.md).

## A fórmula do roteiro

| Ato | Tempo | Função |
|---|---|---|
| Gancho | 0–3 s | parar o dedo — "Você ainda faz X na mão?" |
| Gancho secundário | 3–8 s | curiosidade — "E não é o que você tá pensando." |
| Entrega | 8–28 s | 3 passos simples, direto ao ponto |
| CTA | 28–32 s | `Comenta "IA" que eu te mando o link` |

~75 palavras, linguagem simples, uma ideia por short, fatos só de fonte oficial, **3 versões** para
escolher. Detalhes e bancos de gancho: [`references/roteiro.md`](.claude/skills/makeshorts/references/roteiro.md).

## Especificação visual

1080x1920 · ≤ 59 s (ideal 25–45) · visual desde o frame 0 · tela dividida (tema em cima, rosto embaixo) ·
legendas de 1–3 palavras em pílula escura com palavra-chave âmbar · punch-in + flash por troca ·
SFX curtos, sem música · texto fora da borda de baixo e nunca sobre o rosto · áudio em -14 LUFS ·
CTA com o rosto visível. Completo: [`references/spec-visual.md`](.claude/skills/makeshorts/references/spec-visual.md).

## Portão de QA

```bash
python3 .claude/skills/makeshorts/scripts/qa_short.py final.mp4 --caption legenda.txt
```

```
✅ duração        31.2s
✅ formato        1080x1920
✅ loudness       -14.1 LUFS
✅ gancho visual  sem tela preta no início
✅ hashtags       4: #claudecode #ia #automacao #shorts
✅ CTA            pede comentário com palavra-chave

RESULTADO: APROVADO
```

Exit `0` = aprovado, `1` = reprovado. `--json` para saída estruturada. O que o script não vê (texto
sobre rosto, legibilidade) o Claude confere olhando 3 frames.

## Publicação e funil de DM

- **Legenda:** título com benefício + CTA de comentário. **Máximo 5 hashtags** (o Instagram recusa acima
  disso), específicas e variadas. Rótulo de IA ligado quando há avatar ou voz sintética.
- **Agendamento:** Metricool MCP (`getBrandSettings` → `getBestTimeToPostByNetwork` →
  `createScheduledPostForReview` / `createScheduledPost`). Sempre com sua confirmação antes.
  Detalhes: [`references/publicar.md`](.claude/skills/makeshorts/references/publicar.md).
- **Funil:** "Comenta IA" → resposta pública → DM com botão → link. Configuração no ManyChat passo a
  passo: [`references/funil-dm.md`](.claude/skills/makeshorts/references/funil-dm.md).

## Rodar numa VPS com APIs (sem voz local)

Numa VPS não há GPU nem inemavox. **Nada de código muda — só o `.env`:**

| Etapa | Máquina com GPU | VPS | Onde mudar |
|---|---|---|---|
| Voz | `MS_VOZ=inemavox` | `MS_VOZ=edge` (grátis) · `openai` · `elevenlabs` | `.env` → `MS_VOZ` + chave |
| Transcrição | `MS_TRANSCRICAO=inemavox` | `MS_TRANSCRICAO=groq` · `openai` | `.env` → `MS_TRANSCRICAO` + chave |
| Imagem | `MS_IMAGEM=flux-local` | `MS_IMAGEM=nenhuma` (b-roll real) | `.env` → `MS_IMAGEM` |
| Avatar | HeyGen | HeyGen | `MS_AVATAR=heygen` + `HEYGEN_API_KEY` |
| Edição / QA | HyperFrames + ffmpeg | igual (CPU) | — |

`.env` típico de VPS:

```bash
MS_VOZ=edge
EDGE_VOZ=pt-BR-AntonioNeural
MS_TRANSCRICAO=groq
GROQ_API_KEY=gsk_...
MS_IMAGEM=nenhuma
MS_SAIDA=~/shorts
```

Com a **sua voz clonada**: `MS_VOZ=elevenlabs`, `ELEVENLABS_API_KEY=...`, `ELEVENLABS_VOICE_ID=...`.

Instalação completa no Ubuntu, custos de referência e uso com `tmux`: **[`docs/vps.md`](docs/vps.md)**.

## Scripts — referência

| Script | Uso |
|---|---|
| `scripts/instalar.sh [--check]` | checa dependências; liga a skill; cria `.env` |
| `scripts/voz.py --texto "…" \| --arquivo f.txt --out saida.wav [--backend edge]` | narração |
| `scripts/transcreve.py --in audio.wav --outdir pasta [--backend groq]` | `transcript.json` + `.txt` |
| `.claude/skills/makeshorts/scripts/qa_short.py video.mp4 [--caption f.txt] [--json]` | portão de QA |

O formato de saída de `voz.py` segue a extensão de `--out` (`.wav`, `.mp3`…).

## Solução de problemas

| Sintoma | Causa provável | Correção |
|---|---|---|
| `falta OPENAI_API_KEY no .env` | backend pago escolhido sem chave | preencher a chave ou trocar `MS_VOZ` |
| `instale: pip install edge-tts` | backend `edge` sem o pacote | `pip install --user edge-tts` |
| QA reprova loudness | áudio fora de -14 LUFS | `ffmpeg -i in.mp4 -af loudnorm=I=-14:TP=-1.5:LRA=11 -c:v copy out.mp4` |
| QA reprova gancho visual | tela preta no começo | cortar o início ou pôr o b-roll no frame 0 |
| Instagram recusa o post | mais de 5 hashtags | reduzir para 3–5 |
| `python: command not found` no inemavox | sem `python` no PATH | os scripts já usam `inemavox/venv/bin/python` |

---

Projeto aberto e gratuito do **[INEMA.CLUB](https://inema.club)**.
