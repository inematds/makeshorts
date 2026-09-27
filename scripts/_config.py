"""Carrega a configuração do makeshorts.

Ordem (o primeiro que existir vence para cada chave):
  1. variáveis de ambiente já exportadas
  2. .env na raiz do repo
  3. ~/.config/makeshorts/.env
  4. config/makeshorts.env.example (defaults)
"""
import os
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ARQUIVOS = [REPO / ".env",
            Path.home() / ".config/makeshorts/.env",
            REPO / "config/makeshorts.env.example"]


def _ler(p):
    d = {}
    if p.exists():
        for ln in p.read_text(encoding="utf-8").splitlines():
            ln = ln.strip()
            if ln and not ln.startswith("#") and "=" in ln:
                k, v = ln.split("=", 1)
                d[k.strip()] = v.split(" #")[0].strip().strip('"').strip("'")
    return d


def cfg():
    out = {}
    for p in reversed(ARQUIVOS):
        out.update({k: v for k, v in _ler(p).items() if v != "" or k not in out})
    out.update({k: v for k, v in os.environ.items() if k.startswith(("MS_", "OPENAI", "ELEVENLABS",
                                                                      "GROQ", "EDGE", "INEMAVOX", "HEYGEN", "INEMAIMG"))})
    for k, v in out.items():
        if isinstance(v, str) and v.startswith("~"):
            out[k] = os.path.expanduser(v)
    return out


def exige(c, chave):
    if not c.get(chave):
        raise SystemExit(f"falta {chave} no .env (backend escolhido exige essa chave)")
    return c[chave]
