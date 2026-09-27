#!/usr/bin/env python3
"""voz.py — gera a narração do short com o backend escolhido em MS_VOZ.

  python3 scripts/voz.py --texto "roteiro..." --out ws/voz/narracao.wav
  python3 scripts/voz.py --arquivo roteiro.txt --out ws/voz/narracao.mp3 [--backend edge]

Backends (config/makeshorts.env.example):
  inemavox   TTS local chatterbox (GPU)        — padrão na máquina INEMA
  edge       Edge TTS (grátis, sem GPU)        — padrão recomendado para VPS
  openai     OpenAI TTS (pago)                 — exige OPENAI_API_KEY
  elevenlabs ElevenLabs (pago, voz clonada)    — exige ELEVENLABS_API_KEY + ELEVENLABS_VOICE_ID
A saída é sempre convertida para o formato pedido pela extensão de --out (ffmpeg).
"""
import argparse, json, shutil, subprocess, sys, tempfile, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _config import cfg, exige


def converter(src, dst):
    if Path(src).suffix == Path(dst).suffix:
        shutil.move(src, dst)
    else:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), str(dst)], check=True)


def post(url, headers, body):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=300) as r:
        return r.read()


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--texto")
    g.add_argument("--arquivo")
    ap.add_argument("--out", required=True)
    ap.add_argument("--backend", help="sobrepõe MS_VOZ")
    a = ap.parse_args()

    c = cfg()
    texto = a.texto or Path(a.arquivo).read_text(encoding="utf-8")
    backend = a.backend or c.get("MS_VOZ", "inemavox")
    lang = c.get("MS_VOZ_IDIOMA", "pt")
    out = Path(a.out).expanduser()
    out.parent.mkdir(parents=True, exist_ok=True)
    base = Path(tempfile.mkdtemp(prefix="msvoz_"))
    tmp = base / "out"  # inemavox grava dub_work/ no diretório pai
    tmp.mkdir()

    if backend == "inemavox":
        vox = Path(c.get("INEMAVOX_DIR", "~/projetos/inemavox")).expanduser()
        py = vox / "venv/bin/python"
        cmd = [str(py if py.exists() else "python3"), "tts_direct.py", "--text", texto,
               "--lang", lang, "--engine", "chatterbox", "--outdir", str(tmp)]
        ref = c.get("INEMAVOX_REF")
        if ref and Path(ref).expanduser().exists():
            cmd += ["--ref", str(Path(ref).expanduser())]
        subprocess.run(cmd, cwd=vox, check=True)
        src = tmp / "generated.wav"

    elif backend == "edge":
        exe = shutil.which("edge-tts") or sys.exit("instale: pip install edge-tts")
        src = tmp / "voz.mp3"
        subprocess.run([exe, "--voice", c.get("EDGE_VOZ", "pt-BR-AntonioNeural"),
                        "--text", texto, "--write-media", str(src)], check=True)

    elif backend == "openai":
        key = exige(c, "OPENAI_API_KEY")
        src = tmp / "voz.mp3"
        src.write_bytes(post("https://api.openai.com/v1/audio/speech",
                             {"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                             {"model": c.get("OPENAI_TTS_MODELO", "gpt-4o-mini-tts"),
                              "voice": c.get("OPENAI_TTS_VOZ", "onyx"), "input": texto,
                              "response_format": "mp3"}))

    elif backend == "elevenlabs":
        key = exige(c, "ELEVENLABS_API_KEY")
        vid = exige(c, "ELEVENLABS_VOICE_ID")
        src = tmp / "voz.mp3"
        src.write_bytes(post(f"https://api.elevenlabs.io/v1/text-to-speech/{vid}",
                             {"xi-api-key": key, "Content-Type": "application/json",
                              "Accept": "audio/mpeg"},
                             {"text": texto,
                              "model_id": c.get("ELEVENLABS_MODELO", "eleven_multilingual_v2")}))
    else:
        sys.exit(f"MS_VOZ desconhecido: {backend} (use inemavox | edge | openai | elevenlabs)")

    if not src.exists() or src.stat().st_size == 0:
        sys.exit(f"backend {backend} não gerou áudio")
    converter(src, out)
    shutil.rmtree(base, ignore_errors=True)
    print(f"OK voz ({backend}) → {out}")


if __name__ == "__main__":
    main()
