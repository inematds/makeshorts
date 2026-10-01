#!/usr/bin/env python3
"""Portão do LOTE (makeshorts 1.1.0): acusa vídeos do mesmo lote que abrem com o mesmo quadro 0.

Por quê: o quadro 0 vira a capa no Shorts e o YouTube rebaixa conteúdo repetitivo/de template
(política de "inauthentic content", esclarecida em 07/2026). No lote Claude de 30/09/2026 o V1 e o V5
abriram iguais (diferença 6,3; capas distintas ~56). É AVISO (sai 0): alguém olha e troca a capa ou justifica.
Medição que falha (arquivo ilegível) sai 1.

Uso: qa_lote.py v1.mp4 v2.mp4 ... [--limiar 15] [--json]
"""
import argparse, itertools, json, subprocess, sys
from pathlib import Path

W, H = 36, 64   # quadro 0 reduzido, em cinza


def frame0(path):
    r = subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-i", str(path), "-frames:v", "1",
                        "-vf", f"scale={W}:{H},format=gray", "-f", "rawvideo", "-"], capture_output=True)
    if r.returncode or len(r.stdout) != W * H:
        raise RuntimeError(f"{path}: não foi possível ler o quadro 0")
    return r.stdout


def rotulo(v):
    p = Path(v)
    return f"{p.parent.name}/{p.name}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("videos", nargs="+")
    ap.add_argument("--limiar", type=float, default=15.0, help="diferença média (0–255) abaixo da qual é 'mesma capa'")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    try:
        f0 = {v: frame0(v) for v in a.videos}
    except RuntimeError as e:
        print(json.dumps({"ok": False, "erro": str(e)}) if a.json else f"❌ {e}")
        sys.exit(1)
    rep = []
    for x, y in itertools.combinations(a.videos, 2):
        d = sum(abs(p - q) for p, q in zip(f0[x], f0[y])) / (W * H)
        if d < a.limiar:
            rep.append({"a": rotulo(x), "b": rotulo(y), "diferenca": round(d, 2)})
    out = {"ok": True, "videos": len(a.videos), "repetidos": rep}
    if a.json:
        print(json.dumps(out, ensure_ascii=False))
    else:
        for r in rep:
            print(f"⚠️  mesma capa: {r['a']} × {r['b']} (diferença {r['diferenca']}) — trocar o quadro 0 ou justificar")
        print(f"{len(a.videos)} vídeos, {len(rep)} pares com o quadro 0 repetido")
    sys.exit(0)


if __name__ == "__main__":
    main()
