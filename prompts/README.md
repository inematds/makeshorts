# Prompts prontos (para usar sem a skill)

Cole no Claude Code aberto na pasta do vídeo. Com a skill instalada, basta `/makeshorts` —
estes prompts são a versão "à mão" de cada etapa.

## 1. Roteiro — 3 versões

```
Tema: <título ou link>
Material de apoio: <transcrição/notas, opcional>

Pesquise o tema na fonte oficial (site, GitHub, documentação) e liste 3–5 fatos verificados com a URL.
Depois escreva 3 versões de roteiro de short (~75 palavras, ~30 s), cada uma em 3 parágrafos:
1) gancho de até 3 s; 2) gancho secundário que cria curiosidade ("não é X, nem Y");
3) entrega em 3 passos simples. Termine com: Comenta "<PALAVRA>" que eu te mando o link.
Linguagem simples (criança de 9 anos), uma ideia só, tom de novidade, sem parecer anúncio.
Para cada versão: título do post com benefício, Title Case, até 40 caracteres.
Diga qual você gravaria e por quê.
```

## 2. Editar um clipe gravado (humano ou avatar)

```
Edite o vídeo <arquivo> num short vertical 1080x1920 no estilo Reels:
- corte silêncios e repetições; zoom in/out sutil na fala
- legendas de 1–3 palavras surgindo palavra a palavra, pílula escura, palavra-chave em âmbar
- animações e diagramas sobre o que estou falando, visual desde o primeiro frame
- punch-in + flash curto em cada troca, SFX leves (pop/whoosh), sem música
- texto fora da borda de baixo e nunca sobre o rosto; áudio em -14 LUFS
Transcreva primeiro, entenda o assunto, depois edite. Ao final, escreva a legenda do post com
CTA de comentário e 3–5 hashtags específicas. Rode o QA antes de me entregar.
```

## 3. Short 100% IA (sem gravar)

```
Faça um short de 30 s sobre <TEMA + link oficial>.
1. Roteiro na fórmula gancho → gancho secundário → 3 passos → CTA, só com fatos checados.
2. Narração com scripts/voz.py (backend do .env) — ou avatar HeyGen se eu confirmar o custo.
3. Enquanto isso, capture o site e o GitHub com rolagem suave e junte demos/GIFs oficiais.
4. Monte 1080x1920: visual na metade de cima desde o frame 0, rosto/avatar embaixo,
   legendas palavra a palavra, punch-in + flash por troca, SFX leves.
5. Corte ar morto, normalize para -14 LUFS, cheque texto sobre rosto, rode o QA e me mostre.
```

## 4. Ajustes (depois do primeiro render)

```
O gancho precisa de visual desde o primeiro frame. A legenda some em fundo claro.
A segunda parte está mal recortada. Mostre a ferramenta funcionando em vez de card de texto.
Corrija e renderize de novo.
```

## 5. Publicar

```
Agende este short via Metricool no Instagram, TikTok, YouTube Shorts e Facebook,
no melhor horário de cada rede. Legenda com benefício + CTA de comentário, no máximo 5 hashtags.
Ative o rótulo de IA. Me mostre tudo antes de confirmar.
```

## 6. Lote da semana

```
Ache 5 ferramentas de IA gratuitas em alta esta semana (GitHub trending e notícias).
Para cada uma, faça um short com o processo do prompt 3 e agende um por dia às 18h.
Me mostre os 5 roteiros antes de gerar qualquer mídia.
```
