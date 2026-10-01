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


# --- 1.1.0 (01/10/2026): legenda palavra a palavra (JSON do promoavatar3), SRT malformado, lote ---

def palavras(name, words):
    p = TMP / f"{name}.json"
    p.write_text(json.dumps([{"start": s, "dur": d, "palavra": w} for s, d, w in words]))
    return p


def test_palavras_ok_passam():
    code, c = qa(make("pal-ok"), "--words", str(palavras("ok", [(0.0, 0.4, "ISSO"), (0.4, 0.5, "CUSTA"), (0.9, 0.6, "ZERO")])))
    assert code == 0 and c["palavras (tempo)"] == "OK", c


def test_palavra_com_duracao_negativa_falha():
    # o bug do promoavatar3 (legendas.py:113): ASR fora de ordem → dur negativa → palavra presa na tela
    code, c = qa(make("pal-neg"), "--words", str(palavras("neg", [(24.7, -0.06, "APARECER"), (24.64, 0.3, "SEU")])))
    assert code == 1 and c["palavras (tempo)"] == "FALHA", c


def test_palavras_sobrepostas_falham():
    code, c = qa(make("pal-sob"), "--words", str(palavras("sob", [(0.0, 1.0, "UMA"), (0.5, 0.4, "DUAS")])))
    assert code == 1 and c["palavras (tempo)"] == "FALHA", c


def test_srt_invertido_ou_malformado_falha():
    p = TMP / "invertido.srt"
    p.write_text("1\n00:00:02,000 --> 00:00:01,000\nvolta\n\n2\nsem tempo nenhum\ntexto\n")
    code, c = qa(make("srt-inv"), "--srt", str(p))
    assert code == 1 and c["legendas (estrutura)"] == "FALHA", c


LOTE = Path(__file__).resolve().parents[1] / ".claude/skills/makeshorts/scripts/qa_lote.py"


def lote(*videos):
    r = subprocess.run([sys.executable, str(LOTE), "--json", *map(str, videos)], capture_output=True, text=True)
    return r.returncode, json.loads(r.stdout)


def test_lote_acusa_frame0_repetido():
    a, b = make("lote-a"), make("lote-b")          # mesmo testsrc2 → frame 0 idêntico
    code, rep = lote(a, b)
    assert code == 0 and rep["repetidos"], rep    # aviso, não reprova


def test_lote_sem_repeticao():
    a, b = make("lote-c"), make("lote-d", busy=False)
    code, rep = lote(a, b)
    assert code == 0 and not rep["repetidos"], rep


# --- 1.2.0: faixa do topo (layout empilhado), legendas_palavras.py, qa_roteiro.py ---

SCRIPTS = Path(__file__).resolve().parents[1] / ".claude/skills/makeshorts/scripts"


def cores(name, cores_, seg):
    """Vídeo 1080x1920 trocando de cor a cada `seg` s (simula imagem nova no topo)."""
    out = TMP / f"{name}.mp4"
    ins, fil = [], ""
    for i, c in enumerate(cores_):
        ins += ["-f", "lavfi", "-i", f"color=c={c}:size=1080x1920:rate=30:d={seg}"]
        fil += f"[{i}:v]"
    dur = seg * len(cores_)
    cmd = ["ffmpeg", "-nostdin", "-y", "-loglevel", "error", *ins, "-f", "lavfi", "-i", f"sine=frequency=440:duration={dur}",
           "-filter_complex", fil + f"concat=n={len(cores_)}:v=1:a=0[v]", "-map", "[v]", "-map", f"{len(cores_)}:a",
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-ar", "48000",
           "-shortest", str(out)]
    subprocess.run(cmd, check=True)
    return out


def test_topo_trocando_a_cada_2s_passa():
    code, c = qa(cores("topo-ok", ["red", "white", "black", "yellow", "navy", "silver", "maroon", "lime"], 2), "--layout", "empilhado")
    assert c["troca de imagem (topo)"] == "OK", c


def test_topo_parado_pede_revisao():
    code, c = qa(cores("topo-parado", ["red", "white", "black"], 6), "--layout", "empilhado")
    assert c["troca de imagem (topo)"] == "AVISO", c


