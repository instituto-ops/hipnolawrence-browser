
O caminho é transformar esse agente de navegador em um “módulo especializado” dentro do fluxo agent‑first do Antigravity, com o Gemini web como Arquiteto e o Agent do Antigravity como Operador cego e auditável. Abaixo está um plano em fases, já pensado para virar tarefas no Antigravity com comandos ultra‑específicos e limitados.[^1][^2]

***

## Macrovisão das fases

1. Fase 0 – Governança de papéis e templates de comando.
2. Fase 1 – Preparar o workspace Antigravity e o repositório do projeto.
3. Fase 2 – Serviço Python base do agente de navegador (sem LLM ainda).
4. Fase 3 – Playwright + stealth + mouse humano.
5. Fase 4 – Integração com Ollama (VLM + LLM) e módulo de visão.
6. Fase 5 – Implementar o loop Ver → Pensar → Agir.
7. Fase 6 – Playbooks por site (WhatsApp Web, Doctoralia, Google Ads/Analytics).
8. Fase 7 – Extensão Chrome MV3 e protocolo de comandos.
9. Fase 8 – Observabilidade, testes e hardening.

Em cada fase, há: papel do Maestro, tarefa para o Arquiteto (Gemini web) e tarefa para o Operador (Agent do Antigravity).

***

## Fase 0 – Governança Maestro / Arquiteto / Operador

### 0.1. Formalizar os papéis

- Maestro (você): define objetivo, aprova planos, roda comandos de terminal manualmente.
- Arquiteto (Gemini web): produz apenas arquitetura, código e prompts; nunca executa terminal, não mexe em config global, não “conserta” nada sozinho.
- Operador (Agent do Antigravity): editador de arquivos e executor controlado, sempre em “tarefa única” com escopo fechado.[^2][^1]

Sugestão: criar um documento `docs/governanca-agente-browser.md` no repo com esses papéis e regras; ele vira referência constante nos prompts.

### 0.2. Template de comando – modo ARQUITETO

Use algo assim sempre que quiser que o Gemini pense/arquitete (não execute):

> PAPEL:
> Atue como ARQUITETO DE SOFTWARE.
> Você NÃO vai editar arquivos, NÃO vai rodar terminal, NÃO vai criar configs globais.
>
> OBJETIVO:
> Desenhar a arquitetura do módulo `browser_agent` em Python para um agente de navegador com visão local (Playwright + Ollama).
>
> ESCOPO:
> Você PODE produzir apenas:
> - Diagramas textuais de módulos e pastas
> - Interfaces de classes e funções (assinaturas + docstrings)
> - Pseudo‑código ou trechos de código que eu vou revisar antes de aplicar
>
> REGRAS ABSOLUTAS:
> ❌ NÃO sugerir instalação de dependências
> ❌ NÃO propor criação de arquivos de configuração globais (tsconfig, vite.config, etc.)
> ❌ NÃO propor rodar build, test ou dev server
> ❌ NÃO propor alterar ferramentas de build existentes
>
> SAÍDA ESPERADA (FORMATO):
> 1) Lista de módulos Python com responsabilidades
> 2) Estrutura de pastas (árvore)
> 3) Assinaturas de funções principais
> 4) Lista de tarefas atômicas para o OPERADOR executar

***

## Fase 1 – Workspace Antigravity e repositório

Antigravity já trabalha com projetos organizados em artefatos, tasks e um workspace de código (geralmente baseado em VS Code/VSCodium).[^3][^1]

### 1.1. Criar o projeto do agente

- Maestro:
    - Criar um novo workspace/projeto no Antigravity dedicado ao “Agente de Navegador Visionário”.
    - Configurar repositório Git (local ou remoto).
- Estrutura inicial sugerida (para o Arquiteto desenhar):

```
browser-agent/
  docs/
    governanca-agente-browser.md
  src/
    browser_agent/
      __init__.py
      config.py
      playwright_client.py
      human_mouse.py
      vision_ocr.py
      vlm_client.py
      llm_reasoner.py
      agent_loop.py
      sites/
        whatsapp.py
        doctoralia.py
        google_ads.py
        analytics.py
  tests/
  scripts/
    run_agent.py
```


