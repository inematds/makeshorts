# Publicar — legenda, hashtags e agendamento

## Legenda do post
- **Título = benefício** para quem assiste ("Como editar reels em 5 min com IA 🤯"), Title Case,
  sem CAPS LOCK, sem cara de texto genérico de IA ("Desvende o segredo revolucionário…" ✗).
- **Palavra-chave do tema na 1ª linha** (a mesma dita até 5 s e escrita na tela): Instagram e TikTok indexam
  legenda, fala e texto na tela, e o Mosseri diz que palavra-chave na legenda pesa mais que hashtag.
- 1–2 linhas de contexto + **um CTA**: `Manda pra quem paga por isso` (envios são o sinal mais forte no
  Instagram), `link na bio`, ou `Comenta "IA"…` **só se o funil de DM estiver ligado**.
- **Não colar link** na legenda do Reels (não é clicável); o link vai pela DM (`funil-dm.md`) ou bio.

## Hashtags
- **3 a 5, nunca mais de 5** — desde 18/12/2025 o Instagram limita a 5 por post, **somando legenda e
  primeiro comentário** (o `qa_short.py` barra na legenda).
- Específicas do tema (`#claudecode #automacao #ia`), variando de post para post.
- Nada de genéricas vazias (`#fyp`, `#viral`, `#free`).

## Rótulo de conteúdo de IA
Ligue o rótulo "feito com IA" da plataforma em todo short com avatar, voz clonada ou cena gerada realista.
- **TikTok:** rótulo obrigatório em IA realista (C2PA; o usuário pode pedir "menos IA" no feed).
- **Instagram:** "AI info" no post. Desde 05/2026 contas com *persona* de IA sem rótulo de perfil ficam "não
  recomendáveis"; o Nei é **criador humano usando avatar como ferramenta** — rotular o post, não o perfil
  (regra exata para avatar clonado ainda não confirmada: na dúvida, rotular).
- **YouTube:** "conteúdo alterado ou sintético" ao enviar. A política de conteúdo inautêntico (07/2025,
  esclarecida em 07/2026) rebaixa template repetitivo: variar capa, layout e ângulo entre vídeos.
- **Nunca** cena que simule notícia, entrevista de rua ou depoimento real.

## Agendar via Metricool (MCP)
Ferramentas disponíveis na sessão (carregar via ToolSearch antes de usar):

| Ferramenta | Para quê |
|---|---|
| `mcp__metricool__getBrandSettings` | quais redes estão ligadas na marca |
| `mcp__metricool__getBestTimeToPostByNetwork` | melhor horário por rede |
| `mcp__metricool__createScheduledPost` | agenda o post (vídeo + legenda + redes + data/hora) |
| `mcp__metricool__createScheduledPostForReview` | cria para aprovação humana antes de sair |
| `mcp__metricool__getScheduledPosts` | conferir o que já está na fila |
| `mcp__metricool__getAnalyticsDataByMetrics` | views/engajamento depois de publicado |

Fluxo:
1. `getBrandSettings` → confirmar redes (Instagram, TikTok, YouTube, Facebook…).
2. `getBestTimeToPostByNetwork` → sugerir horário.
3. **Mostrar ao usuário** vídeo + legenda + redes + horário e **esperar o "pode publicar"**
   (publicar é chamada de API externa — regra dura).
4. Preferir `createScheduledPostForReview` na primeira vez; `createScheduledPost` quando o fluxo
   estiver aprovado.
5. Lote: um por dia no mesmo horário (ex.: 18h), ou espaçados 3 h no mesmo dia no YouTube Shorts.

## Teste A/B de gancho — Trial Reels (Instagram)
Conta profissional com 200+ seguidores: o Trial Reel vai só para não seguidores, em ondas, por ~72 h, e
pode ser compartilhado com os seguidores se performar. Teste **2 ganchos do mesmo roteiro** (uma variável por
vez). Ganchos alternativos só são renderizados depois do formato aprovado pelo Nei.

## Frequência [blog, 2026]
Shorts: 1/dia em canal novo, 1–3/dia em canal estabelecido (mais de ~5/dia parece spam). TikTok 3–5/semana.

## Métrica
Os números que decidem (calibrar com o histórico próprio depois de 10–20 shorts; metas são de blog):
- **Instagram — skip rate** (% que pulou nos primeiros 3 s, métrica oficial desde 08/2025): < 20% forte, 20–30% ok.
- **YouTube — viewed vs swiped away**: > 70% ótimo, ~50% média, < 30% o short morre.
- % médio assistido e curva de retenção (queda entre 3 s e o meio).
- **Envios/compartilhamentos** e salvamentos; cliques para o inema.club.

Uma vez por semana: `getAnalyticsDataByMetrics` → quais ganchos/temas performaram → fazer mais
daquilo. Anotar em `~/projetos/output/makeshorts/metricas.md` (tema, gancho, views, comentários).
