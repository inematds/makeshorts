#!/usr/bin/env python3
"""qa_short.py — portão de qualidade de um reel/short antes de mostrar ao Nei ou publicar.

Lê o contrato em references/reel-profiles.json (perfil: divulgacao | tutorial | mini-aula).
Só ffmpeg/ffprobe, local, sem API. O que ele mede (e o que NÃO mede) está em spec-reel.md.

BLOQUEIA (FALHA, sai 1):
  - duração acima do máximo do perfil / abaixo do mínimo
  - formato ≠ 1080x1920, fps ≠ 30, codec ≠ h264/aac
  - sem áudio; loudness fora de -14 ±1 LUFS
  - QUALQUER medição que não pôde ser feita (erro de ffmpeg vira falha, nunca "OK")
  - tela preta no início
  - legendas (--srt): cue com mais palavras que o perfil, ou cues sobrepostos
PEDE REVISÃO (AVISO, não bloqueia):
  - duração fora da faixa ideal; true peak > -1 dBTP
  - frame 0 com pouca informação (heurística de bordas: letra solta, fundo vazio)
  - trechos sem mudança visual acima de static_review_s (lista os intervalos)
  - texto do post (--post) sem CTA reconhecido ou com mais de 5 hashtags

NÃO mede: se o gancho é bom, se a prova é real, pronúncia, colisão de legenda com rosto.
Isso é revisão humana — use --sheet para gerar a folha de quadros.

Uso:
  python3 qa_short.py video.mp4 [--profile divulgacao] [--srt legendas.srt] [--post texto.txt]
                      [--sheet folha.png] [--json] [--report qa.json]
"""
import argparse, json, re, subprocess, sys
from pathlib import Path

PROFILES = Path(__file__).resolve().parent.parent / "references" / "reel-profiles.json"


class MeasureError(RuntimeError):
    pass


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def run_ok(cmd, what):
    r = run(cmd)
    if r.returncode != 0:
        raise MeasureError(f"{what}: {r.stderr.strip()[-300:] or 'exit ' + str(r.returncode)}")
    return r


def load_profile(name):
    data = json.loads(PROFILES.read_text(encoding="utf-8"))
    if name not in data["profiles"]:
        sys.exit(f"perfil desconhecido {name!r}; use: {', '.join(data['profiles'])}")
    return data["common"], data["profiles"][name], data["version"]


def probe(path):
    r = run_ok(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", path], "ffprobe")
    return json.loads(r.stdout)


def loudness(path):
    r = run_ok(["ffmpeg", "-nostats", "-hide_banner", "-i", path, "-af", "ebur128=peak=true", "-f", "null", "-"], "loudness")
    i = re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)
    tp = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", r.stderr)
    if not i:
        raise MeasureError("loudness: ffmpeg não devolveu a loudness integrada")
    return float(i[-1]), (float(tp[-1]) if tp else None)


def black_start(path):
    r = run_ok(["ffmpeg", "-hide_banner", "-t", "2", "-i", path, "-vf", "blackdetect=d=0.1:pix_th=0.10",
                "-an", "-f", "null", "-"], "blackdetect")
    m = re.search(r"black_start:(\d+\.?\d*) black_end:(\d+\.?\d*)", r.stderr)
    return float(m.group(2)) if m and float(m.group(1)) < 0.05 else 0.0


def frame0_information(path):
    """Fração de pixels de borda no frame 0 (270x480, cinza). Letra solta/fundo vazio ≈ < 0,02."""
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-frames:v", "1", "-vf", "scale=270:480,format=gray",
                        "-f", "rawvideo", "-"], capture_output=True)
    if r.returncode != 0 or len(r.stdout) != 270 * 480:
        raise MeasureError("frame 0: não foi possível decodificar")
    px, w, h, edges = r.stdout, 270, 480, 0
    for y in range(1, h - 1):
        row = y * w
        for x in range(1, w - 1):
            g = abs(px[row + x + 1] - px[row + x - 1]) + abs(px[row + w + x] - px[row - w + x])
            if g > 40:
                edges += 1
    return edges / ((w - 2) * (h - 2))


def band_changes(path, top_frac, fps=4, thr=15.0, merge_s=0.5):
    """Instantes em que a IMAGEM da faixa de cima troca (layout empilhado: topo = 704/1920).
    Limiar calibrado no C184 do promoavatar3: troca de imagem dá 19–142, pulso de brilho/zoom 4–5."""
    w, h = 90, max(8, round(160 * top_frac))
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf",
                        f"fps={fps},crop=iw:ih*{top_frac:.4f}:0:0,scale={w}:{h},format=gray", "-f", "rawvideo", "-"],
                       capture_output=True)
    if r.returncode != 0 or not r.stdout:
        raise MeasureError("faixa do topo: não foi possível decodificar")
    n = w * h
    frames = [r.stdout[i:i + n] for i in range(0, len(r.stdout) - n + 1, n)]
    ts = []
    for k in range(1, len(frames)):
        a, b = frames[k - 1], frames[k]
        if sum(abs(a[i] - b[i]) for i in range(n)) / n > thr and (not ts or k / fps - ts[-1] > merge_s):
            ts.append(k / fps)
    return ts


