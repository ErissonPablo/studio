# Nível 2: edição avançada com a Magnific

No Nível 2, além de montar a edição, o Claude **gera imagens e vídeos com IA** na [Magnific](https://www.magnific.com) (antiga Freepik): B-rolls cinematográficos, ilustrações animadas, metáforas visuais, transformações de cena. A montagem continua no **Remotion**, no seu computador, igual ao [Nível 1](2-nivel-1-remotion.md). Na prática, é o Nível 1 com assets gerados por IA.

**Custo:** usa **créditos da sua conta Magnific** (plano pago). Nada é gerado sem você aprovar o plano e o custo estimado. A montagem não custa nada.
**Quando vale a pena:** vídeos em que imagens geradas (B-roll, metáforas, cenas realistas) fazem diferença. Se o vídeo é mais tutorial e print, o [Nível 1](2-nivel-1-remotion.md) resolve de graça.

> **Plano necessário.** O conector aceita qualquer conta, mas no plano Free o catálogo bloqueia a geração de vídeo e quase todos os modelos de imagem: eles aparecem como `requiresPremium`. Para o Nível 2 você precisa do **Premium** ou de um plano superior.

---

## 1. Conectar a Magnific ao Claude

Existem dois caminhos. **Escolha o A se puder**: ele dá acesso a todas as ferramentas do Nível 2, inclusive a estimativa de custo antes de gerar.

### Caminho A: entrar com a sua conta Magnific (recomendado)

É o conector oficial (MCP), em `https://mcp.magnific.com`. A autenticação é feita com login na sua conta (OAuth); não existe chave para copiar. Os créditos saem do mesmo saldo que você usa no site.

**No Claude Desktop (ou em claude.ai):**

1. Abra **Personalizar → Conectores** (em algumas versões, **Configurações → Conectores**).
2. Clique em **Adicionar conector** e escolha **Adicionar conector personalizado**.
3. Nome: `Magnific`. URL: `https://mcp.magnific.com`.
4. Clique em **Conectar** e faça login na sua conta Magnific na janela que abrir.

Atalho que já abre o formulário preenchido:
[claude.ai/customize/connectors?modal=add-custom-connector…](https://claude.ai/customize/connectors?modal=add-custom-connector&connectorName=Magnific&connectorUrl=https%3A%2F%2Fmcp.magnific.com)

Conectores adicionados na sua conta do Claude aparecem também nas sessões **Code** do Claude Desktop e no Claude Code do terminal, desde que você esteja logado na mesma conta.

**No Claude Code pelo terminal (alternativa):**

```bash
claude mcp add --transport http --scope user magnific https://mcp.magnific.com
```

Na primeira chamada, o Claude Code abre o login no navegador. Se não abrir, digite `/mcp`, selecione `magnific` e autentique.

**Como saber se funcionou:** peça ao Claude "consulta meu saldo na Magnific". Ele deve responder com o seu plano e os seus créditos.

### Caminho B: API key da Magnific

> **Importante:** o conector (Caminho A) **não usa API key**. A API REST da Magnific é um produto separado, com chave própria. Neste caminho o Claude não usa o conector: ele chama a API pelo script `tools/magnific_api.py`.

O que muda:

- dá para **gerar imagens e vídeos** normalmente, com os modelos da API;
- **não** há estimativa de custo antes de gerar (`simulate_cost` só existe no conector). O Claude estima pela tabela de preços da Magnific e você aprova do mesmo jeito;
- toda chamada à API consome créditos da organização, mesmo em planos "ilimitados", porque o ilimitado vale só no site.

Passo a passo:

1. Confira em [magnific.com/api](https://www.magnific.com/api) se o seu plano inclui acesso à API.
2. Entre com o e-mail de **administrador** da conta e crie a chave em [magnific.com/user/organization/api-keys](https://www.magnific.com/user/organization/api-keys).
3. Guarde a chave numa **variável de ambiente** do seu usuário (nunca num arquivo do repositório):
   - **Windows (PowerShell):**
     ```powershell
     [Environment]::SetEnvironmentVariable("MAGNIFIC_API_KEY", "SUA-API-KEY", "User")
     ```
   - **macOS / Linux:** adicione ao `~/.zshrc` ou `~/.bashrc`:
     ```bash
     export MAGNIFIC_API_KEY="SUA-API-KEY"
     ```
4. Feche e abra de novo o Claude (Desktop ou terminal) para ele enxergar a variável.
5. Teste pedindo: "gera uma imagem de teste na Magnific pelo caminho B".

O Claude usa:

```bash
python tools/magnific_api.py <endpoint> '<argumentos em JSON>' "projetos/<NNN. nome>/magnific"
```

O `<endpoint>` é o caminho do modelo na API, como `text-to-image/seedream-v5-pro` ou `video/kling-v3-pro`. Os campos aceitos por cada modelo estão na página dele em [docs.magnific.com](https://docs.magnific.com) (o índice completo fica em `docs.magnific.com/llms.txt`). Os links de resultado expiram em 30 minutos, por isso o script já baixa tudo assim que a geração termina.

---

## 2. O que você entrega e recebe

Igual ao Nível 1: vídeo **já cortado** em `video/`, **prints** em `prints/` (fotos de pessoas citadas, notícias, logos, miniaturas) e suas **orientações**, incluindo um **orçamento de créditos** se quiser limitar o gasto.

Você recebe o MP4 final em `edicoes/<NNN. nome>/<nome>_final.mp4`. Os assets gerados ficam em `projetos/<NNN. nome>/magnific/`.

---

## 3. O processo (Caminho A)

### 1. Organizar
Mesma organização do Nível 1: pasta `projetos/<NNN. nome>/`, `ffprobe` no vídeo e `edicoes/<NNN. nome>/`. Os assets gerados vão para `projetos/<NNN. nome>/magnific/`.

### 2. Assistir e transcrever
Mesmo processo do Nível 1: quadros com a skill `watch` em `frames/` e tempo por palavra com `tools/transcrever.py` em `transcricao/`.

### 3. Planejar (ponto de aprovação)
O `plano.md` segue a [direção editorial](5-direcao-editorial.md) e acrescenta:

- lista de assets a gerar, com modelo e **custo estimado em créditos**, calculado com `simulate_cost` (só estima, nunca cobra);
- margem de refação;
- custo total, comparado com o saldo de `account_balance`.

Veja a estrutura de um plano real em [projetos/000. exemplo/plano.md](../projetos/000.%20exemplo/plano.md). Ele foi feito no projeto original, com outra plataforma: os nomes de modelos e os custos não valem para a Magnific.

**Nenhum crédito é gasto antes da sua aprovação.** Se o gasto passar ~20% do estimado, o Claude para e avisa.

### 4. Gerar os assets
- Consulta o saldo (`account_balance`) antes de começar.
- Escolhe os modelos em `images_models_list` e `video_models_list`, preferindo os que têm `agentRecommendation`, e copia o `slug` exatamente como aparece.
- **Imagens primeiro**, com `images_generate`: até 8 variações do mesmo prompt numa única chamada (`count`), já no formato certo (`aspectRatio` `9:16` ou `16:9`). Espera o resultado com `creations_wait`, monta uma prancha de conferência e refaz o que não se lê.
- Fotos e prints seus que servem de referência sobem com `creations_request_upload` → upload do arquivo → `creations_finalize_upload`. O identificador volta e entra em `references`.
- Objeto isolado: `images_remove_background` (PNG transparente) ou um modelo que aceite `transparentBackground`.
- **Depois anima**, com `video_generate`, um vídeo por chamada: a imagem aprovada entra em `keyframes.start` e, para transformações, outra em `keyframes.end` (quando o modelo aceitar). Com `slug`, a `duration` é obrigatória. Use `withSoundEffects: false` quando o modelo permitir: o áudio do vídeo é o seu. Aprova pelo quadro do meio e pelo do fim.
- **Baixa** para `magnific/` com nomes descritivos (`03_broll_ampulheta.mp4`): `creations_get` dá a `url` em resolução cheia e `creations_register_download` registra o download antes de salvar. Se precisar de um formato de editor (H.264, ProRes), use `creations_deliver`, que é grátis.
- **Imagens e vídeos gerados não levam texto.** Todo texto entra na montagem.

### 5. Montar no Remotion
Segue o [Nível 1](2-nivel-1-remotion.md#4-programar-as-cenas) a partir da fase 4: o código fica em `src/videos/<slug>/` e os assets entram com `staticFile('<NNN. nome>/magnific/03_broll_ampulheta.mp4')`.

- O vídeo gravado continua sendo uma única instância contínua na base, com o áudio original.
- **Todo vídeo gerado entra mudo.** O único áudio da edição é o do master.
- B-roll em tela cheia cobre a câmera enquanto você continua falando; os gatilhos são os segundos exatos do `palavras.json`.
- Conferência com stills no início, no meio e no fim de cada troca de layout: rosto coberto, legibilidade, borda preta no zoom, sincronia.

Se algo não ficar bom com os modelos disponíveis, o Claude diz isso e propõe alternativa: outro modelo, uma cena desenhada no Remotion ou um print.

### 6. Validar e entregar
- `ffprobe`: resolução, fps, duração igual à do vídeo gravado, uma trilha de áudio.
- `ffmpeg -af volumedetect` no final e no original: volumes iguais.
- Caminho do arquivo, duração, resolução, codecs e **créditos gastos** (saldo de `account_balance` antes e depois).

## 4. O processo (Caminho B)

Fases 1 a 3 iguais, com uma diferença: sem `simulate_cost`, o custo estimado vem da tabela de preços da Magnific. Na fase 4, os assets são gerados com `tools/magnific_api.py` e salvos em `magnific/`. As fases 5 e 6 são iguais às do Caminho A.

---

## 5. Modelos de referência (Caminho A)

| Uso | Modelo (`slug` no conector) | Observação |
|---|---|---|
| Ilustração 16:9 ou 9:16 | Seedream 5 Pro (`seedream-5-pro`), 2k | modelo padrão recomendado pela Magnific; até 8 variações por chamada |
| Primeiro rascunho só com texto | Recraft V4.1 (`recraft-v4-1`) | rápido, bom para explorar ideias |
| Variação da mesma cena | `seedream-5-pro` + `references` com `type: image` e o identificador da geração | ex.: mesa cheia → mesa vazia |
| Objeto isolado | GPT 2 (`gpt-2`) com `transparentBackground: true`, ou qualquer modelo + `images_remove_background` | PNG com fundo transparente |
| Imagem → vídeo padrão | Kling 3.0 (`kling-30`) ou Kling 3.0 Turbo (`kling-30-turbo`) | `keyframes.start`; `keyframes.end` para transformação |
| Imagem → vídeo "herói" | Seedance 2.0 Pro (`bytedance-seedance-pro-2.0`), `resolution: "1080p"` | cenas principais; recusa o pedido sem `resolution` |
| Cena realista | Veo 3.1 (`google-veo3_1` ou `google-veo3_1-fast`) | texto → vídeo, sem pessoas identificáveis |

- Os slugs são do catálogo de outubro de 2026. Modelos entram e saem: o Claude confere `images_models_list` e `video_models_list` antes de cada projeto.
- **Os custos mudam** com o modelo, a resolução e a duração. O Claude sempre calcula com `simulate_cost`, passando exatamente os argumentos que vai usar, e mostra o número no plano.
- Diagramas, fluxos, chips e textos são construídos no Remotion (0 crédito). A Magnific gera ilustrações, objetos e B-rolls.

## 6. Estilos e prompts base

A galeria em [estilos/](../estilos/README.md) mostra três estilos feitos no Nível 2 do projeto original: **papel recortado** (B-roll), **papel creme em aula** e **cinematográfico escuro**. Os prompts abaixo não dependem de plataforma e funcionam na Magnific. São modelos, não obrigação: descreva o estilo que quiser ou traga imagens de referência em `prints/`.

### Papel recortado (preset do projeto original)

Tokens de cor: papel `#F0EEE6`, papel claro `#FAF9F5`, tinta `#141413`, tinta suave `#3D3929`, cinza `#6B675C`, borda `#E3DED2`, terracota `#D97757`, terracota escuro `#B5532F`, sálvia `#788C5D`, vermelho `#C0453A`.
Tipografia (Google Fonts): **Newsreader** (títulos e números), **Inter** (interface, chips; mínimo 18 px), **JetBrains Mono** (terminal, contadores).

Sufixo de estilo:

```
Handcrafted layered paper-cut illustration, elegant and minimal, photographed cut paper diorama
with real paper grain and soft realistic shadows between layers, warm cream and ivory paper
(#F0EEE6, #E8E4D8), terracotta orange accents (#D97757), charcoal ink details (#2B2A27), small
touches of muted sage green and dusty blue paper, soft diffused top light, calm editorial didactic
mood, generous negative space. Absolutely no text, no letters, no numbers, no logos, no watermark.
```

Exemplos de cena (antes do sufixo):

- **Fundo:** `Seamless empty background made of layered warm cream paper sheets with subtle torn deckled edges peeking at the corners, very subtle paper fiber texture, soft vignette, mostly flat and clean in the center for text overlay.`
- **Conceito → objeto:** `A paper-cut conveyor belt running left to right: crumpled messy paper tasks enter a small elegant paper machine with gears and exit as neat stacked cards with terracotta check marks.`
- **Metáfora vista de cima:** `Top-down overhead view of a paper-cut light wooden desk with neatly arranged documents, note cards with abstract squiggle lines, a small round terracotta kitchen timer, a coffee cup.`
- **Objeto isolado:** `A single small round paper-cut kitchen timer, isolated and centered on a plain flat cream background, front view.`
- **Edição da mesma cena:** `Edit this exact paper-cut desk scene, same overhead camera, same lighting, same style: remove all documents. Keep only the timer and the coffee cup exactly where they are.`

Sufixo de animação (imagem → vídeo):

```
[ação específica e lenta]. Slow gentle camera push-in. Handmade paper stop-motion feel, keep the
exact paper-cut style, colors and soft lighting, no new objects, no text.
```

Transformação com `keyframes.start` + `keyframes.end`: `The documents lift off the desk one by one and fly away out of frame like paper leaves in a gentle breeze, leaving the desk clean; the timer and the cup stay in place. Static overhead camera.`

### Cinematográfico escuro (B-roll realista)

```
Cinematic macro shot of [objeto] on a dark wooden desk, [ação lenta], very slow push-in dolly,
warm moody tungsten lamp light, dark bookshelf softly out of focus, shallow depth of field,
calm and premium, realistic, no people / no faces, no text.
```

Ajuste a luz e o cenário para combinar com o **seu** estúdio: o B-roll deve parecer parte do mesmo mundo da sua câmera.

### Formato vertical
Gere as imagens direto em 9:16 (não recorte de 16:9). Mantenha o assunto principal no terço central, longe do topo e da base, onde fica a interface dos apps.

## 7. Checklist

- [ ] quadros lidos, rosto e fundo mapeados
- [ ] `palavras.json` gerado e conferido
- [ ] suas orientações refletidas no plano
- [ ] custo estimado (`simulate_cost`) aprovado antes de gerar
- [ ] ilustrações sem texto, aprovadas em prancha; animações aprovadas pelo quadro do meio e do fim
- [ ] vídeos gerados mudos na montagem
- [ ] conferência de todas as trocas de layout (rosto, legibilidade, borda, sincronia)
- [ ] render final validado (resolução, fps, duração, volume)
