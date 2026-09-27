# 🎬 MakeShorts — AI Shorts Factory

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

[![MakeShorts](guia/assets/banner.jpg)](https://inematds.github.io/makeshorts/guia/en/)

From **topic** to **published short** inside Claude Code: 3-act script, voice or avatar, real b-roll,
1080x1920 vertical editing, automatic quality gate, caption with hashtags and social scheduling,
plus the "comment WORD" → DM funnel. Runs on a GPU machine (fully local) or on a **VPS with just APIs**.

## 📖 User guide

Full guide (landing + step by step): **https://inematds.github.io/makeshorts/guia/en/**

---

## Table of contents
1. [What it is](#what-it-is)
2. [How it works](#how-it-works)
3. [Repository structure](#repository-structure)
4. [Installation](#installation)
5. [Configuration (backends)](#configuration-backends)
6. [Usage — the 5 modes](#usage--the-5-modes)
7. [The script formula](#the-script-formula)
8. [Visual specification](#visual-specification)
9. [QA gate](#qa-gate)
10. [Publishing and DM funnel](#publishing-and-dm-funnel)
11. [Running on a VPS with APIs (no local voice)](#running-on-a-vps-with-apis-no-local-voice)
12. [Scripts — reference](#scripts--reference)
13. [Troubleshooting](#troubleshooting)

---

## What it is

MakeShorts is a **Claude Code skill** (`/makeshorts`) with supporting scripts that turns a topic,
a link or a recorded clip into a short ready for Reels, TikTok, YouTube Shorts and Kwai.

- **Orchestrates, doesn't reinvent.** Uses the pieces that already exist: HyperFrames for editing, inemavox for voice and
  local transcription, HeyGen for the avatar, Metricool for scheduling.
- **Fixed formula, variable topic.** Every short follows hook → secondary hook → 3-step delivery → CTA.
- **Measured quality.** Nothing ships without passing `qa_short.py` (duration, format, loudness, visual hook,
  hashtags, CTA).
- **Swappable backends.** Voice, transcription and image change with one line in `.env` — local or API.

## How it works

```
topic / link / clip
   │
   ├─ 1. SCRIPT ......... 3 versions, ~75 words, facts only from official sources
   ├─ 2. VOICE / FACE ... human recording · voice (inemavox | edge | openai | elevenlabs) · HeyGen avatar
   ├─ 3. B-ROLL ......... website and GitHub scrolling, official demos (generated image only if missing)
   ├─ 4. EDITING ........ 1080x1920, visual on top / face below, word-by-word captions, SFX
   ├─ 5. QA ............. qa_short.py — fails and goes back if it doesn't pass
   ├─ 6. PUBLISH ........ caption + ≤5 hashtags + AI label → Metricool (with your confirmation)
   └─ 7. FUNNEL ......... "Comment AI" → automatic DM with the link
```

Skills that makeshorts calls by name (installed in the INEMA environment):

| Stage | Skill / tool |
|---|---|
| Refine the script in the INEMA tone | `roteirista-inema` |
| Avatar | `avatar-heygen-nei` → `heygen-cli` |
| Website/GitHub capture | `agent-browser`, `website-intelligence` |
| 16:9 talk editing → stacked reel | `reel-edita-inema` |
| Raw vertical clip editing | `reel-edita-inematds` |
| Free-form composition | `hyperframes` + `general-video` |
| Word-by-word captions | `embedded-captions` |
| Scheduling | Metricool MCP |

Outside the INEMA environment, Claude Code follows the same steps using HyperFrames and ffmpeg directly.

## Repository structure

```
makeshorts/
├── .claude/skills/makeshorts/        ← the skill
│   ├── SKILL.md                      orchestrator (modes, pipeline, rules)
│   ├── references/
│   │   ├── roteiro.md                3-act formula + hook banks
│   │   ├── spec-visual.md            editing checklist
│   │   ├── publicar.md               caption, hashtags, Metricool
│   │   └── funil-dm.md               "comment WORD" → DM (ManyChat)
│   └── scripts/qa_short.py           quality gate
├── scripts/
│   ├── instalar.sh                   links the skill + creates .env + checks dependencies
│   ├── voz.py                        narration (backend in MS_VOZ)
│   ├── transcreve.py                 transcription with per-word timing (MS_TRANSCRICAO)
│   └── _config.py                    reads .env
├── config/makeshorts.env.example     all backends and keys, commented
├── prompts/README.md                 ready-made prompts to use without the skill
├── docs/vps.md                       installation and config on a VPS
├── guia/                             landing + guide (PT, en/, es/)
└── capa/capa.png                     catalog cover
```

## Installation

Prerequisites: **Claude Code** (subscription), `ffmpeg`, `python3`, `node`/`npx`.

```bash
git clone https://github.com/inematds/makeshorts.git
cd makeshorts
bash scripts/instalar.sh --check   # only checks dependencies
bash scripts/instalar.sh           # links ~/.claude/skills/makeshorts and creates .env
npx hyperframes skills update general-video   # editing engine
```

`instalar.sh` creates a **symlink** — editing the skill in the repo takes effect in Claude Code right away.
To use it only in this project, without installing globally, just open Claude Code inside the folder
(the skill lives in `.claude/skills/`).

## Configuration (backends)

Everything in **one file**: `.env` at the repo root (or `~/.config/makeshorts/.env`). Commented template at
`config/makeshorts.env.example`. Read order: exported variables → repo `.env` →
`~/.config/makeshorts/.env` → defaults.

| Variable | Values | Default |
|---|---|---|
| `MS_VOZ` | `inemavox` · `edge` · `openai` · `elevenlabs` | `inemavox` |
| `MS_TRANSCRICAO` | `inemavox` · `groq` · `openai` | `inemavox` |
| `MS_IMAGEM` | `flux-local` · `nenhuma` | `flux-local` |
| `MS_AVATAR` | `heygen` · `nenhum` | `nenhum` |
| `MS_PUBLICAR` | `metricool` · `manual` | `metricool` |
| `MS_SAIDA` | output folder | `~/projetos/output/makeshorts` |
| `INEMAVOX_REF` | reference .wav of the local cloned voice | `rachel.wav` |
| `EDGE_VOZ` | Edge voice (`pt-BR-AntonioNeural`, `pt-BR-FranciscaNeural`…) | Antonio |
| `OPENAI_TTS_MODELO` / `OPENAI_TTS_VOZ` | OpenAI model and voice | `gpt-4o-mini-tts` / `onyx` |
| `ELEVENLABS_VOICE_ID` / `ELEVENLABS_MODELO` | your cloned voice | — / `eleven_multilingual_v2` |
| `GROQ_WHISPER_MODELO` / `OPENAI_WHISPER_MODELO` | Whisper model | `whisper-large-v3-turbo` / `whisper-1` |
| `OPENAI_API_KEY`, `ELEVENLABS_API_KEY`, `GROQ_API_KEY`, `HEYGEN_API_KEY` | keys | empty |

`.env` is in `.gitignore`. **Keys never go into git.**

## Usage — the 5 modes

In Claude Code, call `/makeshorts` or just talk naturally:

| Mode | Example request | Result |
|---|---|---|
| **1 · Script** | "makeshorts: 3 scripts about Claude Code on your phone" | 3 versions + titles + recommendation |
| **2 · Human** | "edit the short `~/Downloads/clip.mp4`" | edited short + caption + QA |
| **3 · AI** | "make a short about the site https://…, no recording" | script → voice/avatar → b-roll → editing → QA |
| **4 · Publish** | "publish `final.mp4` to Instagram and TikTok tomorrow at 6pm" | QA → caption → scheduling (after confirmation) |
| **5 · Batch** | "5 shorts on this week's free AI tools, one a day" | mode 3 in series, scheduled |

Each short becomes a folder at `MS_SAIDA/<YYYY-MM-DD>-<slug>/`:
`roteiro.md`, `voz/`, `transcricao/`, `broll/`, `edicao/`, `final.mp4`, `legenda.txt`, `qa.json`.

Without the skill, use the prompts in [`prompts/README.md`](prompts/README.md) (in Portuguese).

## The script formula

| Act | Time | Purpose |
|---|---|---|
| Hook | 0–3 s | stop the scroll — "Are you still doing X by hand?" |
| Secondary hook | 3–8 s | curiosity — "And it's not what you're thinking." |
| Delivery | 8–28 s | 3 simple steps, straight to the point |
| CTA | 28–32 s | `Comment "AI" and I'll send you the link` |

~75 words, plain language, one idea per short, facts only from official sources, **3 versions** to
choose from. Details and hook banks: [`references/roteiro.md`](.claude/skills/makeshorts/references/roteiro.md) (in Portuguese).

## Visual specification

1080x1920 · ≤ 59 s (ideal 25–45) · visual from frame 0 · split screen (topic on top, face below) ·
1–3 word captions in a dark pill with an amber keyword · punch-in + flash on each change ·
short SFX, no music · text away from the bottom edge and never over the face · audio at -14 LUFS ·
CTA with the face visible. Full spec: [`references/spec-visual.md`](.claude/skills/makeshorts/references/spec-visual.md) (in Portuguese).

## QA gate

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

Exit `0` = passed, `1` = failed. `--json` for structured output. What the script can't see (text
over the face, legibility) Claude checks by looking at 3 frames.

## Publishing and DM funnel

- **Caption:** title with a benefit + comment CTA. **Maximum 5 hashtags** (Instagram rejects more
  than that), specific and varied. AI label turned on when there's an avatar or synthetic voice.
- **Scheduling:** Metricool MCP (`getBrandSettings` → `getBestTimeToPostByNetwork` →
  `createScheduledPostForReview` / `createScheduledPost`). Always with your confirmation first.
  Details: [`references/publicar.md`](.claude/skills/makeshorts/references/publicar.md) (in Portuguese).
- **Funnel:** "Comment AI" → public reply → DM with button → link. Step-by-step ManyChat
  setup: [`references/funil-dm.md`](.claude/skills/makeshorts/references/funil-dm.md) (in Portuguese).

## Running on a VPS with APIs (no local voice)

A VPS has no GPU and no inemavox. **No code changes — only the `.env`:**

| Stage | GPU machine | VPS | Where to change |
|---|---|---|---|
| Voice | `MS_VOZ=inemavox` | `MS_VOZ=edge` (free) · `openai` · `elevenlabs` | `.env` → `MS_VOZ` + key |
| Transcription | `MS_TRANSCRICAO=inemavox` | `MS_TRANSCRICAO=groq` · `openai` | `.env` → `MS_TRANSCRICAO` + key |
| Image | `MS_IMAGEM=flux-local` | `MS_IMAGEM=nenhuma` (real b-roll) | `.env` → `MS_IMAGEM` |
| Avatar | HeyGen | HeyGen | `MS_AVATAR=heygen` + `HEYGEN_API_KEY` |
| Editing / QA | HyperFrames + ffmpeg | same (CPU) | — |

Typical VPS `.env`:

```bash
MS_VOZ=edge
EDGE_VOZ=pt-BR-AntonioNeural
MS_TRANSCRICAO=groq
GROQ_API_KEY=gsk_...
MS_IMAGEM=nenhuma
MS_SAIDA=~/shorts
```

With **your cloned voice**: `MS_VOZ=elevenlabs`, `ELEVENLABS_API_KEY=...`, `ELEVENLABS_VOICE_ID=...`.

Full Ubuntu install, reference costs and use with `tmux`: **[`docs/vps.md`](docs/vps.md) (in Portuguese)**.

## Scripts — reference

| Script | Usage |
|---|---|
| `scripts/instalar.sh [--check]` | checks dependencies; links the skill; creates `.env` |
| `scripts/voz.py --texto "…" \| --arquivo f.txt --out saida.wav [--backend edge]` | narration |
| `scripts/transcreve.py --in audio.wav --outdir pasta [--backend groq]` | `transcript.json` + `.txt` |
| `.claude/skills/makeshorts/scripts/qa_short.py video.mp4 [--caption f.txt] [--json]` | QA gate |

The output format of `voz.py` follows the `--out` extension (`.wav`, `.mp3`…).

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `falta OPENAI_API_KEY no .env` | paid backend chosen without a key | fill in the key or switch `MS_VOZ` |
| `instale: pip install edge-tts` | `edge` backend without the package | `pip install --user edge-tts` |
| QA fails loudness | audio not at -14 LUFS | `ffmpeg -i in.mp4 -af loudnorm=I=-14:TP=-1.5:LRA=11 -c:v copy out.mp4` |
| QA fails visual hook | black screen at the start | trim the start or put the b-roll at frame 0 |
| Instagram rejects the post | more than 5 hashtags | reduce to 3–5 |
| `python: command not found` in inemavox | no `python` on PATH | the scripts already use `inemavox/venv/bin/python` |

---

Open and free project by **[INEMA.CLUB](https://inema.club)**.