def static_gaps(path, dur, limit, fps=2, thr=6.0):
    """Intervalos sem mudança visual maiores que `limit` s. Amostra 2 quadros/s (90x160, cinza) e marca
    mudança quando a diferença média para a amostra anterior passa de `thr` (0–255). Pega fade e corte;
    fala do avatar (boca mexendo) fica abaixo do limiar."""
    w, h = 90, 160
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", f"fps={fps},scale={w}:{h},format=gray",
                        "-f", "rawvideo", "-"], capture_output=True)
    if r.returncode != 0 or not r.stdout:
        raise MeasureError("detecção de mudanças: não foi possível decodificar")
    n = w * h
    frames = [r.stdout[i:i + n] for i in range(0, len(r.stdout) - n + 1, n)]
    ts = [0.0]
    for k in range(1, len(frames)):
        a, b = frames[k - 1], frames[k]
        if sum(abs(a[i] - b[i]) for i in range(0, n, 3)) / (n / 3) > thr:
            ts.append(k / fps)
    ts.append(dur)
    return [(round(a, 1), round(b, 1)) for a, b in zip(ts, ts[1:]) if b - a > limit]


def parse_srt(path):
    def sec(t):
        h, m, s = t.replace(",", ".").split(":")
        return int(h) * 3600 + int(m) * 60 + float(s)
    cues, bad = [], []
    for block in re.split(r"\n\s*\n", Path(path).read_text(encoding="utf-8").strip()):
        lines = [l for l in block.splitlines() if l.strip()]
        m = next((re.match(r"(\S+)\s*-->\s*(\S+)", l) for l in lines if "-->" in l), None)
        try:
            a, b = sec(m.group(1)), sec(m.group(2))
        except (AttributeError, ValueError):
            bad.append(block.strip()[:40])        # bloco sem tempo legível: antes era ignorado em silêncio
            continue
        text = " ".join(l for l in lines[lines.index(m.string) + 1:])
        cues.append((a, b, text))
    return cues, bad


