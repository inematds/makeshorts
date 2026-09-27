# Rodar numa VPS (sem GPU, sem voz local)

O makeshorts foi pensado para a máquina INEMA (GPU + inemavox + flux local), mas **tudo que exige GPU
tem troca por API** — e a troca é **só configuração**, no arquivo `.env`. Nenhum código muda.

## O que muda (e onde)

| Etapa | Na máquina com GPU | Na VPS | Onde mudar |
|---|---|---|---|
| Voz | `MS_VOZ=inemavox` (chatterbox local) | `MS_VOZ=edge` (grátis) · `openai` · `elevenlabs` | `.env` → `MS_VOZ` + chave |
| Transcrição | `MS_TRANSCRICAO=inemavox` (Whisper local) | `MS_TRANSCRICAO=groq` · `openai` | `.env` → `MS_TRANSCRICAO` + chave |
| Imagem de apoio | `MS_IMAGEM=flux-local` | `MS_IMAGEM=nenhuma` (só b-roll real: site, GitHub, demo) | `.env` → `MS_IMAGEM` |
| Avatar | HeyGen (já é API) | HeyGen | `.env` → `MS_AVATAR=heygen` + `HEYGEN_API_KEY` |
| Edição | HyperFrames (CPU + Chromium) | igual | — |
| QA | ffmpeg | igual | — |
| Publicação | Metricool MCP | igual | conector no Claude |

Scripts que leem essa configuração: `scripts/voz.py`, `scripts/transcreve.py`.
Ordem de leitura: variáveis exportadas → `.env` do repo → `~/.config/makeshorts/.env` → defaults.

### Custo aproximado por short de 30 s (referência, confira os preços atuais)
- **Edge TTS:** grátis (serviço online da Microsoft, sem chave; vozes fixas, sem clonagem).
- **OpenAI TTS / ElevenLabs:** centavos por short; ElevenLabs permite a **sua voz clonada**.
- **Groq Whisper:** frações de centavo por minuto.
- **HeyGen:** créditos por render — o item mais caro; use só quando quiser rosto.

## Passo a passo (Ubuntu 22.04/24.04, 2 vCPU / 4 GB já rodam)

```bash
# 1. sistema
sudo apt update && sudo apt install -y ffmpeg python3 python3-pip git curl \
  chromium-browser fonts-noto fonts-noto-color-emoji
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash - && sudo apt install -y nodejs

# 2. Claude Code (login pela sua assinatura)
npm i -g @anthropic-ai/claude-code
claude   # faça o login uma vez

# 3. voz sem GPU (opcional, grátis)
pip install --user edge-tts

# 4. makeshorts
git clone https://github.com/inematds/makeshorts.git && cd makeshorts
bash scripts/instalar.sh          # liga a skill e cria .env

# 5. motor de edição (HyperFrames, roda em CPU)
npx hyperframes skills update general-video
```

## `.env` típico de VPS

```bash
MS_VOZ=edge                  # ou openai / elevenlabs
EDGE_VOZ=pt-BR-AntonioNeural # feminina: pt-BR-FranciscaNeural
MS_TRANSCRICAO=groq
GROQ_API_KEY=gsk_...
MS_IMAGEM=nenhuma
MS_AVATAR=nenhum             # heygen se for usar avatar
MS_PUBLICAR=metricool
MS_SAIDA=~/shorts
```

Com voz clonada:
```bash
MS_VOZ=elevenlabs
ELEVENLABS_API_KEY=...
ELEVENLABS_VOICE_ID=...      # id da sua voz clonada no painel da ElevenLabs
```

## Testar cada peça

```bash
python3 scripts/voz.py --texto "Teste de voz do makeshorts." --out /tmp/t.mp3
python3 scripts/transcreve.py --in /tmp/t.mp3 --outdir /tmp/tr && cat /tmp/tr/transcript.txt
python3 .claude/skills/makeshorts/scripts/qa_short.py seu_video.mp4 --caption legenda.txt
```

## Rodar sem ficar olhando (tmux)

```bash
tmux new -s shorts
claude "faz 5 shorts sobre ferramentas de IA gratuitas desta semana e agenda um por dia às 18h"
# Ctrl-b d para sair; tmux attach -t shorts para voltar
```

## Cuidados
- `.env` fica fora do git (`.gitignore`). Permissão `chmod 600 .env`.
- Chave vazada: revogue no painel do serviço e gere outra.
- A publicação (Metricool) e o avatar (HeyGen) sempre pedem confirmação antes de gastar/publicar.
