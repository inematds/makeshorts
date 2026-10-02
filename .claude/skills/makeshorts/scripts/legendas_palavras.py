#!/usr/bin/env python3
"""Normaliza a legenda palavra a palavra (JSON) e, opcional, gera o SRT de 1–3 palavras.

Corrige o bug achado em 01/10/2026 no promoavatar3 (`scripts/legendas.py:113`, 41% dos reels): a duração era
"início da próxima − início desta"; quando o ASR devolve palavras fora de ordem ou com o mesmo início, ela
fica ≤ 0 e a palavra nunca sai da tela (no C184, "APARECER" ficou presa e as seguintes foram desenhadas por cima).

Regra: ordena por início; cada palavra começa em max(início, fim da anterior) e dura até o início da próxima,
com mínimo de MIN_S (empurrando a próxima um pouco se for preciso). Nunca duração ≤ 0, nunca sobreposição.
Aceita lista de {start, dur|end, palavra|word, ...} ou {"palavras"|"words": [...]}; preserva os outros campos
(ex.: "kw") e devolve no mesmo esquema da entrada.

Uso: legendas_palavras.py legendas.json --out legendas.json [--srt legendas.srt] [--max-words 3] [--max-chars 22]
"""
import argparse, json, sys
from pathlib import Path

MIN_S = 0.08
TAIL_S = 0.15


def load(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    wrap = None
    if isinstance(data, dict):
        wrap = "palavras" if "palavras" in data else "words"
        data, outer = data.get(wrap) or [], data
    else:
        outer = None
    # segmentos com palavras dentro (Whisper verbose): achata
    if data and isinstance(data[0], dict) and "words" in data[0] and not ("palavra" in data[0] or "word" in data[0]):
        data, wrap, outer = [w for seg in data for w in seg.get("words") or []], None, None
    if data and not any(k in data[0] for k in ("palavra", "word")):
        raise ValueError("sem tempo por palavra (só segmentos/frases — o inemavox exporta assim). "
                         "Rode de novo: transcreve.py (inemavox com --words) ou transcrever_v1.py --words")
    return data, wrap, outer


def normalize(words):
    items = []
    for i, w in enumerate(words):
        ini = float(w["start"])
        fim = float(w["end"]) if "end" in w else ini + float(w.get("dur", 0))
        items.append((ini, i, fim, w))
    items.sort(key=lambda x: (x[0], x[1]))          # estável: mesmo início mantém a ordem original
    out, prev_end = [], 0.0
    for k, (ini, _, fim, w) in enumerate(items):
        t = max(ini, prev_end)
        if k + 1 < len(items):
            end = max(items[k + 1][0], t + MIN_S)
        else:
            end = max(fim, t + MIN_S) + TAIL_S
        prev_end = end
        nw = dict(w)
        nw["start"] = round(t, 3)
        if "end" in w:
            nw["end"] = round(end, 3)
        else:
            nw["dur"] = round(end - t, 3)
        out.append(nw)
    return out


def text_of(w):
    return str(w.get("palavra", w.get("word", ""))).strip()


def end_of(w):
    return w["end"] if "end" in w else w["start"] + w["dur"]


def to_srt(words, max_words=3, max_chars=22, gap_s=0.35):
    """Agrupa em cues de 1–max_words palavras; quebra em pausa > gap_s, pontuação final ou excesso de caracteres."""
    def stamp(t):
        n = round(t * 1000)
        return f"{n // 3600000:02d}:{n // 60000 % 60:02d}:{n // 1000 % 60:02d},{n % 1000:03d}"
    cues, cur = [], []
    for w in words:
        if cur:
            txt = " ".join(text_of(x) for x in cur + [w])
            pausa = w["start"] - end_of(cur[-1]) > gap_s
            if len(cur) >= max_words or len(txt) > max_chars or pausa or text_of(cur[-1])[-1:] in ".!?":
                cues.append(cur)
                cur = []
        cur.append(w)
    if cur:
        cues.append(cur)
    blocks = []
    for i, c in enumerate(cues):
        a = c[0]["start"]
        z = min(end_of(c[-1]), cues[i + 1][0]["start"]) if i + 1 < len(cues) else end_of(c[-1])
        blocks.append(f"{i + 1}\n{stamp(a)} --> {stamp(max(z, a + MIN_S))}\n" + " ".join(text_of(x) for x in c) + "\n")
    return "\n".join(blocks)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("entrada")
    ap.add_argument("--out", required=True, help="JSON normalizado (pode ser o mesmo arquivo)")
    ap.add_argument("--srt", help="grava também o SRT de 1–3 palavras")
    ap.add_argument("--max-words", type=int, default=3)
    ap.add_argument("--max-chars", type=int, default=22)
    a = ap.parse_args()
    try:
        words, wrap, outer = load(a.entrada)
        fixed = normalize(words)
    except (OSError, ValueError, KeyError, TypeError) as e:
        sys.exit(f"erro lendo {a.entrada}: {e}")
    antes = sum(1 for w in words if (float(w["end"]) if "end" in w else float(w["start"]) + float(w.get("dur", 0))) <= float(w["start"]))
    payload = fixed if wrap is None else {**outer, wrap: fixed}
    Path(a.out).write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    if a.srt:
        Path(a.srt).write_text(to_srt(fixed, a.max_words, a.max_chars), encoding="utf-8")
    print(f"{len(fixed)} palavras; {antes} tinham duração ≤ 0 — corrigidas → {a.out}" + (f" + {a.srt}" if a.srt else ""))


if __name__ == "__main__":
    main()
