# 🎬 MakeShorts — Fábrica de Shorts con IA

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

[![MakeShorts](guia/assets/banner.jpg)](https://inematds.github.io/makeshorts/guia/es/)

Del **tema** al **short publicado** dentro de Claude Code: guion en 3 actos, voz o avatar, b-roll real,
edición vertical 1080x1920, control de calidad automático, descripción con hashtags y programación en redes,
y además el embudo "comenta PALABRA" → DM. Corre en la máquina con GPU (todo local) o en un **VPS solo con APIs**.

## 📖 Guía de uso

Guía completa (landing + paso a paso): **https://inematds.github.io/makeshorts/guia/es/**

---

## Índice
1. [Qué es](#qué-es)
2. [Cómo funciona](#cómo-funciona)
3. [Estructura del repositorio](#estructura-del-repositorio)
4. [Instalación](#instalación)
5. [Configuración (backends)](#configuración-backends)
6. [Uso — los 5 modos](#uso--los-5-modos)
7. [La fórmula del guion](#la-fórmula-del-guion)
8. [Especificación visual](#especificación-visual)
9. [Control de QA](#control-de-qa)
10. [Publicación y embudo de DM](#publicación-y-embudo-de-dm)
11. [Correr en un VPS con APIs (sin voz local)](#correr-en-un-vps-con-apis-sin-voz-local)
12. [Scripts — referencia](#scripts--referencia)
13. [Solución de problemas](#solución-de-problemas)

---

## Qué es

MakeShorts es una **skill de Claude Code** (`/makeshorts`) con scripts de apoyo que convierte un tema,
un enlace o un clip grabado en un short listo para Reels, TikTok, YouTube Shorts y Kwai.

- **Orquesta, no reinventa.** Usa las piezas que ya existen: HyperFrames para editar, inemavox para voz y
  transcripción local, HeyGen para avatar, Metricool para programar.
- **Fórmula fija, tema variable.** Todo short sigue gancho → gancho secundario → entrega en 3 pasos → CTA.
- **Calidad medida.** Nada sale sin pasar por `qa_short.py` (duración, formato, loudness, gancho visual,
  hashtags, CTA).
- **Backends intercambiables.** Voz, transcripción e imagen cambian con una línea en el `.env` — local o API.

## Cómo funciona

```
tema / enlace / clip
   │
   ├─ 1. GUION .......... 3 versiones, ~75 palabras, datos solo de fuente oficial
   ├─ 2. VOZ / ROSTRO ... grabación humana · voz (inemavox | edge | openai | elevenlabs) · avatar HeyGen
   ├─ 3. B-ROLL ......... sitio y GitHub en desplazamiento, demos oficiales (imagen generada solo si falta)
   ├─ 4. EDICIÓN ........ 1080x1920, visual arriba / rostro abajo, subtítulo palabra por palabra, SFX
   ├─ 5. QA ............. qa_short.py — reprueba y vuelve atrás si falla
   ├─ 6. PUBLICAR ....... descripción + ≤5 hashtags + etiqueta de IA → Metricool (con tu confirmación)
   └─ 7. EMBUDO ......... "Comenta IA" → DM automático con el enlace
```

Skills que makeshorts llama por nombre (instaladas en el entorno INEMA):

| Etapa | Skill / herramienta |
|---|---|
| Refinar el guion con el tono INEMA | `roteirista-inema` |
| Avatar | `avatar-heygen-nei` → `heygen-cli` |
| Captura de sitio/GitHub | `agent-browser`, `website-intelligence` |
| Edición de habla 16:9 → reel apilado | `reel-edita-inema` |
| Edición de clip vertical en bruto | `reel-edita-inematds` |
| Composición libre | `hyperframes` + `general-video` |
| Subtítulos palabra por palabra | `embedded-captions` |
| Programación | Metricool MCP |

Fuera del entorno INEMA, Claude Code sigue los mismos pasos usando HyperFrames y ffmpeg directamente.

## Estructura del repositorio

```
makeshorts/
├── .claude/skills/makeshorts/        ← la skill
│   ├── SKILL.md                      orquestador (modos, pipeline, reglas)
│   ├── references/
│   │   ├── roteiro.md                fórmula de 3 actos + bancos de ganchos
│   │   ├── spec-visual.md            checklist de edición
│   │   ├── publicar.md               descripción, hashtags, Metricool
│   │   └── funil-dm.md               "comenta PALABRA" → DM (ManyChat)
│   └── scripts/qa_short.py           control de calidad
├── scripts/
│   ├── instalar.sh                   enlaza la skill + crea .env + revisa dependencias
│   ├── voz.py                        narración (backend en MS_VOZ)
│   ├── transcreve.py                 transcripción con tiempo por palabra (MS_TRANSCRICAO)
│   └── _config.py                    lectura del .env
├── config/makeshorts.env.example     todos los backends y claves, comentados
├── prompts/README.md                 prompts listos para usar sin la skill
├── docs/vps.md                       instalación y configuración en un VPS
├── guia/                             landing + guía (PT, en/, es/)
└── capa/capa.png                     portada del catálogo
```

## Instalación

Requisitos previos: **Claude Code** (suscripción), `ffmpeg`, `python3`, `node`/`npx`.

```bash
git clone https://github.com/inematds/makeshorts.git
cd makeshorts
bash scripts/instalar.sh --check   # solo revisa las dependencias
bash scripts/instalar.sh           # enlaza ~/.claude/skills/makeshorts y crea .env
npx hyperframes skills update general-video   # motor de edición
```

`instalar.sh` crea un **symlink** — editar la skill en el repo ya surte efecto en Claude Code.
Para usarla solo en este proyecto, sin instalarla globalmente, basta con abrir Claude Code dentro de la carpeta
(la skill está en `.claude/skills/`).

## Configuración (backends)

Todo en **un archivo**: `.env` en la raíz del repo (o `~/.config/makeshorts/.env`). Modelo comentado en
`config/makeshorts.env.example`. Orden de lectura: variables exportadas → `.env` del repo →
`~/.config/makeshorts/.env` → valores por defecto.

| Variable | Valores | Por defecto |
|---|---|---|
| `MS_VOZ` | `inemavox` · `edge` · `openai` · `elevenlabs` | `inemavox` |
| `MS_TRANSCRICAO` | `inemavox` · `groq` · `openai` | `inemavox` |
| `MS_IMAGEM` | `flux-local` · `nenhuma` | `flux-local` |
| `MS_AVATAR` | `heygen` · `nenhum` | `nenhum` |
| `MS_PUBLICAR` | `metricool` · `manual` | `metricool` |
| `MS_SAIDA` | carpeta de salida | `~/projetos/output/makeshorts` |
| `INEMAVOX_REF` | .wav de referencia de la voz clonada local | `rachel.wav` |
| `EDGE_VOZ` | voz Edge (`pt-BR-AntonioNeural`, `pt-BR-FranciscaNeural`…) | Antonio |
| `OPENAI_TTS_MODELO` / `OPENAI_TTS_VOZ` | modelo y voz de OpenAI | `gpt-4o-mini-tts` / `onyx` |
| `ELEVENLABS_VOICE_ID` / `ELEVENLABS_MODELO` | tu voz clonada | — / `eleven_multilingual_v2` |
| `GROQ_WHISPER_MODELO` / `OPENAI_WHISPER_MODELO` | modelo Whisper | `whisper-large-v3-turbo` / `whisper-1` |
| `OPENAI_API_KEY`, `ELEVENLABS_API_KEY`, `GROQ_API_KEY`, `HEYGEN_API_KEY` | claves | vacías |

El `.env` está en el `.gitignore`. **Las claves nunca van al git.**

## Uso — los 5 modos

En Claude Code, llama a `/makeshorts` o habla con naturalidad:

| Modo | Ejemplo de pedido | Resultado |
|---|---|---|
| **1 · Guion** | "makeshorts: 3 guiones sobre Claude Code en el celular" | 3 versiones + títulos + recomendación |
| **2 · Humano** | "edita el short `~/Downloads/clip.mp4`" | short editado + descripción + QA |
| **3 · IA** | "haz un short sobre el sitio https://…, sin grabar" | guion → voz/avatar → b-roll → edición → QA |
| **4 · Publicar** | "publica `final.mp4` en Instagram y TikTok mañana a las 18h" | QA → descripción → programación (tras confirmación) |
| **5 · Lote** | "5 shorts de herramientas de IA gratuitas de la semana, uno por día" | modo 3 en serie, programados |

Cada short se convierte en una carpeta en `MS_SAIDA/<AAAA-MM-DD>-<slug>/`:
`roteiro.md`, `voz/`, `transcricao/`, `broll/`, `edicao/`, `final.mp4`, `legenda.txt`, `qa.json`.

Sin la skill, usa los prompts de [`prompts/README.md`](prompts/README.md) (en portugués).

## La fórmula del guion

| Acto | Tiempo | Función |
|---|---|---|
| Gancho | 0–3 s | detener el dedo — "¿Todavía haces X a mano?" |
| Gancho secundario | 3–8 s | curiosidad — "Y no es lo que estás pensando." |
| Entrega | 8–28 s | 3 pasos simples, directo al grano |
| CTA | 28–32 s | `Comenta "IA" y te mando el enlace` |

~75 palabras, lenguaje sencillo, una idea por short, datos solo de fuente oficial, **3 versiones** para
elegir. Detalles y bancos de ganchos: [`references/roteiro.md`](.claude/skills/makeshorts/references/roteiro.md) (en portugués).

## Especificación visual

1080x1920 · ≤ 59 s (ideal 25–45) · visual desde el frame 0 · pantalla dividida (tema arriba, rostro abajo) ·
subtítulos de 1–3 palabras en píldora oscura con palabra clave ámbar · punch-in + flash en cada cambio ·
SFX cortos, sin música · texto lejos del borde inferior y nunca sobre el rostro · audio en -14 LUFS ·
CTA con el rostro visible. Completo: [`references/spec-visual.md`](.claude/skills/makeshorts/references/spec-visual.md) (en portugués).

## Control de QA

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

Exit `0` = aprobado, `1` = reprobado. `--json` para salida estructurada. Lo que el script no ve (texto
sobre el rostro, legibilidad) Claude lo revisa mirando 3 frames.

## Publicación y embudo de DM

- **Descripción:** título con beneficio + CTA de comentario. **Máximo 5 hashtags** (Instagram rechaza
  más que eso), específicos y variados. Etiqueta de IA activada cuando hay avatar o voz sintética.
- **Programación:** Metricool MCP (`getBrandSettings` → `getBestTimeToPostByNetwork` →
  `createScheduledPostForReview` / `createScheduledPost`). Siempre con tu confirmación previa.
  Detalles: [`references/publicar.md`](.claude/skills/makeshorts/references/publicar.md) (en portugués).
- **Embudo:** "Comenta IA" → respuesta pública → DM con botón → enlace. Configuración en ManyChat paso a
  paso: [`references/funil-dm.md`](.claude/skills/makeshorts/references/funil-dm.md) (en portugués).

## Correr en un VPS con APIs (sin voz local)

En un VPS no hay GPU ni inemavox. **No cambia nada de código — solo el `.env`:**

| Etapa | Máquina con GPU | VPS | Dónde cambiar |
|---|---|---|---|
| Voz | `MS_VOZ=inemavox` | `MS_VOZ=edge` (gratis) · `openai` · `elevenlabs` | `.env` → `MS_VOZ` + clave |
| Transcripción | `MS_TRANSCRICAO=inemavox` | `MS_TRANSCRICAO=groq` · `openai` | `.env` → `MS_TRANSCRICAO` + clave |
| Imagen | `MS_IMAGEM=flux-local` | `MS_IMAGEM=nenhuma` (b-roll real) | `.env` → `MS_IMAGEM` |
| Avatar | HeyGen | HeyGen | `MS_AVATAR=heygen` + `HEYGEN_API_KEY` |
| Edición / QA | HyperFrames + ffmpeg | igual (CPU) | — |

`.env` típico de VPS:

```bash
MS_VOZ=edge
EDGE_VOZ=pt-BR-AntonioNeural
MS_TRANSCRICAO=groq
GROQ_API_KEY=gsk_...
MS_IMAGEM=nenhuma
MS_SAIDA=~/shorts
```

Con **tu voz clonada**: `MS_VOZ=elevenlabs`, `ELEVENLABS_API_KEY=...`, `ELEVENLABS_VOICE_ID=...`.

Instalación completa en Ubuntu, costos de referencia y uso con `tmux`: **[`docs/vps.md`](docs/vps.md) (en portugués)**.

## Scripts — referencia

| Script | Uso |
|---|---|
| `scripts/instalar.sh [--check]` | revisa dependencias; enlaza la skill; crea `.env` |
| `scripts/voz.py --texto "…" \| --arquivo f.txt --out saida.wav [--backend edge]` | narración |
| `scripts/transcreve.py --in audio.wav --outdir pasta [--backend groq]` | `transcript.json` + `.txt` |
| `.claude/skills/makeshorts/scripts/qa_short.py video.mp4 [--caption f.txt] [--json]` | control de QA |

El formato de salida de `voz.py` sigue la extensión de `--out` (`.wav`, `.mp3`…).

## Solución de problemas

| Síntoma | Causa probable | Corrección |
|---|---|---|
| `falta OPENAI_API_KEY no .env` | backend de pago elegido sin clave | completar la clave o cambiar `MS_VOZ` |
| `instale: pip install edge-tts` | backend `edge` sin el paquete | `pip install --user edge-tts` |
| QA reprueba el loudness | audio fuera de -14 LUFS | `ffmpeg -i in.mp4 -af loudnorm=I=-14:TP=-1.5:LRA=11 -c:v copy out.mp4` |
| QA reprueba el gancho visual | pantalla negra al inicio | recortar el inicio o poner el b-roll en el frame 0 |
| Instagram rechaza la publicación | más de 5 hashtags | reducir a 3–5 |
| `python: command not found` en inemavox | sin `python` en el PATH | los scripts ya usan `inemavox/venv/bin/python` |

---

Proyecto abierto y gratuito de **[INEMA.CLUB](https://inema.club)**.