def test_legendas_palavras_corrige_duracao_negativa():
    src = palavras("bruto", [(24.7, -0.06, "APARECER"), (24.64, 0.3, "SEU"), (25.0, 0.4, "AGENTE")])
    out = TMP / "corrigido.json"
    srt_out = TMP / "corrigido.srt"
    r = subprocess.run([sys.executable, str(SCRIPTS / "legendas_palavras.py"), str(src), "--out", str(out), "--srt", str(srt_out)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    ws = json.loads(out.read_text())
    assert [w["palavra"] for w in ws] == ["SEU", "APARECER", "AGENTE"]       # ordenado por início
    assert all(w["dur"] > 0 for w in ws)
    assert all(a["start"] + a["dur"] <= b["start"] + 1e-6 for a, b in zip(ws, ws[1:]))
    code, c = qa(make("pal-corr"), "--words", str(out), "--srt", str(srt_out))
    assert c["palavras (tempo)"] == "OK" and c["legendas (estrutura)"] == "OK" and c["legendas (palavras)"] == "OK", c


def roteiro(name, fala):
    p = TMP / f"{name}.md"
    p.write_text(f"Tipo: pro\n\n### FALA\n{fala}\n\n### SOBREPOSIÇÕES\nATENÇÃO: x\n")
    return p


def qr(*args):
    r = subprocess.run([sys.executable, str(SCRIPTS / "qa_roteiro.py"), "--json", *map(str, args)], capture_output=True, text=True)
    rep = json.loads(r.stdout)
    return r.returncode, rep


BOM = ("Você paga por algo que já é grátis. "
       "O curso de agentes do INEMA é aberto, sem cadastro, direto no navegador. "
       "Em três passos: abre o inema.club, escolhe a trilha de agentes e faz a primeira aula hoje. "
       "Cada aula tem exemplo pronto pra copiar e testar no seu trabalho. "
       "Quem faz a primeira aula hoje sai sabendo montar um agente simples que responde e-mail. "
       "Manda pra quem ainda paga por isso.")


def test_roteiro_bom_passa():
    code, rep = qr(roteiro("r-bom", BOM), "--keyword", "agentes")
    itens = {c["item"]: c["status"] for c in rep["arquivos"][0]["checks"]}
    assert code == 0, rep
    assert itens["gancho (palavras)"] == "OK" and itens["palavra-chave no início"] == "OK"


def test_roteiro_gancho_longo_e_abertura_proibida_falham():
    code, rep = qr(roteiro("r-ruim", "Olá pessoal, neste vídeo eu vou mostrar uma coisa muito interessante sobre inteligência artificial. " + BOM))
    itens = {c["item"]: c["status"] for c in rep["arquivos"][0]["checks"]}
    assert code == 1 and itens["gancho (palavras)"] == "FALHA" and itens["abertura proibida"] == "FALHA"


def test_roteiro_depoimento_e_bastidor_pedem_revisao():
    code, rep = qr(roteiro("r-dep", "Pare de pagar agência. Ontem eu testei e ninguém dublou nada. " + BOM))
    itens = {c["item"]: c["status"] for c in rep["arquivos"][0]["checks"]}
    assert itens["depoimento/bastidor"] == "AVISO", itens


def test_roteiro_palavra_chave_tardia_falha():
    code, rep = qr(roteiro("r-kw", BOM), "--keyword", "trilha")
    itens = {c["item"]: c["status"] for c in rep["arquivos"][0]["checks"]}
    assert code == 1 and itens["palavra-chave no início"] == "FALHA"


def test_lote_de_roteiros_acusa_frase_repetida():
    a = roteiro("r-a", BOM)
    b = roteiro("r-b", "Pare de testar ferramenta toda semana. " + BOM)
    code, rep = qr(a, b)
    assert rep["frases_repetidas"], rep


def test_legendas_palavras_recusa_transcricao_so_com_frases():
    p = TMP / "segmentos.json"
    p.write_text(json.dumps([{"start": 0, "end": 2, "text": "frase inteira sem palavras"}]))
    r = subprocess.run([sys.executable, str(SCRIPTS / "legendas_palavras.py"), str(p), "--out", str(TMP / "x.json")],
                       capture_output=True, text=True)
    assert r.returncode != 0 and "sem tempo por palavra" in r.stderr
