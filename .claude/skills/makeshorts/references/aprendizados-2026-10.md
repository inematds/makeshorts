# Aprendizados até 01/10/2026 — de onde vêm as regras desta skill

Força da fonte: **[medido]** dado com amostra · **[oficial]** declaração da plataforma (às vezes via imprensa) ·
**[blog]** blog de ferramenta/marketing (fraco) · **[Nei]** avaliação do dono · **[local]** medido aqui.
Relatórios completos: `~/projetos/wifi/RELATORIO-CAPACIDADE-VIDEO-VIRAL-2026-10-01.md` e
`~/projetos/wifi/MELHORIAS-VIRAIS-2026-10-01.md`.

## O que aconteceu em cada projeto

- **inema-areas-viral (28/09)** — skill errada (`video-explicativo`), sem rosto, voz `rachel` inglesa falando PT,
  9 assuntos por vídeo, sem legenda, sem imagem, ~7,5 s por cena. [Nei] "nem estagiária faria algo tão ruim".
  → Regras: rosto/voz do Nei, uma ideia por short, legenda, prova real, protótipo antes de lote.
- **Lote Claude Fable (30/09, `output/virais-nei-2026-09-30`)** — melhor gramática viral [Nei: "o Claude foi
  melhor"], mas "imagem junto com avatar ficou muito irreal, exagerada" [Nei]. [local] cena Kling parada
  ~25 s no V4; V1 e V5 com a mesma capa; V2 dizia "ninguém dublou nada" e foi dublado; V3 imitava telejornal.
  → Regras: cena crível e mesmo mundo, troca a cada 2–3 s, bastidores verdadeiros, nada de notícia simulada,
  `qa_lote.py`.
- **Lote Codex Astra (30/09, `istoreal-gpt/delivery`)** — ensinou mais (uma regra prática por vídeo) e rotulou a
  IA o tempo todo, mas 720p (reprovado no QA), abertura no close do rosto, sem CTA do INEMA.
  → Regras: "regra prática" no passo zero, rótulo "cena criada com IA", CTA obrigatório.
- **promoavatar3** — [Nei] "tem bom resultado"; publicação manual. Layout empilhado (topo imagem+manchete, meio
  avatar+legenda, base painel) e prompts com passo zero e oficina de gancho → importados aqui.
  [local] 803 de 1.966 reels (41%) com palavra de duração ≤ 0 (legenda presa — `legendas.py:113`); imagem
  troca a cada ~6,3 s (mediana); 57% dos `alc` > 40 s; só fotos geradas. → Portão `--words`; troca 2–3 s;
  1 prova real em cada 3 visuais.
- **explicavideos** — conteúdo mais útil (aulas reais, avatar do Nei); modo reel corrigido na 2.4.5 (QA por bloco,
  recibo com impressão, strict exigido). Motor padrão para divulgação INEMA.

## Medido com as ferramentas novas (1.2.0, 01/10/2026)
- [local] C184 do promoavatar3: imagem do topo parada 9,0 s, 5,5 s, **16,2 s** e 9,5 s (`--layout empilhado`);
  áudio a **−20,5 LUFS** (plataformas normalizam em ~−14: toca baixo); depois do `legendas_palavras.py`, 0 palavras
  com duração ≤ 0 e SRT de 43 cues com ≤ 3 palavras.
- [local] 36 roteiros do C184 (`qa_roteiro.py`): 5 com gancho > 9 palavras; "A IA pode ser igual à de todo
  mundo" repetida em **9 roteiros** (risco de template repetitivo); os aprovados têm 111–134 palavras (45–53 s) →
  contrato 1.2.0 com divulgação ideal 20–50 s / 60–125 palavras.
- [local] O backend local `inemavox` só dá tempo por frase; legenda palavra a palavra local hoje só pelo explicavideos.

## O que as redes premiam em 2026

- "AI slop" saturou: ~60% do que o TikTok mostra a contas novas é slop [medido, Kapwing/TNW 21/06/2026,
  definição do fornecedor]; TikTok permite pedir menos IA no feed [oficial, TechCrunch 18/11/2025]; Mosseri:
  "o estético polido e perfeito morreu" [oficial via blogs, 31/12/2025].
- YouTube rebaixa conteúdo inautêntico/repetitivo/de template [oficial, TechCrunch 20/07/2026].
- Instagram: 5 hashtags no máximo desde 18/12/2025, legenda + comentário [oficial via Later/Metricool];
  envios pesam mais que curtidas [blog citando Mosseri]; **skip rate** nos primeiros 3 s virou métrica oficial
  em 08/2025 [oficial via imprensa]; Trial Reels para teste com não seguidores [blog].
- Avatar realista não perde retenção em conteúdo informativo [estudos USF/UCL via blog], mas a confiança cai
  quando a IA aparece onde se espera humano ou parece artificial [CHI 2026, acadêmico].
- Rosto: mediana 1,9× maior que sem rosto [medido, ContentLabs 7.431 vídeos, 26/04/2026].
- Criadores de educação em IA (Riley Brown, Kevin Stratvert, SetupsAI) usam **tela real/demonstração** como
  visual principal [perfil, não verificado vídeo a vídeo]. Criadores BR ainda não verificados.
- Ritmo de fala ~150 palavras/min; gancho de uma frase em 1–3 s; loop no fim; reengajar em ~25% e ~65%;
  legenda palavra a palavra; safe zone 900×1400 [todos blog — convenção de ofício, não medição].
- Duração: 35–50 s com retenção alta [blog]; o que conta é % assistido.

## Lacunas abertas
- Formato real de 5–8 criadores BR de IA (baixar últimos Reels/Shorts pelo inemavox e medir gancho, 1º corte, CTA).
- Regra exata do Instagram para avatar clonado do próprio criador.
- Métrica própria: nenhum projeto tem dado de retenção ainda — calibrar tudo isso depois de 10–20 shorts.
