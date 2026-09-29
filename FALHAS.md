# FALHAS

| data | o que quebrou | menor correção | prompt \| infra |
|---|---|---|---|
| 2026-09-29 | `qa_short.py` aprovaria os reels reprovados pelo Nei: "gancho visual" só checava tela preta; medição com erro virava aviso/OK; `--caption` olhava o texto do post, não a legenda do vídeo; limite fixo de 59 s | Contrato `reel-profiles.json` (3 perfis); medição faltando = FALHA; fps/codec; `--srt` (≤3 palavras, sem sobreposição); avisos de frame 0 vazio e trecho parado; `--sheet`/`--report`; 11 testes | prompt |
| 2026-09-27 | `python baixar_v1.py` do inemavox → `python: command not found` | chamar `~/projetos/inemavox/venv/bin/python` (não existe `python` no PATH) | infra |
