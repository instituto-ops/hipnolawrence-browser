# Agente Web Autônomo com Visão Local (Python + Ollama)

## Visão geral da arquitetura

A arquitetura mais alinhada ao seu objetivo é um loop de agente "Computer Use" local com 3 camadas principais: captura/visão, raciocínio e execução de ações.

- **Camada de Captura & Percepção (Ver):** Playwright para controlar o navegador, captura de screenshots (viewport ou elementos específicos), OCR local (Tesseract/paddleocr) e VLM local via Ollama (LLaVA/BakLLaVA/Qwen-VL) para interpretação visual avançada, incluindo elementos Canvas e estética de página.[^1]
- **Camada de Raciocínio (Pensar):** LLM local via Ollama (DeepSeek-R1, Llama-3, Qwen) recebendo um "estado" textual/estruturado (descrição de tela, resultados de OCR, metaestado do plano) e emitindo planos de ação estruturados em JSON.[^1]
- **Camada de Execução (Agir):** Playwright + bibliotecas de simulação humana (movimento de mouse, teclas, espera estocástica) implementando as ações prescritas pelo plano; módulo de integração com o sistema maior (n8n, planilhas locais, NeuroStrategy OS).[^1]

Essas camadas são coordenadas por um loop de agente com iteração Ver → Pensar → Agir → Ver, com limite de passos e mecanismos de segurança (timeout, whitelists de sites, filtros de privacidade).[^1]

***

## Stack de tecnologias recomendadas (100% local/grátis)

### Navegador e automação

- **Playwright Python:** controle confiável de Chrome/Chromium com suporte a múltiplos contextos, permissões e interceptação de rede.[^1]
- **Playwright async:** usar a API assíncrona para manter o agente responsivo e permitir múltiplas abas/tasklets no futuro.[^1]

### Visão computacional / OCR local

- **Captura de tela:** `page.screenshot()` (viewport completo) ou `locator.screenshot()` para elementos específicos (lista de conversas do WhatsApp, cards do Doctoralia, área de gráficos do Google Ads).[^1]
- **OCR textual:** 
  - `pytesseract` (Tesseract OCR) para texto relativamente limpo em português.[^1]
  - Alternativa mais moderna: `paddleocr` com modelos em português para melhor robustez.[^1]
- **VLM local:** via Ollama com modelos como:
  - **LLaVA**, **BakLLaVA** ou **Qwen-VL** para interpretação semântica de screenshots (identificar "Novo Lead", estética de página, leitura de cards complexos ou Canvas).[^1]
  - Esses modelos leem a imagem + prompt textual e devolvem texto estruturado (por exemplo, JSON com bounding boxes aproximadas, labels, ranking de resultados, etc.).[^1]

### LLM de raciocínio

- **DeepSeek-R1**, **Llama-3** ou similares rodando em Ollama com contexto suficiente para manter o estado da sessão do agente.[^1]
- Interface via HTTP local (porta 11434) a partir do Python, com um protocolo de mensagens fixo (system + history + última observação de tela; saída em JSON de ações).[^1]

### Simulação de mouse humano e stealth

- **Movimento humano:** não existe uma única lib padrão absoluta para Playwright, mas há componentes reutilizáveis:
  - **`playwright-stealth` (Python):** pacote que aplica patches de stealth e fornece utilitários para evasão de bot detection.[^1]
  - **Curvas de Bézier:** pode-se usar bibliotecas matemáticas genéricas como `numpy` ou `bezier` para gerar curvas suaves entre dois pontos e alimentar `page.mouse.move(x, y, steps=...)` com uma sequência de pontos, adicionando jitter manual.[^1]
- **Jitter e pausas humanas:** usar `random` para introduzir pequenas variações de coordenadas e delays não lineares; controlar isso em um módulo dedicado, para manter o core do agente limpo.[^1]

### Integração com seu ecossistema

- **Extensão Chrome MV3:** usada apenas como front-end de input, enviando comandos para um servidor local (FastAPI/Flask) que orquestra o agente.[^1]
- **Comunicação:** WebSockets ou HTTP local entre extensão e backend Python.
- **Persistência de dados:** planilhas locais (por exemplo, via `openpyxl`/`pandas`), CSV ou integração com seu n8n via webhooks locais.

***

## Uso de modelos de visão locais em vez de GPT-4o no browser-use

### Situação atual do `browser-use`

Muitos exemplos públicos de `browser-use` usam GPT-4o como backend principal tanto para raciocínio quanto para interpretação visual.[^1]
No entanto, é possível adaptar o fluxo para usar Ollama com modelos VLM e LLM separados, desde que se assuma o controle da camada de agente.[^1]