def parse_words(path):
    """Legenda palavra a palavra em JSON: lista de {start, dur|end, palavra|word} (formato do promoavatar3)."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("palavras") or data.get("words") or []
    out = []
    for w in data:
        ini = float(w["start"])
        fim = float(w["end"]) if "end" in w else ini + float(w["dur"])
        out.append((ini, fim, str(w.get("palavra", w.get("word", "")))))
    return out


def _read(fn, path):
    """Leitura de arquivo auxiliar: erro de leitura vira medição não feita (FALHA), nunca exceção sem relatório."""
    try:
        return fn(path)
    except (OSError, ValueError, KeyError, TypeError) as e:
        raise MeasureError(f"{Path(path).name}: {e}")


def contact_sheet(path, dur, out):
    times = sorted({0.0, min(2.0, dur), min(5.0, dur), dur / 2, max(0.0, dur - 1.0)})
    tmp = Path(out).with_suffix("")
    ins = []
    for k, t in enumerate(times):
        f = f"{tmp}-{k}.png"
        run_ok(["ffmpeg", "-nostdin", "-y", "-loglevel", "error", "-ss", f"{t:.2f}", "-i", path, "-frames:v", "1",
                "-vf", "scale=360:640", f], "folha de quadros")
        ins += ["-i", f]
    run_ok(["ffmpeg", "-nostdin", "-y", "-loglevel", "error", *ins, "-filter_complex", f"hstack=inputs={len(times)}", out],
           "folha de quadros")
    for k in range(len(times)):
        Path(f"{tmp}-{k}.png").unlink(missing_ok=True)
    return times


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--profile", default="divulgacao")
    ap.add_argument("--profiles", help="arquivo reel-profiles.json alternativo (o mesmo que o explicavideos usa)")
    ap.add_argument("--srt", help="legendas do vídeo (SRT) para conferir 1–3 palavras e sobreposição")
    ap.add_argument("--layout", choices=["empilhado"], help="empilhado: mede a troca de imagem na faixa de cima (0–704 px)")
    ap.add_argument("--words", help="legenda palavra a palavra em JSON (start + dur|end): reprova duração ≤ 0 e sobreposição")
    ap.add_argument("--post", "--caption", dest="post", help="texto do POST (legenda da rede), não a legenda do vídeo")
    ap.add_argument("--sheet", help="grava a folha de quadros (0 s, 2 s, 5 s, meio, fim)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--report", help="grava o relatório JSON neste arquivo")
    a = ap.parse_args()
    global PROFILES
    if a.profiles:
        PROFILES = Path(a.profiles)
    common, prof, version = load_profile(a.profile)

    res = []
    def add(st, item, det): res.append((st, item, det))
    def measure(item, fn):
        try:
            return fn()
        except MeasureError as e:
            add("FALHA", item, f"medição não feita — {e}")
            return None

    info = measure("ffprobe", lambda: probe(a.video))
    if info is None:
        return finish(a, res, prof, version)
    dur = float(info["format"].get("duration", 0))
    v = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
    au = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)

    d = prof["duration"]
    if dur > d["max"]:
        add("FALHA", "duração", f"{dur:.1f}s — máximo do perfil {a.profile} é {d['max']} s")
    elif dur < d["min"]:
        add("FALHA", "duração", f"{dur:.1f}s — mínimo do perfil {a.profile} é {d['min']} s")
    elif not d["ideal"][0] <= dur <= d["ideal"][1]:
        add("AVISO", "duração", f"{dur:.1f}s — ideal do perfil: {d['ideal'][0]}–{d['ideal'][1]} s")
    else:
        add("OK", "duração", f"{dur:.1f}s")

    cv = common["video"]
    if not v:
        add("FALHA", "vídeo", "sem trilha de vídeo")
    else:
        w, h = int(v["width"]), int(v["height"])
        add("OK" if (w, h) == (cv["width"], cv["height"]) else "FALHA", "formato", f"{w}x{h}")
        num, den = (v.get("r_frame_rate") or "0/1").split("/")
        fps = float(num) / float(den or 1)
        add("OK" if abs(fps - cv["fps"]) < 0.05 else "FALHA", "fps", f"{fps:.2f}")
        add("OK" if v.get("codec_name") == cv["codec"] else "FALHA", "codec vídeo", v.get("codec_name", "?"))

    ca = common["audio"]
    if not au:
        add("FALHA", "áudio", "sem trilha de áudio")
    else:
        add("OK" if au.get("codec_name") == cv["audio_codec"] else "FALHA", "codec áudio", au.get("codec_name", "?"))
        lt = measure("loudness", lambda: loudness(a.video))
        if lt:
            lufs, tp = lt
            ok = abs(lufs - ca["lufs"]) <= ca["lufs_tolerance"]
            add("OK" if ok else "FALHA", "loudness", f"{lufs:.1f} LUFS" + ("" if ok else
                f" — normalizar para {ca['lufs']} ±{ca['lufs_tolerance']} (ffmpeg -af loudnorm=I=-14:TP=-1.5:LRA=11)"))
            if tp is None:
                add("FALHA", "true peak", "não medido — medição obrigatória")
            elif tp > ca["true_peak_max"]:
                add("AVISO", "true peak", f"{tp:.1f} dBTP — manter ≤ {ca['true_peak_max']}")

    if v:
        b = measure("sem tela preta inicial", lambda: black_start(a.video))
        if b is not None:
            if b > common["opening"]["black_max_s"]:
                add("FALHA", "sem tela preta inicial", f"{b:.2f}s de preto no início")
            else:
                add("OK", "sem tela preta inicial", "imagem desde o frame 0")
        info0 = measure("frame 0", lambda: frame0_information(a.video))
        if info0 is not None:
            add("OK" if info0 >= 0.02 else "AVISO", "frame 0 (informação)",
                f"{info0:.3f} de bordas" + ("" if info0 >= 0.02 else " — pouco conteúdo: letra solta ou fundo vazio? revisar a capa"))
        gaps = measure("mudanças visuais", lambda: static_gaps(a.video, dur, common["rhythm"]["static_review_s"]))
        if gaps is not None:
            if gaps:
                add("AVISO", "trechos parados", f"{len(gaps)} acima de {common['rhythm']['static_review_s']} s: "
                    + ", ".join(f"{x}–{y}s" for x, y in gaps) + " — justificar ou quebrar")
            else:
                add("OK", "trechos parados", f"nenhum acima de {common['rhythm']['static_review_s']} s")

    if a.layout == "empilhado":
        lim = common["rhythm"].get("image_change_max_s", 3.5)
        ch = measure("troca de imagem (topo)", lambda: band_changes(a.video, 704 / 1920))
        if ch is not None:
            pts = [0.0] + ch + [dur]
            ints = [round(y - x, 1) for x, y in zip(pts, pts[1:])]
            longos = [(round(x, 1), round(y - x, 1)) for x, y in zip(pts, pts[1:]) if y - x > lim]
            med = sorted(ints)[len(ints) // 2]
            if longos:
                add("AVISO", "troca de imagem (topo)", f"mediana {med} s; {len(longos)} trechos acima de {lim} s: "
                    + ", ".join(f"{x}s (+{g}s)" for x, g in longos) + " — imagem nova a cada 2–3 s; pulso de brilho não conta")
            else:
                add("OK", "troca de imagem (topo)", f"{len(ch)} trocas, mediana {med} s")

    if a.srt:
        cues, bad = measure("legendas (leitura)", lambda: _read(parse_srt, a.srt)) or ([], ["ilegível"])
        inv = [c for c in cues if c[1] <= c[0] or c[0] < 0 or c[0] > dur + 0.5]   # fim ≤ início ou cue além do vídeo
        if bad or inv:
            add("FALHA", "legendas (estrutura)", f"{len(bad)} blocos sem tempo legível, {len(inv)} cues com fim ≤ início"
                + (f" — ex.: {inv[0][0]:.2f}→{inv[0][1]:.2f}s" if inv else ""))
        else:
            add("OK", "legendas (estrutura)", f"{len(cues)} cues")
        cues = sorted(cues)
        if not cues:
            add("FALHA", "legendas", "SRT vazio ou ilegível")
        else:
            mw = common["captions"]["max_words"]
            longas = [c for c in cues if len(c[2].split()) > mw]
            add("FALHA" if longas else "OK", "legendas (palavras)", f"{len(longas)} de {len(cues)} cues com mais de {mw} palavras"
                + (f" — ex.: “{longas[0][2]}”" if longas else ""))
            sobre = sum(1 for p, q in zip(cues, cues[1:]) if q[0] < p[1] - 0.01)
            add("FALHA" if sobre else "OK", "legendas (sobreposição)", f"{sobre} sobreposições")
            fim = cues[-1][1]
            if fim < dur - 3:
                add("AVISO", "legendas (cobertura)", f"última legenda termina em {fim:.1f}s de {dur:.1f}s")

    if a.words:
        ws = measure("palavras (leitura)", lambda: _read(parse_words, a.words))
        if ws is not None:
            neg = [w for w in ws if w[1] <= w[0]]
            ws = sorted(ws)
            sob = [(p, q) for p, q in zip(ws, ws[1:]) if q[0] < p[1] - 0.01]
            if not ws:
                add("FALHA", "palavras (tempo)", "nenhuma palavra no arquivo")
            elif neg or sob:
                ex = f"“{neg[0][2]}” {neg[0][0]:.2f}s dur {neg[0][1] - neg[0][0]:.2f}" if neg else f"“{sob[0][0][2]}”/“{sob[0][1][2]}”"
                add("FALHA", "palavras (tempo)", f"{len(neg)} com duração ≤ 0 (ficam presas na tela), {len(sob)} sobrepostas — ex.: {ex}")
            else:
                add("OK", "palavras (tempo)", f"{len(ws)} palavras, sem duração ≤ 0 nem sobreposição")

    if not a.srt and not getattr(a, "words", None):
        add("AVISO", "legendas", "não verificadas (passe --srt ou --words); reel sem legenda conferida não vai pro Nei")

    if a.post:
        txt = Path(a.post).read_text(encoding="utf-8")
        tags = re.findall(r"(?<!\w)#\w+", txt)
        if len(tags) > 5:
            add("AVISO", "post: hashtags", f"{len(tags)} — Instagram recusa post com mais de 5")
        low = txt.lower()
        kinds = [k for k in common["cta"]["kinds"] if k in low]
        add("OK" if kinds else "AVISO", "post: CTA", ", ".join(kinds) if kinds else "nenhum CTA reconhecido")

    if a.sheet:
        t = measure("folha de quadros", lambda: contact_sheet(a.video, dur, a.sheet))
        if t is not None:
            add("OK", "folha de quadros", f"{a.sheet} ({', '.join(f'{x:.1f}s' for x in t)})")

    return finish(a, res, prof, version)


def finish(a, res, prof, version):
    falhou = any(s == "FALHA" for s, _, _ in res)
    rep = {"ok": not falhou, "video": a.video, "profile": a.profile, "contract_version": version,
           "checks": [dict(status=s, item=i, detalhe=d) for s, i, d in res],
           "nao_medido": ["qualidade do gancho", "prova real", "pronúncia", "legenda sobre rosto"]}
    if a.report:
        Path(a.report).write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    if a.json:
        print(json.dumps(rep, ensure_ascii=False, indent=1))
    else:
        icon = {"OK": "✅", "AVISO": "⚠️ ", "FALHA": "❌"}
        for s, i, d in res:
            print(f"{icon[s]} {i:24} {d}")
        print(f"\nperfil {a.profile} · contrato {version}")
        print("RESULTADO:", "REPROVADO" if falhou else "APROVADO (falta a revisão humana: gancho, prova, pronúncia)")
    sys.exit(1 if falhou else 0)


if __name__ == "__main__":
    main()