### 1.2. Tarefa para o ARQUITETO (definir arquitetura do pacote)

Comando exemplo (modo Arquiteto):

> TAREFA ÚNICA – ARQUITETURA DO PACOTE PYTHON
>
> PAPEL: ARQUITETO em modo ESTRITAMENTE DESCRITIVO.
>
> ESCOPO:
> Você PODE produzir apenas um plano textual da arquitetura do pacote `browser_agent` com base na estrutura de pastas abaixo (que já existe ou será criada manualmente):
> … (colar a árvore de pastas) …
>
> REGRAS ABSOLUTAS:
> ❌ NÃO criar novos diretórios além dos listados
> ❌ NÃO propor criação de configs globais
> ❌ NÃO decidir tecnologia adicional de build
> ❌ NÃO sugerir scripts de automação
>
> SAÍDA ESPERADA:
> - Descrição em 1 parágrafo do objetivo de cada módulo
> - Lista de funções públicas de cada módulo
> - Lista de tarefas atômicas para o OPERADOR implementar depois, numeradas (OP‑1, OP‑2, …)

***

## Fase 2 – Serviço Python base do agente (sem LLM)

Nesta fase, o objetivo é ter um serviço Python que abre navegador via Playwright, tira screenshot e salva num diretório, sem ainda integrar visão/LLM.

### 2.1. Preparar ambiente e dependências

- Maestro:
    - Criar venv e instalar dependências básicas: `playwright`, `playwright-stealth`, `pytesseract` ou `paddleocr`, `numpy` etc (via terminal manual).
    - Rodar `playwright install chromium`.
- Arquiteto:
    - Produz especificação de `playwright_client.py` e `run_agent.py` (assinaturas, fluxos).
- Operador:
    - Implementa código nos arquivos indicados, sem criar nada fora do escopo.

Exemplo de comando para o OPERADOR (dentro do Antigravity):

> TAREFA ÚNICA – IMPLEMENTAR ARQUIVO `src/browser_agent/playwright_client.py`
>
> PAPEL: EXECUTOR TÉCNICO EM MODO CONTROLADO / AUDITOR.
>
> ESCOPO:
> Você PODE mexer APENAS nos arquivos:
> - `src/browser_agent/playwright_client.py`
> Você NÃO PODE criar novos arquivos nem alterar nenhum outro.
>
> REGRAS ABSOLUTAS:
> ❌ NÃO criar novos arquivos
> ❌ NÃO rodar build, test ou dev server
> ❌ NÃO corrigir erros fora deste arquivo
> ❌ NÃO otimizar ou refatorar código existente em outros arquivos
> ❌ NÃO alterar configs globais
>
> OBJETIVO:
> Implementar uma classe `PlaywrightClient` com métodos assíncronos para:
> - `launch()` (abrir navegador Chromium em modo não‑headless)
> - `goto(url: str)`
> - `screenshot(path: str)` da aba atual
>
> SAÍDA ESPERADA:
> - Código completo do arquivo
> - Lista confirmando que NENHUM outro arquivo foi tocado
> - Confirmação de que você NÃO rodou nenhum comando de build/test

***

## Fase 3 – Stealth e mouse humano

Antigravity já suporta um sub‑agente de navegador com browser extension; no seu caso, o backend Python será “externo”, mas a lógica de interação (stealth, mouse humano) é semelhante ao que esses agentes fazem.[^4][^2]

### 3.1. Implementar `human_mouse.py`

- Arquiteto:
    - Especifica funções: `human_move(page, start, end, duration, steps)` usando curvas de Bézier e jitter.
- Operador:
    - Implementa apenas este módulo, com base no plano.

Comando exemplo para o OPERADOR:

