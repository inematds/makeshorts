"""Testes do portão qa_short.py com vídeos sintéticos (ffmpeg lavfi, local).
Rodar: python3 -m pytest tests/ -q   (ou python3 tests/test_qa_short.py)"""
import json, subprocess, sys, tempfile
from pathlib import Path

QA = Path(__file__).resolve().parents[1] / ".claude/skills/makeshorts/scripts/qa_short.py"
TMP = Path(tempfile.mkdtemp(prefix="qa-short-"))


def make(name, dur=25, size="1080x1920", fps=30, black=0.0, audio=True, loud=True, busy=True):
    out = TMP / f"{name}.mp4"
    # fundo com conteúdo (testsrc2 muda o tempo todo) ou cor lisa (parado, sem informação)
    src = f"testsrc2=size={size}:rate={fps}:d={dur}" if busy else f"color=c=0x0D1321:size={size}:rate={fps}:d={dur}"
    vf = f"drawbox=enable='lt(t,{black})':x=0:y=0:w=iw:h=ih:color=black:t=fill" if black else "null"
    cmd = ["ffmpeg", "-nostdin", "-y", "-loglevel", "error", "-f", "lavfi", "-i", src]
    if audio:
        cmd += ["-f", "lavfi", "-i", f"sine=frequency=440:duration={dur}"]
    cmd += ["-vf", vf, "-c:v", "libx264", "-pix_fmt", "yuv420p"]
    if audio:
        cmd += ["-af", "loudnorm=I=-14:TP=-1.5:LRA=11" if loud else "volume=-30dB", "-c:a", "aac", "-ar", "48000"]
    cmd += ["-shortest", str(out)]
    subprocess.run(cmd, check=True)
    return out


def qa(video, *extra):
    r = subprocess.run([sys.executable, str(QA), str(video), "--json", *extra], capture_output=True, text=True)
    rep = json.loads(r.stdout)
    return r.returncode, {c["item"]: c["status"] for c in rep["checks"]}


def srt(name, cues):
    p = TMP / f"{name}.srt"
    fmt = lambda s: f"00:00:{int(s):02d},{int(round((s % 1) * 1000)):03d}"
    p.write_text("\n\n".join(f"{i+1}\n{fmt(a)} --> {fmt(b)}\n{t}" for i, (a, b, t) in enumerate(cues)) + "\n")
    return p


def test_bom_passa():
    code, c = qa(make("bom"), "--srt", str(srt("ok", [(0, 1, "isso custa"), (1, 2, "zero reais")])))
    assert code == 0, c
    assert c["legendas (palavras)"] == "OK" and c["formato"] == "OK" and c["fps"] == "OK"


def test_longo_demais_falha():
    code, c = qa(make("longo", dur=65))
    assert code == 1 and c["duração"] == "FALHA"


def test_longo_ok_no_perfil_mini_aula():
    code, c = qa(make("longo2", dur=65), "--profile", "mini-aula")
    assert c["duração"] in ("OK", "AVISO") and code == 0, c


def test_horizontal_falha():
    code, c = qa(make("horiz", size="1920x1080"))
    assert code == 1 and c["formato"] == "FALHA"


def test_fps_errado_falha():
    code, c = qa(make("fps25", fps=25))
    assert code == 1 and c["fps"] == "FALHA"


def test_preto_no_inicio_falha():
    code, c = qa(make("preto", black=1.0))
    assert code == 1 and c["sem tela preta inicial"] == "FALHA"


def test_sem_audio_falha():
    code, c = qa(make("mudo", audio=False))
    assert code == 1 and c["áudio"] == "FALHA"


def test_baixo_volume_falha():
    code, c = qa(make("baixo", loud=False))
    assert code == 1 and c["loudness"] == "FALHA"


def test_legenda_longa_e_sobreposta_falham():
    code, c = qa(make("leg"), "--srt", str(srt("longa", [(0, 2, "uma frase inteira de legenda"), (1.5, 3, "sobreposta")])))
    assert code == 1 and c["legendas (palavras)"] == "FALHA" and c["legendas (sobreposição)"] == "FALHA"


def test_fundo_liso_parado_pede_revisao():
    code, c = qa(make("liso", busy=False))
    assert c["frame 0 (informação)"] == "AVISO" and c["trechos parados"] == "AVISO"


def test_arquivo_invalido_falha_nao_passa():
    bad = TMP / "quebrado.mp4"
    bad.write_bytes(b"isto nao e um mp4")
    code, c = qa(bad)
    assert code == 1 and c.get("ffprobe") == "FALHA"


if __name__ == "__main__":
    fails = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            try:
                fn(); print("ok  ", name)
            except AssertionError as e:
                fails += 1; print("FAIL", name, e)
    sys.exit(1 if fails else 0)