### Estratégia: desacoplar percepção visual do agente

1. **Captura de screenshot:** a cada passo, o Playwright captura a tela atual.
2. **Pipeline de visão:**
   - Primeiro, aplica OCR (Tesseract/PaddleOCR) para obter texto bruto da tela.[^1]
   - Depois, envia a imagem (ou recortes específicos) para o VLM via Ollama com um prompt que peça uma saída estruturada, por exemplo:

   ```
   Você é um assistente de visão. Analise a captura de tela de um site.
   Seu objetivo: descrever elementos clicáveis relevantes e sua posição aproximada.

   Responda APENAS em JSON no formato:
   {
     "descricao_geral": "...",
     "elementos": [
       {"nome": "card_doctoralia_hipnose_ericksoniana_goiania", "texto": "Hipnose Ericksoniana - Goiânia - Fulano", "tipo": "card_profissional", "x": 345, "y": 612},
       ...
     ]
   }
   ```

   O VLM devolve esse JSON textual, que o backend converte em dicionário Python.[^1]

3. **Estado para o LLM de raciocínio:** o LLM textual recebe:
   - Metadados da tarefa ("encontrar ranking no Doctoralia"),
   - Saída do OCR simplificada,
   - Saída estruturada do VLM (lista de elementos com texto e coordenadas aproximadas).[^1]

4. **Execução:** o LLM define ações ("mover_mouse_para elemento.x, elemento.y", "scroll_down", etc.), devolvendo JSON.[^1]

### Adaptando `browser-use`/LangChain

- Em vez de usar `browser-use` como caixa preta com GPT-4o, a abordagem recomendada é **reusar apenas a ideia de schema de ações** (open-page, click, type, scroll, wait) e implementar manualmente:
  - Uma função `observe_page()` que retorna um dicionário com OCR + elementos VLM.
  - Uma ferramenta `execute_action(action: dict)` que traduz ações em chamadas Playwright.[^1]
- O LLM local (DeepSeek/Llama-3) é configurado com um prompt de sistema que define o formato de saída (lista de ações em JSON) e a semântica de cada ação.

***

## Simulação de comportamento humano (mouse, jitter, stealth)

### Movimento de mouse baseado em curvas de Bézier

A lógica básica é gerar uma curva suave entre ponto inicial e final e amostrar vários pontos intermediários.

Exemplo de função em Python usando `numpy` para curvas quadráticas:

```python
import numpy as np
import random

async def human_mouse_move(page, start, end, duration=0.8, steps=50):
    x0, y0 = start
    x2, y2 = end

    # Ponto de controle com jitter aleatório
    cx = (x0 + x2) / 2 + random.randint(-50, 50)
    cy = (y0 + y2) / 2 + random.randint(-50, 50)

    ts = np.linspace(0, 1, steps)
    for t in ts:
        x = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t ** 2 * x2
        y = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t ** 2 * y2

        # Jitter leve por passo
        jx = x + random.uniform(-1, 1)
        jy = y + random.uniform(-1, 1)

        await page.mouse.move(jx, jy)
```

Essa função pode ser combinada com `await page.mouse.down()` e `await page.mouse.up()` para cliques, mantendo o movimento realista.[^1]

### Bibliotecas e técnicas de stealth

- **`playwright-stealth` (Python):** biblioteca que aplica patches no Playwright (por exemplo, remoção de `navigator.webdriver`, ajustes em `userAgent`, plugins e WebGL) para reduzir detecção em sites sensíveis.[^1]
- **User agents realistas:** uso de cabeçalhos de user agent reais (navegadores estáveis em dispositivos comuns), rotacionados de forma coerente, mas consistente por sessão.[^1]
- **Parâmetros de viewport e device scale:** simular resoluções típicas (1920x1080, 1366x768) e zoom normal para parecer sessão humana comum.[^1]
- **Padrões de interação:**
  - Pequenos scrolls com pausas.
  - Movimentos de mouse que não vão direto ao alvo, mas fazem micro-ajustes.
  - Pequenas pausas antes de clicar em elementos críticos (botões de enviar, login, etc.).[^1]

### Configuração de `playwright-stealth`

Um esboço típico no Python:

```python
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

async def launch_stealth_browser():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={"width": 1366, "height": 768},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...",
        )
        page = await context.new_page()
        await stealth_async(page)
        return browser, context, page
```

Isso serve como base tanto para acessos à Meta Ads Library quanto ao Doctoralia, sempre respeitando as políticas de uso das plataformas.[^1]

***

## Lógica condicional de privacidade no WhatsApp Web

### Objetivo

