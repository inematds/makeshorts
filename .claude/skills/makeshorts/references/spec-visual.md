# Especificação visual do short

Checklist de edição. O `qa_short.py` confere o que é mensurável (marcado com 🤖); o resto se confere
olhando frames.

## Formato
- 🤖 Vertical **1080x1920**, 30 fps, H.264 + AAC.
- 🤖 Duração **≤ 59 s** (ideal 25–45 s). Nunca termina no meio de uma frase.
- 🤖 Áudio normalizado em **-14 LUFS**, true peak ≤ -1 dBTP.

## Os primeiros 3 segundos
- 🤖 **Imagem desde o frame 0** — nada de tela preta, cinza ou logo parado.
- O primeiro frame vira a thumbnail do Shorts: escolha um frame forte (rosto + visual do tema).
- Visual do assunto já no gancho (site da ferramenta, resultado, print), nunca menu sem contexto.

## Layout (short com avatar ou fala)
- **Tela dividida**: visual do tema na metade de cima, rosto (avatar/pessoa) na metade de baixo.
- Quando o visual é detalhe (código, tela), **zoom** até dar para ler no celular; tela cheia se preciso.
- **Texto nunca na borda de baixo** (a interface da plataforma cobre). Zona segura: 10% em cima,
  20% embaixo, 6% nas laterais.
- **Nenhum texto sobre o rosto.**

## Ritmo
- Troca de visual a cada 2–4 s; cada troca com **punch-in curto + flash** leve.
- Cortar todo silêncio/ar morto e repetição.
- Zoom in/out sutil na fala para não ficar estático.
- SFX curtos (pop, whoosh) nas trocas. **Sem música de fundo** em short didático.

## Legendas
- 1–3 palavras por vez, surgindo palavra a palavra, sincronizadas com a fala.
- Fonte bold sem serifa, em **pílula escura** semi-transparente, palavra-chave em **âmbar `#F5A623`**.
- Contraste garantido em fundo claro (pílula resolve).

## B-roll
- Preferência: **material real** — site rolando, página do GitHub, demo oficial, GIF do produto.
- Mostrar a ferramenta **funcionando** vence card de texto.
- Imagem gerada (flux2-klein) só para preencher lacuna.

## CTA final
- Rosto visível no CTA (não tela preta), com a palavra do comentário escrita grande:
  **COMENTE "IA"**.

## Pedidos de ajuste que funcionam (em linguagem natural)
- "O gancho precisa de visual desde o primeiro frame."
- "A legenda some em fundo claro — reforça o contraste."
- "A segunda parte está mal recortada, centraliza no conteúdo."
- "Mostra a ferramenta funcionando em vez de card de texto."
- "Corta o respiro entre as frases e refaz o render."
