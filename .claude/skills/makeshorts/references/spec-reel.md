# Contrato de reel (< 2 min) — o que é bloqueante, o que é revisão

Fonte única, legível por código: [`reel-profiles.json`](reel-profiles.json). Lido por `scripts/qa_short.py`
e pelo explicavideos (`"reel_profile"` na config). Este arquivo só explica; **se discordar do JSON, vale o JSON.**

Origem: análise dos 5 vídeos reprovados em 28/09/2026 e revisão do Codex Astra
(`~/projetos/wifi/ANALISE-ERROS-VIDEOS-VIRAIS-2026-09-29.md`, `~/projetos/wifi/docs/revisao-astra-proposta-reels-2026-09-29.md`).

## Perfil = escolha editorial (não a proporção)

| Perfil | Duração (mín · ideal · máx) | Palavras | Estrutura |
|---|---|---|---|
| `divulgacao` | 15 · 20–35 · 59 s | 60–90 | gancho → prova → CTA |
| `tutorial` | 25 · 35–60 · 75 s | 90–150 | gancho → 3 passos → CTA |
| `mini-aula` | 45 · 60–110 · 119 s | 150–280 | gancho → loop aberto → 3–5 pontos (micro-gancho a cada ~20 s) → fecha o loop → CTA |

9:16 é só o formato. Um vídeo 9:16 de 3 min não é reel; um reel sempre é 9:16.

## Bloqueia (o QA reprova, sai 1)

- duração fora do mínimo/máximo do perfil;
- 1080×1920, 30 fps, H.264 + AAC;
- sem áudio; loudness fora de −14 ±1 LUFS;
- **qualquer medição que não pôde ser feita** (erro de ffmpeg nunca vira "OK");
- tela preta no início;
- legendas (`--srt`): cue com mais de 3 palavras; cues sobrepostos.

## Pede revisão (aviso — alguém olha e justifica)

- duração fora da faixa ideal; true peak > −1 dBTP;
- **frame 0 com pouca informação** (heurística de bordas: letra solta, fundo vazio). Rosto passa na heurística e ainda assim pode não ter gancho — por isso é revisão, não aprovação;
- **trechos parados > 4 s** (amostra 2 quadros/s; avatar falando não conta como mudança). Lista os intervalos;
- texto do post sem CTA reconhecido.

## O QA NÃO mede (revisão humana obrigatória antes de mostrar ao Nei)

1. **Gancho:** o frame 0 já diz a promessa/tensão em 3–6 palavras? Benefício ou problema claro até 2 s?
2. **Prova:** objeto real (site, curso, ferramenta rodando) aparece até 5 s? Imagem gerada **não** prova funcionamento.
3. **Pronúncia:** ouvir o áudio inteiro. Transcrição (ASR) ajuda a achar palavra sumida, não aprova pronúncia.
4. **Composição:** legenda sobre rosto ou sobre a prova; recorte do rosto nas transições.
5. **Teste do leitor:** alguém que não escreveu o roteiro assiste 1 vez e responde: o que ganho? qual foi a prova? qual o próximo passo? Três respostas certas ou volta.

## Regras editoriais (não medidas)

- **Uma promessa por reel.** Tema com 9 partes = série de 9 reels.
- **Mudança de conteúdo a cada 2–4 s** — corte, troca de cena, destaque, zoom com propósito. Brilho, estrela ou palavra colorida não contam. Efeito (flash, SFX) só com função narrativa, não em toda troca.
- **Voz humana ou do Nei.** Nunca voz estrangeira falando PT.
- **CTA único** por plataforma: Instagram "manda pra quem paga por isso" / "comente PALAVRA" (com o funil ligado); TikTok e Shorts "link na bio". O CTA do INEMA.CLUB conta como esse único CTA — não empilhar dois.
- **Datas e afirmações:** "2027" em vídeo de 2026 é projeção — dizer que é. Toda afirmação e número com fonte registrada.
- **3 ganchos escritos** por reel; variantes renderizadas só depois do formato aprovado.

## Pacote para o Nei (portão)

MP4 completo + folha de quadros (`--sheet`) + relatório (`--report`) + versão identificada. Zero falhas bloqueantes e
zero problema já conhecido enviado para ele descobrir. **Primeiro 1 protótipo; lote, publicação e envio só depois do ok.**
Aprovação de roteiro ≠ autorização de HeyGen ≠ autorização de publicar: três decisões separadas.

## Métricas depois de publicar

Comparar retenção inicial, conclusão e envios com o histórico **da mesma plataforma, faixa de duração e público**.
"70% no gancho" é hipótese de trabalho, não certificado.