- Ver apenas a lista de conversas.
- Detectar visualmente as conversas marcadas como "Novo Lead" (por etiqueta, ícone, texto, cor específica etc.).
- Calcular coordenadas aproximadas X,Y dessas conversas e clicar somente nelas, ignorando o resto.

### Pipeline recomendado

1. **Navegar até WhatsApp Web** com Playwright, garantindo que a lista de conversas esteja visível.
2. **Capturar screenshot apenas da lista de conversas**, usando um locator CSS que delimite essa área (por exemplo, a sidebar esquerda).[^1]

   ```python
   conv_list = page.locator("div[aria-label='Lista de conversas']")
   await conv_list.screenshot(path="conversas.png")
   ```

3. **Processar screenshot com OCR + VLM:**
   - OCR para extrair possíveis textos "Novo Lead".
   - VLM para identificar visualmente ícones/labels, inclusive se não forem texto puro.
4. **Mapear coordenadas relativas:**
   - O VLM pode ser instruído a devolver posições aproximadas dos itens que contenham "Novo Lead".
   - Como alternativa ou fallback, o OCR devolve a posição dos bounding boxes (quando usado via APIs que suportam localização de texto).
5. **Converter coordenadas relativas em coordenadas absolutas na página:**
   - Ao saber a posição e tamanho do elemento de lista (via Playwright) e a resolução da screenshot, é possível mapear (x_rel, y_rel) → (x_abs, y_abs) usando regra de três simples.
6. **Executar clique apenas nessas coordenadas:**
   - Usar o módulo de movimento humano para mover o mouse até (x_abs, y_abs) e clicar.

### Exemplo de prompt para o VLM

```text
Você receberá uma captura de tela da coluna esquerda do WhatsApp Web, contendo uma lista de conversas.
Seu objetivo é localizar visualmente todas as conversas que tenham algum indicativo de "Novo Lead".

Responda APENAS em JSON no formato:
{
  "conversas_novo_lead": [
    {"descricao": "Novo Lead - João", "x_rel": 0.52, "y_rel": 0.18},
    {"descricao": "Novo Lead - Clínica", "x_rel": 0.55, "y_rel": 0.44}
  ]
}

Onde x_rel e y_rel são coordenadas normalizadas entre 0 e 1 em relação à largura e altura totais da imagem.
```

O backend transforma essas coordenadas normalizadas em pixels absolutos com base no tamanho atual do viewport e do elemento da lista.[^1]

***

## Engenharia reversa de ranking no Doctoralia

### Tarefa

- Realizar busca anônima (por exemplo, "Hipnose Ericksoniana Goiânia").
- Localizar seu card visualmente entre os resultados.
- Extrair a posição (ranking) e a contagem de horários disponíveis (widgets dinâmicos/calendário JS).

### Pipeline

1. **Abertura da página de resultados:**
   - Página é carregada com uma lista de cards de profissionais, geralmente com foto, nome, especialidade, avaliações e botão de agendamento.[^1]
2. **Captura de screenshot da área de resultados:**
   - `locator(".search-results").screenshot("doctoralia_results.png")`.
3. **Passo de visão:**
   - Enviar ao VLM com prompt pedindo:
     - Listagem ordenada top-down dos profissionais.
     - Nome completo/identificador.
     - Posição (1, 2, 3, ...).
     - Indicação textual dos horários disponíveis (por exemplo, "3 horários disponíveis hoje", "sem horários disponíveis").
4. **Identificação do seu card:**
   - O LLM de raciocínio recebe o JSON retornado pelo VLM e procura a entrada que case com o seu nome/clínica.
   - Extração do campo `posicao` e de qualquer metadado de horários.
5. **Fallback via DOM:**
   - Em paralelo, pode-se usar Playwright para pegar o DOM da lista de cards e tentar casar via seletor de texto (por exemplo, `page.locator("text=Seu Nome").nth(0)`) como redundância.[^1]

### Exemplo de saída esperada do VLM

```json
{
  "profissionais": [
    {"nome": "Dr. Fulano A", "posicao": 1, "texto_card": "Hipnose Ericksoniana - Goiânia", "horarios": "3 horários disponíveis hoje"},
    {"nome": "Dr. Fulano B", "posicao": 2, "texto_card": "Psicologia Clínica", "horarios": "1 horário amanhã"},
    {"nome": "Seu Nome", "posicao": 3, "texto_card": "Hipnose Ericksoniana e TEA em adultos", "horarios": "sem horários disponíveis"}
  ]
}
```

O backend grava `posicao` e `horarios` em uma planilha local, com timestamp, para acompanhar evolução do ranking ao longo do tempo.[^1]

***

