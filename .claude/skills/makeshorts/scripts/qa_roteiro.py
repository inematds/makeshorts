#!/usr/bin/env python3
"""Portão do ROTEIRO (makeshorts 1.2.0) — roda antes de gastar render ou crédito de avatar.

Lê a fala de cada arquivo (seção `### FALA` — mesmo formato do promoavatar3; sem a seção, o texto inteiro menos
títulos) e confere o que é mecânico nas regras de `references/roteiro.md`:

FALHA (sai 1): gancho com mais de 9 palavras · abertura proibida ("olá", "você sabia", "neste vídeo"…) ·
               palavra-chave (--keyword) fora das primeiras ~15 palavras (≈ 5 s a 150 palavras/min).
AVISO:         palavras fora da faixa do perfil · depoimento/bastidor que precisa de fonte ("ontem eu testei",
               "ninguém dublou", "custou zero"…) · "fica até o fim" · nenhum CTA ou mais de um tipo de CTA.
LOTE:          frase (≥ 6 palavras) repetida em 2+ arquivos → aviso de "template repetitivo" (YouTube).

Não mede: se o gancho passa no teste da lacuna, se a tese toma lado, se os fatos têm fonte. Isso é do humano.

Uso: qa_roteiro.py v1.md [v2.md ...] [--profile divulgacao] [--keyword agentes] [--json]
"""
import argparse, json, re, sys, unicodedata
from collections import defaultdict
from pathlib import Path

CONTRACT = Path(__file__).resolve().parents[1] / "references" / "reel-profiles.json"
HOOK_MAX = 9
KEYWORD_WINDOW = 15
OPENERS = ["ola", "oi pessoal", "fala pessoal", "voce sabia", "neste video", "nesse video", "hoje eu vou", "hoje vou te mostrar",
           "bem-vindo", "bem vindo", "e ai pessoal"]
SOURCE_NEEDED = ["ontem eu testei", "eu testei", "um aluno me", "uma aluna me", "aconteceu comigo", "um cliente me",
                 "ninguem dublou", "custou zero", "custou nada", "sem encostar no teclado", "fui dormir", "eu nao fiz nada",
                 "levou dois minutos", "em dois minutos"]
BAIT = ["fica ate o fim", "assista ate o final", "ate o final do video"]
CTA = {"envio": ["manda pra", "manda para", "envia pra", "envie para", "compartilha"],
       "comentario": ["comenta", "comente", "escreve nos comentarios", "escreva nos comentarios"],
       "link": ["link na bio", "inema.club", "acesse", "entra no"],
       "salvar": ["salva esse", "salve esse", "salva este", "salve este"]}


def norm(t):
    t = unicodedata.normalize("NFKD", t.lower())
    return "".join(c for c in t if not unicodedata.combining(c))


def fala_of(text):
    m = re.search(r"^#{2,4}\s*FALA\s*$(.*?)(?=^#{1,4}\s|\Z)", text, re.S | re.M | re.I)
    body = m.group(1) if m else "\n".join(l for l in text.splitlines() if not l.lstrip().startswith("#"))
    return body.strip()


def words_of(t):
    return re.findall(r"[\wÀ-ÿ'’.-]+", t)


def sentences(t):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", t.replace("\n", " ")) if s.strip()]


