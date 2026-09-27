# Publicar — legenda, hashtags e agendamento

## Legenda do post
- **Título = benefício** para quem assiste ("Como editar reels em 5 min com IA 🤯"), Title Case,
  sem CAPS LOCK, sem cara de texto genérico de IA ("Desvende o segredo revolucionário…" ✗).
- 1–2 linhas de contexto + **CTA de comentário**: `Comenta "IA" que eu te mando o link 👇`.
- **Não colar link** na legenda do Reels (não é clicável); o link vai pela DM (`funil-dm.md`) ou bio.

## Hashtags
- **3 a 5, nunca mais de 5** — o Instagram recusa o post acima disso (o `qa_short.py` barra).
- Específicas do tema (`#claudecode #automacao #ia`), variando de post para post.
- Nada de genéricas vazias (`#fyp`, `#viral`, `#free`).

## Rótulo de conteúdo de IA
Ligue o rótulo "feito com IA" da plataforma em todo short com avatar, voz clonada ou pessoa
sintética. Protege a conta contra derrubada/redução de alcance.

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

## Métrica
Uma vez por semana: `getAnalyticsDataByMetrics` → quais ganchos/temas performaram → fazer mais
daquilo. Anotar em `~/projetos/output/makeshorts/metricas.md` (tema, gancho, views, comentários).