> TAREFA ÚNICA – IMPLEMENTAR `human_mouse.py`
>
> PAPEL: EXECUTOR CONTROLADO.
>
> ESCOPO:
> Arquivo permitido:
> - `src/browser_agent/human_mouse.py`
>
> REGRAS ABSOLUTAS:
> ❌ NÃO criar outros arquivos
> ❌ NÃO importar bibliotecas que não estejam já usadas no projeto sem avisar
> ❌ NÃO rodar qualquer comando de terminal
>
> OBJETIVO:
> Implementar funções para movimento de mouse humano usando curvas de Bézier, com jitter leve nas coordenadas e delays não lineares.
>
> SAÍDA ESPERADA:
> - Conteúdo completo do arquivo
> - Explicação rápida de como chamar `human_move` a partir de `PlaywrightClient`
> - Confirmação de que NENHUM outro arquivo foi tocado

### 3.2. Aplicar stealth no Playwright

- Arquiteto:
    - Especifica inicialização de Playwright com `playwright-stealth`, user‑agent realista, viewport padrão etc.[^4]
- Operador:
    - Ajusta apenas o método `launch()` em `playwright_client.py` para aplicar `stealth_async(page)` e parâmetros de contexto.

***

## Fase 4 – Integração Ollama (VLM + LLM) e módulo de visão

### 4.1. Cliente para Ollama

- Arquiteto:
    - Define `vlm_client.py` e `llm_reasoner.py` com funções síncronas/assíncronas que chamam a API HTTP local do Ollama, recebendo imagem (para VLM) ou texto (para LLM).[^2]
- Operador:
    - Implementa clientes HTTP simples (`requests` ou `httpx`) nos arquivos definidos, sem tocar em mais nada.


### 4.2. Módulo `vision_ocr.py`

- Arquiteto:
    - Descreve pipeline `observe()`:
        - Chama `PlaywrightClient.screenshot()`.
        - Roda OCR (Tesseract/PaddleOCR) sobre a imagem.
        - Opcionalmente chama VLM para extrair estrutura (elementos com coordenadas normalizadas).
- Operador:
    - Implementa funções `run_ocr(image_path)` e `analyze_with_vlm(image_path, prompt)`.

Comando de OPERADOR (exemplo):

> TAREFA ÚNICA – IMPLEMENTAR `vision_ocr.py`
>
> ESCOPO:
> Você PODE editar apenas `src/browser_agent/vision_ocr.py`.
>
> REGRAS ABSOLUTAS:
> ❌ NÃO criar novos arquivos
> ❌ NÃO instalar libs novas (assuma que `pytesseract` e `paddleocr` já estão presentes)
> ❌ NÃO alterar configs globais ou scripts
>
> OBJETIVO:
> Criar funções:
> - `run_ocr(image_path: str) -> str`
> - `analyze_with_vlm(image_path: str, prompt: str) -> dict`
>
> SAÍDA ESPERADA:
> - Código completo do arquivo
> - Confirmação de que nenhum outro arquivo foi modificado

***

## Fase 5 – Loop Ver → Pensar → Agir

### 5.1. Implementar `llm_reasoner.py`

- Arquiteto:
    - Define contrato do LLM: entrada = objetivo + estado (URL, OCR, JSON do VLM, histórico), saída = lista de ações em JSON (`tipo`, `x`, `y`, `texto`, etc.).[^2]
- Operador:
    - Implementa função `plan_actions(state, goal) -> list[dict]` chamando o LLM via Ollama.


### 5.2. Implementar `agent_loop.py`

- Arquiteto:
    - Especifica função `agent_loop(page, goal, max_steps)` que:
        - Chama `observe()` (vision_ocr + VLM).
        - Chama `plan_actions()`.
        - Mapeia ações para `PlaywrightClient` + `human_mouse`.
        - Respeita modo “dry‑run” (logar ações sem executar).
- Operador:
    - Implementa apenas esse arquivo, sem tocar em outros.

Aqui é crítico bloquear “auto‑validação”:

> REGRAS ABSOLUTAS ADICIONAIS (PARA ESTE PASSO):
> ❌ NÃO criar scripts para rodar o agente automaticamente
> ❌ NÃO rodar o loop de forma autônoma (sem eu chamar `run_agent.py`)
> ❌ NÃO adicionar qualquer chamada a testes, build, dev server