## Bypass de API em Google Ads & Analytics via visão/OCR

### Contexto

Google Ads e Google Analytics/GA4 têm dashboards com muitos componentes não triviais: tabelas complexas, cards resumidos, gráficos Canvas, tooltips dinâmicos.[^1]
As APIs oficiais requerem Developer Token, permissões etc.; o objetivo aqui é extrair apenas o que já está exibido na tela, como se fosse um "leitor humano".[^1]

### Estratégia geral

1. **Definir o layout alvo:**
   - Para cada tela, mapear manualmente quais áreas contêm os dados desejados (ex: tabela de campanhas, cards de conversão, gráfico de custo vs conversões), inclusive por CSS selectors quando possível.[^1]
2. **Capturar subsets de tela:**
   - Em vez de OCR da tela inteira, capturar apenas elementos relevantes (`locator.screenshot`).
3. **Escolher ferramenta adequada por tipo de componente:**
   - **Tabelas HTML:** preferência por extração DOM via Playwright (ler `<table>`, `<tr>`, `<td>`) quando presentes.[^1]
   - **Cards numéricos simples:** OCR (Tesseract/PaddleOCR) normalmente resolve.
   - **Gráficos Canvas:** VLM (LLaVA/Qwen-VL) com prompt específico para ler valores agregados, tendências ou último ponto do gráfico.

### Exemplo: extrair dados de tabela de campanhas do Google Ads

1. **Via DOM (quando acessível):**

```python
rows = page.locator("[role='row']").all()
for r in rows:
    cells = r.locator("[role='cell']").all_inner_texts()
    # processar cells e salvar em planilha
```

2. **Via OCR/VLM (quando tabela estiver em Canvas/complexa):**

- Screenshot da área da tabela.
- Prompt ao VLM solicitando saída em CSV/JSON:

```text
Você verá uma imagem contendo uma tabela de desempenho de campanhas do Google Ads.
Extraia todas as linhas e colunas legíveis e devolva como CSV no seguinte formato:

Nome_da_Campanha;Impressões;Cliques;CPC_Médio;Conversões;Custo
...
```

- Backend converte CSV textual em dataframe (`pandas.read_csv(StringIO(csv_text), sep=';')`) e salva em planilha local.[^1]

### Extração de cards/resumos

Para KPIs em cards (por exemplo, "Cliques: 123", "Conversões: 7", "Custo: R$ 350,00"):

- Screenshot do card individual.
- OCR para texto bruto.
- Regex/parse simples no Python para normalizar números (remover símbolos, trocar vírgula por ponto etc.).

Em cenários ambíguos (como gráficos com múltiplas linhas), o VLM pode ser instruído a responder apenas perguntas específicas (por exemplo, "qual é o valor da métrica X no último ponto do gráfico?").[^1]

***

## Loop Ver → Pensar → Agir (esqueleto técnico)

### Representação de estado

O estado mínimo por passo de agente inclui:

- URL atual.
- Screenshot(s) recentes.
- Saída de OCR.
- Saída do VLM (estrutura com elementos clicáveis, textos, rankings, etc.).
- Histórico resumido de ações recentes.[^1]

### Esqueleto em Python (alto nível)

```python
async def observe(page):
    # 1) Screenshot
    await page.screenshot(path="screen.png", full_page=False)

    # 2) OCR
    ocr_text = run_ocr("screen.png")

    # 3) Visão (VLM)
    vlm_json = call_vlm("screen.png", prompt=VLM_PROMPT)

    return {
        "url": page.url,
        "ocr": ocr_text,
        "visao": vlm_json,
    }

async def think(state, objetivo):
    prompt = build_prompt_from_state(state, objetivo)
    actions_json = call_llm(prompt)  # DeepSeek/Llama-3 via Ollama
    return actions_json["acoes"]

async def act(page, actions):
    for a in actions:
        if a["tipo"] == "click":
            x, y = a["x"], a["y"]
            await human_mouse_move(page, get_current_mouse_pos(), (x, y))
            await page.mouse.click(x, y)
        elif a["tipo"] == "scroll":
            await page.mouse.wheel(0, a.get("delta_y", 400))
        elif a["tipo"] == "esperar":
            await asyncio.sleep(a.get("segundos", 1.0))
        # ... outras ações

async def agent_loop(page, objetivo, max_steps=15):
    for step in range(max_steps):
        state = await observe(page)
        if check_objetivo_concluido(state, objetivo):
            break
        actions = await think(state, objetivo)
        await act(page, actions)
```

Esse esqueleto pode ser especializado por site/tarefa: um conjunto de prompts e regras de pós-processamento para WhatsApp Web, outro para Doctoralia, outro para Google Ads/Analytics.[^1]

