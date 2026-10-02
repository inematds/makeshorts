#!/usr/bin/env python3
"""transcreve.py — transcrição com tempo por palavra (para legendas) no backend de MS_TRANSCRICAO.

  python3 scripts/transcreve.py --in narracao.wav --outdir ws/transcricao [--backend groq]

Backends:
  inemavox  Whisper large-v3 local (GPU)     — padrão na máquina INEMA
  groq      Whisper na Groq (pago, barato)   — exige GROQ_API_KEY — recomendado para VPS
  openai    Whisper da OpenAI (pago)         — exige OPENAI_API_KEY
Saída: <outdir>/transcript.json (segmentos + palavras quando o backend fornece) e transcript.txt
"""
import argparse, json, subprocess, sys, tempfile, uuid, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _config import cfg, exige


def multipart(url, key, arquivo, campos):
    b = uuid.uuid4().hex
    corpo = b""
    for k, v in campos:
        corpo += f"--{b}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode()
    corpo += (f"--{b}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{arquivo.name}\"\r\n"
              "Content-Type: application/octet-stream\r\n\r\n").encode() + arquivo.read_bytes() + b"\r\n"
    corpo += f"--{b}--\r\n".encode()
    req = urllib.request.Request(url, data=corpo, method="POST", headers={
        "Authorization": f"Bearer {key}", "Content-Type": f"multipart/form-data; boundary={b}"})
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.loads(r.read())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="entrada", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--backend", help="sobrepõe MS_TRANSCRICAO")
    a = ap.parse_args()

    c = cfg()
    backend = a.backend or c.get("MS_TRANSCRICAO", "inemavox")
    ent = Path(a.entrada).expanduser().resolve()
    out = Path(a.outdir).expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)

    if backend == "inemavox":
        vox = Path(c.get("INEMAVOX_DIR", "~/projetos/inemavox")).expanduser()
        py = vox / "venv/bin/python"
        subprocess.run([str(py if py.exists() else "python3"), "transcrever_v1.py", "--in", str(ent),
                        "--outdir", str(out), "--whisper-model", "large-v3", "--words"], cwd=vox, check=True)
        print(f"OK transcrição (inemavox) → {out}")
        return

    # APIs: enviar só o áudio (mp3 mono 64k) para caber no limite de upload
    tmp = Path(tempfile.mkdtemp(prefix="mstr_")) / "audio.mp3"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(ent), "-vn", "-ac", "1", "-b:a", "64k",
                    str(tmp)], check=True)
    campos = [("response_format", "verbose_json"), ("timestamp_granularities[]", "word"),
              ("timestamp_granularities[]", "segment"), ("language", c.get("MS_VOZ_IDIOMA", "pt"))]
    if backend == "groq":
        key = exige(c, "GROQ_API_KEY")
        r = multipart("https://api.groq.com/openai/v1/audio/transcriptions", key, tmp,
                      campos + [("model", c.get("GROQ_WHISPER_MODELO", "whisper-large-v3-turbo"))])
    elif backend == "openai":
        key = exige(c, "OPENAI_API_KEY")
        r = multipart("https://api.openai.com/v1/audio/transcriptions", key, tmp,
                      campos + [("model", c.get("OPENAI_WHISPER_MODELO", "whisper-1"))])
    else:
        sys.exit(f"MS_TRANSCRICAO desconhecido: {backend} (use inemavox | groq | openai)")

    (out / "transcript.json").write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    (out / "transcript.txt").write_text(r.get("text", ""), encoding="utf-8")
    print(f"OK transcrição ({backend}) → {out}")


if __name__ == "__main__":
    main()