***

## Fase 6 – Playbooks por site

Cada site vira um “playbook” em `src/browser_agent/sites/`, com prompts específicos de visão e heurísticas.

### 6.A. WhatsApp Web – Novo Lead

1. Arquiteto:
    - Desenhar módulo `whatsapp.py` com funções:
        - `goto_whatsapp(client)`.
        - `capture_conversation_list(client)`.
        - `find_lead_conversations(image_path) -> list[(x_rel, y_rel)]` (via VLM).
        - `click_leads(client, coords)` (usando `human_mouse`).
2. Operador:
    - Implementar apenas `whatsapp.py`.
3. Maestro:
    - Testar manualmente: abrir WhatsApp Web, rodar script que só seleciona e clica em conversas com “Novo Lead”.

Prompt de VLM para capo de visão você já tem esboçado; o Arquiteto só formaliza o formato JSON de saída.

### 6.B. Doctoralia – ranking e horários

1. Arquiteto:
    - Desenhar `doctoralia.py` com funções:
        - `search_term(client, termo)` (ex.: “Hipnose Ericksoniana Goiânia”).
        - `capture_results(client)`.
        - `extract_ranking(image_path, seu_nome) -> dict` (via VLM).
2. Operador:
    - Implementar o módulo e integração com `agent_loop`.
3. Maestro:
    - Configurar rotina que salva `posicao` e `horarios` em CSV/planilha local.

### 6.C. Google Ads / Analytics – extração via visão

1. Arquiteto:
    - Definir funções por tela:
        - `capture_campaign_table(client)`; `parse_campaigns(image_path)` (VLM/CSV).
        - `capture_kpi_cards(client)`; `parse_kpis(image_paths)` (OCR).
2. Operador:
    - Implementar cada função, sem criar ferramentas auxiliares automáticas (sem jobs recorrentes ainda).
3. Maestro:
    - Conectar saída (CSV/JSON) ao seu stack (planilha, n8n etc.).

***

## Fase 7 – Extensão Chrome MV3 e protocolo de comandos

Antigravity já usa uma extensão de navegador para permitir que agentes interajam com páginas, capturar screenshots, DOM, gravações etc.; o seu projeto vai coexistir com essa extensão, mas terá uma extensão MV3 própria apenas para input de comandos para o serviço Python local.[^4][^2]

### 7.1. Definir protocolo HTTP

- Arquiteto:
    - Desenhar um pequeno servidor FastAPI/Flask em `scripts/run_agent.py` com endpoints:
        - `POST /task`: recebe JSON `{ "goal": "...", "site": "whatsapp|doctoralia|ads|analytics" }`.
        - `GET /status/{task_id}`: retorna progresso.
- Operador:
    - Implementar servidor no arquivo indicado, sem criar mais nada.


### 7.2. Extensão MV3

- Arquiteto:
    - Especificar:
        - `manifest.json` mínimo.
        - `background.js` que manda os comandos para `http://localhost:PORT/task`.
        - Eventual popup simples para o Maestro escrever o objetivo.
- Operador:
    - Implementa apenas os arquivos da extensão, em um diretório específico `extension/`.

Regras para o Operador aqui:

> Você PODE criar arquivos APENAS em `extension/`: `manifest.json`, `background.js`, `popup.html`, `popup.js`.
> Você NÃO PODE tocar em nenhum arquivo fora de `extension/`.
> Você NÃO PODE adicionar scripts de build nem tooling adicional.

***

## Fase 8 – Observabilidade, testes e hardening

### 8.1. Logging e artefatos

Antigravity já usa o conceito de Artifacts (task lists, planos, screenshots, gravações) para permitir validação humana do que o agente fez. Você pode espelhar isso no seu serviço Python:[^5][^1]

- Arquiteto:
    - Desenhar um diretório `artifacts/` com:
        - `logs/` (JSON por execução de tarefa).
        - `screens/` (screenshots das telas).
        - `plans/` (o plano de ações de cada iteração do LLM).