def check(path, prof, keyword):
    res = []
    add = lambda st, item, det: res.append({"status": st, "item": item, "detalhe": det})
    fala = fala_of(Path(path).read_text(encoding="utf-8"))
    ws = words_of(fala)
    if not ws:
        add("FALHA", "fala", "sem texto de fala (use a seção ### FALA)")
        return res, fala
    lo, hi = prof["words"]
    add("OK" if lo <= len(ws) <= hi else "AVISO", "palavras (perfil)", f"{len(ws)} palavras — perfil {lo}–{hi}")
    first = sentences(fala)[0]
    n = len(words_of(first))
    add("OK" if n <= HOOK_MAX else "FALHA", "gancho (palavras)", f"{n} palavras: “{first[:80]}” (máx. {HOOK_MAX})")
    nf = norm(fala)
    op = [o for o in OPENERS if nf.startswith(o)]
    add("FALHA" if op else "OK", "abertura proibida", f"começa com “{op[0]}”" if op else "nenhuma")
    if keyword:
        early = norm(" ".join(ws[:KEYWORD_WINDOW]))
        ok = norm(keyword) in early
        add("OK" if ok else "FALHA", "palavra-chave no início",
            f"“{keyword}” {'nas' if ok else 'fora das'} primeiras {KEYWORD_WINDOW} palavras (≈ 5 s)")
    hits = [p for p in SOURCE_NEEDED if p in nf]
    add("AVISO" if hits else "OK", "depoimento/bastidor",
        ("precisa de fonte ou é falso: " + ", ".join(f"“{h}”" for h in hits) + " — cena em 2ª pessoa, bastidor só o que aconteceu")
        if hits else "nada a conferir")
    bait = [b for b in BAIT if b in nf]
    if bait:
        add("AVISO", "retenção forçada", f"“{bait[0]}” — troque por loop aberto")
    fim = norm(" ".join(sentences(fala)[-2:]))
    kinds = [k for k, pats in CTA.items() if any(p in fim for p in pats)]
    add("OK" if len(kinds) == 1 else "AVISO", "CTA no fim",
        f"tipo: {kinds[0]}" if len(kinds) == 1 else (f"{len(kinds)} tipos ({', '.join(kinds)}) — um só" if kinds else "nenhum CTA nas 2 últimas frases"))
    return res, fala


def repeated(falas, min_words=6):
    seen = defaultdict(set)
    for name, fala in falas.items():
        for s in sentences(fala):
            key = " ".join(words_of(norm(s)))
            if len(key.split()) >= min_words:
                seen[key].add(name)
    return [{"frase": k, "arquivos": sorted(v)} for k, v in seen.items() if len(v) > 1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("roteiros", nargs="+")
    ap.add_argument("--profile", default="divulgacao")
    ap.add_argument("--keyword", help="palavra-chave do tema (dita até ~5 s)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    profiles = json.loads(CONTRACT.read_text(encoding="utf-8"))["profiles"]
    if a.profile not in profiles:
        sys.exit(f"perfil desconhecido {a.profile!r}; use: {', '.join(profiles)}")
    arquivos, falas = [], {}
    for p in a.roteiros:
        try:
            res, fala = check(p, profiles[a.profile], a.keyword)
        except OSError as e:
            res, fala = [{"status": "FALHA", "item": "leitura", "detalhe": str(e)}], ""
        arquivos.append({"arquivo": p, "checks": res})
        falas[Path(p).name] = fala
    rep = repeated(falas) if len(falas) > 1 else []
    falhou = any(c["status"] == "FALHA" for f in arquivos for c in f["checks"])
    out = {"ok": not falhou, "profile": a.profile, "arquivos": arquivos, "frases_repetidas": rep}
    if a.json:
        print(json.dumps(out, ensure_ascii=False, indent=1))
    else:
        icon = {"OK": "✅", "AVISO": "⚠️ ", "FALHA": "❌"}
        for f in arquivos:
            print(f"\n{f['arquivo']}")
            for c in f["checks"]:
                print(f"  {icon[c['status']]} {c['item']:24} {c['detalhe']}")
        for r in rep:
            print(f"\n⚠️  frase repetida em {len(r['arquivos'])} roteiros ({', '.join(r['arquivos'])}): “{r['frase'][:90]}”")
        print("\nRESULTADO:", "REPROVADO" if falhou else "APROVADO (falta: teste da lacuna, tese, fontes — revisão humana)")
    sys.exit(1 if falhou else 0)


if __name__ == "__main__":
    main()
