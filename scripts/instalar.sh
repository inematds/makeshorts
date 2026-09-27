#!/usr/bin/env bash
# instalar.sh — liga a skill makeshorts no Claude Code e prepara a configuração.
#   bash scripts/instalar.sh          # instala (symlink em ~/.claude/skills/makeshorts)
#   bash scripts/instalar.sh --check  # só confere dependências
set -euo pipefail
MS="$(cd "$(dirname "$0")/.." && pwd)"
ok(){ printf '  ✅ %s\n' "$1"; }; no(){ printf '  ⚠️  %s\n' "$1"; }

echo "Dependências:"
for b in ffmpeg ffprobe python3 node npx; do command -v "$b" >/dev/null && ok "$b" || no "$b ausente"; done
command -v claude >/dev/null && ok "claude (Claude Code)" || no "Claude Code ausente — npm i -g @anthropic-ai/claude-code"
command -v edge-tts >/dev/null && ok "edge-tts (voz sem GPU)" || no "edge-tts ausente (opcional) — pip install edge-tts"
[ -d "$HOME/projetos/inemavox" ] && ok "inemavox (voz/transcrição local)" || no "inemavox ausente → use MS_VOZ=edge|openai|elevenlabs e MS_TRANSCRICAO=groq|openai"
command -v nvidia-smi >/dev/null && ok "GPU NVIDIA" || no "sem GPU → modo VPS (backends por API)"
[ "${1:-}" = "--check" ] && exit 0

mkdir -p "$HOME/.claude/skills"
if [ -e "$HOME/.claude/skills/makeshorts" ] && [ ! -L "$HOME/.claude/skills/makeshorts" ]; then
  echo "!! ~/.claude/skills/makeshorts já existe e não é symlink — não mexi"; exit 1
fi
ln -sfn "$MS/.claude/skills/makeshorts" "$HOME/.claude/skills/makeshorts"
ok "skill ligada: ~/.claude/skills/makeshorts → $MS/.claude/skills/makeshorts"

if [ ! -f "$MS/.env" ] && [ ! -f "$HOME/.config/makeshorts/.env" ]; then
  cp "$MS/config/makeshorts.env.example" "$MS/.env"
  ok "criado $MS/.env (edite os backends e chaves)"
fi
echo "Pronto. No Claude Code: /makeshorts  ou  \"faz um short sobre <tema>\""