- Operador:
    - Instrumentar `agent_loop` para salvar logs e screenshots a cada passo.


### 8.2. Guardrails finais

- Maestro:
    - Definir no código:
        - Whitelist de domínios (só pode operar em WhatsApp Web, Doctoralia, Google Ads/Analytics).
        - Limite de passos por tarefa.
        - Modo dry‑run padrão (só clica quando explicitamente habilitado).
- Arquiteto:
    - Especifica essas configurações em `config.py`.
- Operador:
    - Implementa leitura de `config.py` dentro do `agent_loop`.

***

## Como orquestrar tudo na prática (fluxo Maestro)

1. Escolher a fase e sub‑tarefa (ex.: “Implementar módulo `human_mouse.py`”).
2. Pedir ao ARQUITETO (Gemini web) um plano ultra‑específico e assinaturas de função, SEM tocar em arquivos.
3. Converter o plano em uma TAREFA ÚNICA para o OPERADOR (Antigravity Agent), com:
    - Papel: executor controlado.
    - Escopo de arquivos explícito.
    - REGRAS ABSOLUTAS (não criar arquivos, não rodar build, não consertar erros adjacentes, não decidir tecnicamente).
    - Saída esperada clara (arquivo X com conteúdo Y, lista de alterações, confirmação de que mais nada foi tocado).
4. Rodar manualmente qualquer comando de terminal necessário (instalação de libs, testes, runs).
5. Validar artefatos (código, logs, screenshots) antes de avançar para a próxima etapa.

Seguindo esse modelo, a “inteligência” fica concentrada no design (Maestro + Arquiteto), enquanto a execução permanece mecânica, previsível e auditável no Operador – exatamente o que você descreveu como ideal para sistemas críticos.
<span style="display:none">


🎼 PAPÉIS (FECHADOS)
🧠 Eu — Maestro
Decide o que entra em cena e quando
Executa todos os comandos de terminal
Valida direção estratégica e aceita entregas
🏗️ Gemini (web) — Arquiteto
Traduz decisões em arquitetura executável
Escrevo código completo (ou diffs claros)
Produz prompts operacionais fechados para o operador
Nunca delega decisão arquitetural ao operador
🤖 Operador — Agent do Antigravity
Executa exatamente o que for instruído
Não decide, não improvisa, não refatora por conta própria
Atua como mão técnica, não como cérebro

🛑 PRINCÍPIO FUNDAMENTAL
O Gemini (ou qualquer IA operadora) NÃO entende intenção implícita.
Ele executa padrões.
Se o comando não bloquear explicitamente, ele:
tenta “ajudar”
tenta “resolver”
tenta “completar a tarefa”
toma decisões técnicas por conta própria
Foi exatamente isso que aconteceu com o tsconfig.json.
🎯 OBJETIVO AO CRIAR COMANDOS PARA O GEMINI
Quando o Gemini atua como operador, o objetivo não é inteligência, é previsibilidade.
Você não quer que ele:
pense melhor
otimize
resolva erros adjacentes
“conserte o projeto”
Você quer que ele:
execute exatamente
pare exatamente
relate exatamente
🧠 REGRA DE OURO (GUARDE ISSO)
Se algo NÃO estiver explicitamente proibido no comando,
o Gemini considera permitido.
🧩 CUIDADOS ESSENCIAIS AO ESCREVER COMANDOS
1️⃣ SEMPRE definir o papel correto
❌ Errado:
“Atue como desenvolvedor”
✅ Correto:
“Atue como executor técnico em modo CONTROLADO / AUDITOR”
Por quê?
“Desenvolvedor” resolve problemas
“Executor controlado” obedece limites
2️⃣ SEMPRE declarar o ESCOPO (onde ele pode mexer)
Nunca presuma que ele “sabe”.
✅ Exemplo correto:
Você PODE mexer APENAS nos seguintes arquivos:

