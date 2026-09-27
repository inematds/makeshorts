#!/usr/bin/env python3
"""qa_short.py — portão de qualidade de um short antes de publicar.

Checa, só com ffmpeg/ffprobe (local, sem API):
  - duração ≤ 59 s (ideal 25–45 s)
  - formato vertical 1080x1920 (9:16)
  - áudio presente, loudness integrada perto de -14 LUFS e true peak ≤ -1 dBTP
  - primeiro segundo sem tela preta (o gancho precisa de imagem desde o frame 0)
  - legenda (opcional, --caption arquivo.txt): ≤ 5 hashtags e um CTA "comente ..."

Uso:
  python3 scripts/qa_short.py video.mp4 [--caption legenda.txt] [--json]
Sai com 0 se tudo passou (avisos não reprovam), 1 se algum item FALHOU.
"""
import argparse, json, re, subprocess, sys


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def probe(path):
    r = run(["ffprobe", "-v", "error", "-print_format", "json",
             "-show_format", "-show_streams", path])
    if r.returncode != 0:
        sys.exit(f"ffprobe falhou: {r.stderr.strip()}")
    return json.loads(r.stdout)


def loudness(path):
    r = run(["ffmpeg", "-nostats", "-hide_banner", "-i", path,
             "-af", "ebur128=peak=true", "-f", "null", "-"])
    txt = r.stderr
    i = re.findall(r"I:\s+(-?[\d.]+) LUFS", txt)
    tp = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", txt)
    return (float(i[-1]) if i else None, float(tp[-1]) if tp else None)


def black_start(path):
    """Segundos de tela preta a partir do início (0 se não há)."""
    r = run(["ffmpeg", "-hide_banner", "-t", "2", "-i", path,
             "-vf", "blackdetect=d=0.1:pix_th=0.10", "-an", "-f", "null", "-"])
    m = re.search(r"black_start:(\d+\.?\d*) black_end:(\d+\.?\d*)", r.stderr)
    if m and float(m.group(1)) < 0.05:
        return float(m.group(2))
    return 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--caption", help="arquivo de texto com a legenda do post")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    res = []  # (status, item, detalhe)   status: OK | AVISO | FALHA
    def add(st, item, det): res.append((st, item, det))

    info = probe(a.video)
    dur = float(info["format"].get("duration", 0))
    v = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
    au = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)

    if dur > 59:
        add("FALHA", "duração", f"{dur:.1f}s — Shorts/Reels curtos devem ter ≤ 59 s")
    elif dur < 15 or dur > 45:
        add("AVISO", "duração", f"{dur:.1f}s — o ponto ideal é 25–45 s")
    else:
        add("OK", "duração", f"{dur:.1f}s")

    if not v:
        add("FALHA", "vídeo", "sem trilha de vídeo")
    else:
        w, h = int(v["width"]), int(v["height"])
        if (w, h) == (1080, 1920):
            add("OK", "formato", "1080x1920")
        elif h > w and abs(w / h - 9 / 16) < 0.01:
            add("AVISO", "formato", f"{w}x{h} — 9:16, mas o padrão é 1080x1920")
        else:
            add("FALHA", "formato", f"{w}x{h} — precisa ser vertical 9:16 (1080x1920)")

    if not au:
        add("FALHA", "áudio", "sem trilha de áudio")
    else:
        lufs, tp = loudness(a.video)
        if lufs is None:
            add("AVISO", "loudness", "não foi possível medir")
        elif abs(lufs - (-14)) <= 2:
            add("OK", "loudness", f"{lufs:.1f} LUFS")
        else:
            add("FALHA", "loudness", f"{lufs:.1f} LUFS — normalizar para -14 ±2 "
                "(ffmpeg -af loudnorm=I=-14:TP=-1.5:LRA=11)")
        if tp is not None and tp > -1:
            add("AVISO", "true peak", f"{tp:.1f} dBTP — manter ≤ -1")

    if v:
        b = black_start(a.video)
        if b > 0.3:
            add("FALHA", "gancho visual", f"{b:.2f}s de tela preta no início — imagem desde o frame 0")
        else:
            add("OK", "gancho visual", "sem tela preta no início")

    if a.caption:
        cap = open(a.caption, encoding="utf-8").read()
        tags = re.findall(r"(?<!\w)#\w+", cap)
        if len(tags) > 5:
            add("FALHA", "hashtags", f"{len(tags)} — Instagram recusa post com mais de 5")
        elif not tags:
            add("AVISO", "hashtags", "nenhuma — use 3 a 5 específicas")
        else:
            add("OK", "hashtags", f"{len(tags)}: {' '.join(tags)}")
        if re.search(r"\bcomente\b|\bcomment\b|\bcomenta\b", cap, re.I):
            add("OK", "CTA", "pede comentário com palavra-chave")
        else:
            add("AVISO", "CTA", "sem 'comente PALAVRA' — o funil de DM depende disso")

    falhou = any(s == "FALHA" for s, _, _ in res)
    if a.json:
        print(json.dumps({"ok": not falhou, "video": a.video,
                          "checks": [dict(status=s, item=i, detalhe=d) for s, i, d in res]},
                         ensure_ascii=False, indent=1))
    else:
        icon = {"OK": "✅", "AVISO": "⚠️ ", "FALHA": "❌"}
        for s, i, d in res:
            print(f"{icon[s]} {i:14} {d}")
        print("\nRESULTADO:", "REPROVADO" if falhou else "APROVADO")
    sys.exit(1 if falhou else 0)


if __name__ == "__main__":
    main()