***

## Considerações de performance e hardware

### Restrições do seu setup

- GPU: GTX 1650 com 4 GB de VRAM; CPU: Ryzen 5 5600G; RAM: 16 GB.
- Isso é suficiente para LLMs texto de 3B–8B quantizados e para VLMs compactos, mas exige cuidado com tamanho de modelo de visão.[^2]

### Recomendações práticas

- **Modelos de visão menores:** preferir variantes reduzidas/quantizadas (por exemplo, LLaVA/Qwen-VL menores) para manter latência aceitável.[^1]
- **Cortes de imagem:** em vez de passar tela cheia sempre, recortar apenas regiões de interesse (lista de conversas, área de resultados, gráfico específico), reduzindo custo de inferência.[^1]
- **Frequência de visão:** não chamar o VLM a cada pequeno passo; usar heurísticas (por exemplo, chamar visão somente após scroll significativo ou mudança de página).[^1]
- **Uso combinado OCR+VLM:** OCR é muito mais leve, então reservar o VLM para tarefas que realmente exigem interpretação visual complexa (Canvas, estética, gráficos); texto puro fica com OCR.[^1]

***

## Checklist por caso de uso

### WhatsApp Web (Novo Lead)

- [ ] Locator da lista de conversas e screenshot parcial.
- [ ] OCR + VLM com prompt para localizar "Novo Lead" e devolver coordenadas normalizadas.
- [ ] Conversão para coordenadas absolutas e clique com movimento humano.
- [ ] Filtro de privacidade (nenhum outro clique é permitido fora das coordenadas aprovadas pelo VLM/LLM).

### Doctoralia (Ranking + horários)

- [ ] Execução de busca anônima.
- [ ] Screenshot da área de resultados.
- [ ] VLM com prompt para listar cards em ordem e extrair posição e horários.
- [ ] LLM textual para localizar seu card e salvar `posicao` + `horarios` em planilha.

### Google Ads / Analytics (bypass API)

- [ ] Mapear manualmente componentes-alvo (tabelas, cards, gráficos).
- [ ] Tentar DOM direto para tabelas; fallback OCR/VLM para casos complexos.
- [ ] Normalizar dados e salvar em CSV/planilha local.

***

## Conclusão

A arquitetura proposta permite um agente web autônomo estilo LAM 100% local usando Python + Playwright + Ollama (LLM + VLM), combinando OCR, visão, raciocínio e controle de navegador de forma orquestrada.[^1]
Com módulos específicos para movimento humano, stealth, visão seletiva e protocolos por site (WhatsApp Web, Doctoralia, Google Ads/Analytics), o sistema se torna um "operador digital" que lê a tela como um humano e age com privacidade e controle fino.[^1]
Os exemplos de código, prompts e fluxos descritos servem como base para implementação progressiva dentro do seu NeuroStrategy OS e podem ser integrados ao seu stack atual com n8n, extensões Chrome e servidores locais Python.[^1]

---

## References

1. [Contexto: Sou um psicologo sem conhecimento de programação, construindo um Agente de Navegador Autônomo (Browser Agent) estilo "Large Action Model" (LAM). O objetivo é que este agente opere localmente no meu computador para realizar tarefas complexas...

...texto do usuário logado, extrair o texto e retornar a resposta.
Objetivo Final: Quero um tutorial "passo a passo" para transformar meu PC em um servidor de automação pessoal gratuito, onde eu digito uma ordem e o mouse se move sozinho para cumpri-la.](https://www.perplexity.ai/search/35cd5393-d53d-4fdf-be9c-c33692661522) - A arquitetura que você descreveu é viável com stack 100% local e open source, usando Ollama + Playwr...

2. [Considere:

Computador atual:
    *   *GPU:* NVIDIA GeForce GTX 1650 (4GB)
    *   *CPU:* AMD Ryzen 5 5600G (6 núcleos / 12 threads)
    *   *RAM:* 16 GB (2666 MT/s)

Notebook atual:
IdeaPad S145-15IIL
Intel Core i5-1035G1
Placa de vídeo (GPU) Modelo...

...iGPU)

Atualmente o nucleo de marketing está utilizando:
Nível 1 (Groq API): Ultra-rápida e inteligente (requer apenas uma chave gratuita, ja esta instalado a chave).
Nível 2 (Ollama Local): Privacidade total e offline (usa o seu llama3.2 instalado).](https://www.perplexity.ai/search/dcaace0e-e44d-4797-b902-ed3ceae100f7) - Sim, o seu setup atual aguenta muito bem a estratégia “Groq + Ollama”, mas com papéis diferentes par...

