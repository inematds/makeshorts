# Especificação visual do short

Checklist de edição. O `qa_short.py` confere o que é mensurável (🤖); o resto se confere olhando frames.
Porquês e fontes: [`aprendizados-2026-10.md`](aprendizados-2026-10.md).

## Formato
- 🤖 Vertical **1080×1920, 30 fps, H.264 + AAC** (bloqueante).
- 🤖 Duração **pelo perfil** (`reel-profiles.json`). Nunca termina no meio de uma frase.
- 🤖 Áudio **−14 ±1 LUFS**, true peak ≤ −1 dBTP. Concat por cópia não normaliza: normalize o arquivo final.

## Layout padrão — o empilhado aprovado (promoavatar3, `templates/empilhado-capa.json`)

O Nei aprova este layout nos reels do promoavatar3; use-o como padrão para "avatar + imagem/prova".

| Faixa | Altura (px) | Conteúdo |
|---|---|---|
| **Topo** | 0–704 | prova ou imagem do tema; manchete 76 px peso 900, caixa alta, 2 linhas ≤ 5 palavras, 2ª linha em âmbar `#F5A623`, a 56 px do pé da faixa |
| **Meio** | 704–1312 | avatar/rosto (`object-fit: cover`), dono do áudio; legenda palavra a palavra 86 px, Montserrat Black, contorno preto 8 px, 28 px acima da base da faixa |
| **Base** | 1312–1920 | painel com a frase-resumo 66 px peso 800, palavra-chave em âmbar — **ou** a prova (print/tela) quando o topo é a imagem; não deixar 600 px de fundo vazio |

Variantes do mesmo template: **díptico** (imagem e avatar com 960 px cada) e **imagem-plena** (prova em
tela cheia, avatar em PiP no canto superior direito) — esta é a melhor para gravação de tela.
Fundo `#0E1116`, texto `#FFF`, acento `#F5A623`.

## Os primeiros 3 segundos
- 🤖 **Imagem desde o quadro 0** — nada de tela preta (bloqueia) nem quadro vazio/letra solta (aviso).
- **O quadro 0 é a capa completa**: manchete do gancho (3–6 palavras) + visual do tema, nada "surgindo do vazio".
- 🤖 (lote) **Capas diferentes entre os vídeos do lote** — `scripts/qa_lote.py` avisa quadro 0 repetido.
- **Teste da imagem 1** (promoavatar3, `prompts/reel-regras.md:15-39`): *transferência* (dá para entender o
  tema só pela imagem?), *polegar* (pararia o dedo?), *tensão* (há algo em jogo?).

## Cena crível, mesmo mundo (lição do lote de 30/09/2026)
O Nei achou "irreal, exagerado" o lote com cena de IA impossível em cima e avatar embaixo. Regras:
- **Cena cotidiana e plausível**: mesa, celular, planilha, padaria normal, escritório real. A surpresa vem da
  ideia, não do efeito. **Proibido**: onda gigante, objeto falando, entrevista de rua ou telejornal simulado
  ("AO VIVO", logo de emissora), qualquer coisa que pareça notícia real.
- **Mesmo mundo**: avatar e cena com luz e tom parecidos; não empilhar uma cena cinematográfica azul/laranja
  sobre o rosto num fundo real de outra luz.
- **Clichês proibidos** (promoavatar3): holograma, HUD, matrix, cérebro de circuitos, robô apertando mão,
  lâmpada, texto dentro da imagem gerada.
- **Rótulo discreto "cena criada com IA"** sobre toda cena gerada realista (o lote do Codex fez assim; o
  TikTok exige rótulo em IA realista).

## Prova e b-roll
- **Pelo menos 1 em cada 3 visuais é material real**: site rolando, página do curso no inema.club, terminal
  rodando, GitHub, antes/depois. Imagem gerada **ilustra, não prova**.
- No divulgação, a prova aparece **até 5 s**.
- Imagem gerada: flux2-klein local, seed por público/alvo (`--seed-key`, como o `gen-imagem.py` do
  promoavatar3) para não repetir a mesma foto em vídeos diferentes.

## Ritmo
- 🤖 Mudança de **conteúdo** a cada 2–4 s; o QA avisa trecho parado > 4 s. **Imagem nova a cada 2–3 s** —
  um pulso de brilho, flash ou zoom sobre a mesma imagem não conta como troca (o promoavatar3 segura imagens
  ~6 s com pulso; não copiar).
- Reengajar perto de 25% e 65% do vídeo com troca de visual ou de ângulo.
- Cortar silêncio, respiro longo e repetição.
- **SFX**: só para marcar uma ação ou revelação, não em toda troca. **Sem música de fundo** em short didático.

## Legendas
- 🤖 1–3 palavras por vez (`--srt`), sem cues sobrepostos nem invertidos; 🤖 com `--words`, nenhuma palavra
  com duração ≤ 0 (fica presa na tela — bug achado em 41% dos reels do promoavatar3).
- Estilo aprovado: **Montserrat Black com contorno preto 8 px**, palavra-chave em âmbar, ≥ 64 px
  (86 px no layout empilhado). **`@font-face` obrigatório** no HTML — sem ele o render cai calado numa fonte
  genérica (promoavatar3 `docs/legenda.md:55-62`).
- Palavras ordenadas por início antes de calcular durações; duração mínima ~0,08 s cortada no início da próxima.
- **Nenhum texto sobre o rosto.**

## Zona segura (1080×1920)
- Universal: tudo que importa dentro de **900×1400 centrados**. Margens de referência [blog, 2026]: TikTok
  topo 108 · base 320 · direita 120; Shorts topo e base 380 · direita 120. Use o maior valor de cada lado.
- Texto nunca na faixa de baixo nem na coluna direita (botões da plataforma).

## CTA final
- Rosto visível no CTA (não cartela preta sozinha), com a ação escrita grande:
  **"manda pra quem…"**, **"link na bio"** ou **COMENTE "IA"** (só com o funil ligado).
- Cartela inema.club de até 3 s depois do CTA falado é aceita (padrão do promoavatar3).

## Pedidos de ajuste que funcionam
- "O gancho precisa de visual desde o primeiro quadro."
- "Troca a imagem a cada 2–3 s; o pulso não vale como troca."
- "Mostra o curso aberto no inema.club em vez da foto gerada."
- "A cena está em outro mundo — iguala a luz com o avatar ou troca por uma cena cotidiana."
- "Corta o respiro entre as frases e refaz o render."