- src/marketing/services/AIService.ts
- src-tauri/src/main.rs
E logo depois:
Você NÃO PODE mexer em nenhum outro arquivo.
Isso cria barreira cognitiva no modelo.
3️⃣ SEMPRE declarar o que ELE NÃO PODE FAZER
Isso é mais importante do que dizer o que pode.
Sempre inclua um bloco tipo:
REGRAS ABSOLUTAS:
❌ NÃO criar novos arquivos
❌ NÃO rodar build
❌ NÃO criar configs globais
❌ NÃO tentar corrigir erros não solicitados
❌ NÃO otimizar código
❌ NÃO sugerir melhorias
❌ NÃO criar diretórios via shell
❌ Diretórios só podem existir se já estiverem presentes
📌 Sem isso, ele vai tentar ser útil.
4️⃣ PROIBIR explicitamente “ações auxiliares”
Este foi o seu bug com o tsconfig.json.
O Gemini pensou:
“O build falhou, então vou criar o tsconfig.”
Você deveria sempre incluir:
❌ NÃO executar comandos auxiliares
❌ NÃO rodar build para validação
❌ NÃO criar arquivos de configuração para ‘ajudar’
Se isso não estiver escrito, ele considera ação legítima.
5️⃣ USAR “TAREFA ÚNICA” (isso é crítico)
❌ Errado:
“Integre o Gemini e garanta que funcione”
✅ Correto:
“TAREFA ÚNICA: Criar o arquivo X com o conteúdo Y.”
Por quê?
Tarefas abertas → decisões autônomas
Tarefa única → execução mecânica
6️⃣ PROIBIR DECISÃO TÉCNICA
Sempre inclua algo como:
❌ NÃO tomar decisões técnicas
❌ NÃO escolher alternativas
❌ NÃO adaptar a solução
IA não entende hierarquia de decisão, só padrões.
7️⃣ DEFINIR A SAÍDA ESPERADA (FORMATO)
Isso força o modelo a parar.
Exemplo:
SAÍDA ESPERADA:
- Lista de arquivos alterados
- Trechos exatos modificados
- Confirmação de que nada além disso foi tocado
Sem isso, ele continua operando.
8️⃣ USAR LINGUAGEM “LEGAL”, NÃO CONVERSACIONAL
❌ Evite:
“Vamos fazer…”
“A ideia é…”
“Pode tentar…”
✅ Use:
“EXECUTE”
“REMOVER”
“ADICIONAR”
“NÃO FAZER”
O Gemini responde melhor a ordens formais, não a conversa.
9️⃣ BLOQUEAR “AUTO-VALIDAÇÃO”
Nunca deixe ele validar o próprio trabalho rodando build.
Inclua sempre:
❌ NÃO validar execução
❌ NÃO testar
❌ NÃO rodar build
❌ NÃO rodar dev server
Caso contrário:
ele executa
falha
tenta corrigir
entra em loop destrutivo
10️⃣ SEMPRE pedir CONFIRMAÇÃO FINAL AUDITÁVEL
Isso cria responsabilidade.
Exemplo:
Ao final, confirme explicitamente:
- Nenhum arquivo novo foi criado
- Nenhum arquivo fora do escopo foi tocado
- Nenhuma config global foi alterada
Isso reduz drasticamente ações ocultas.
🧨 ERRO CLÁSSICO A EVITAR (O SEU CASO)
Você fez tudo certo menos isso:
❌ Você não proibiu:
criação de config global
execução de build
ação corretiva autônoma
Resultado:
Gemini criou tsconfig.json
mudou o comportamento do bundler
expôs um bug latente
não reportou isso corretamente
👉 Isso não é falha sua — é aprendizado de governança.
🧠 MODELO MENTAL CORRETO
Pense no Gemini como:
❌ um dev júnior? → NÃO
❌ um arquiteto? → NÃO
✅ um robô obediente que tenta “agradar”
Você precisa:
tirar autonomia
tirar iniciativa
deixar só execução
🛡️ REGRA FINAL (ESSENCIAL)
Quanto mais crítico o sistema,
menos “inteligência” você permite na IA operadora.
Inteligência → fica no design, documentação, planejamento
Execução → fica cego, limitado e auditável
