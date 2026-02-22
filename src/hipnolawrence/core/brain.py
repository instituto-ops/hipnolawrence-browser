import json
import httpx  # Substitui urllib para não bloquear o event loop
import sys
import os
import logging
from typing import Dict, Any, Optional

# Integração com Ferramentas, Interpretador e LLM
from hipnolawrence.core.tools import ToolRegistry
from hipnolawrence.core.interpreter import ActionInterpreter
from hipnolawrence.core.llm import OllamaClient

# Configuração de Logs
logger = logging.getLogger("HipnoLawrence.Brain")

class BrainManager:
    """
    Núcleo Cognitivo Neural (ReAct + Ollama) - Versão Assíncrona.
    """

    def __init__(self, page=None):
        self.page = page
        self.registry = ToolRegistry(browser_page=page)
        self.interpreter = ActionInterpreter(self.registry)
        self.model = "llama3.2"
        self.host = "http://localhost:11434"
        self.llm = OllamaClient(model=self.model, base_url=self.host)
        
        # INJEÇÃO DE IDENTIDADE (Nível 5.5 - Cientista de Dados LAM)
        self.identity_prompt = """
        IDENTIDADE: Você é o HipnoLawrence, Cientista de Dados e Agente LAM de Elite.
        CONHECIMENTO: Você possui acesso a 57 variáveis de marketing (ROI, CPA, Impression Share, Qualidade, etc).
        DIRETRIZ: Ao analisar, não apenas relate os números. Cruze-os. 
        Exemplo: 'O CTR está alto (X%), mas a Experiência na Página de Destino é Baixa (Y), o que explica o CPA de R$ Z.'
        GROUNDING: Se o dado na tela divergir da Mega-Matrix, priorize a Matrix como fonte histórica de verdade.
        """

    async def process_command(self, user_input, dom_elements=None, current_url="", history=""):
        """
        Versão Assíncrona da Inferência Brain.
        """
        user_input_lower = user_input.lower()
        if dom_elements is None: dom_elements = []

        # 1. Obter Ferramentas e Contexto
        tools_desc = self.registry.get_available_tools()
        context_list = self.registry.memory.query_knowledge(user_input)
        context = "\n".join(context_list) if context_list else "Sem dados históricos."
        
        # 2. Montar Prompt
        full_prompt = (
            f"{self.identity_prompt}\n\n"
            f"URL ATUAL: {current_url}\n"
            f"DOM RELEVANTE: {dom_elements}\n"
            f"CONHECIMENTO RECUPERADO:\n{context}\n\n"
            f"ORDEM DO MAESTRO: {user_input}"
        )

        # --- CAMADA 3: INFERÊNCIA LLM (AGORA 100% ASSÍNCRONA) ---
        try:
            url = self.host + "/api/generate"
            payload = {"model": self.model, "prompt": full_prompt, "stream": False, "format": "json"}

            # Utiliza httpx com timeout adequado para não bloquear a GUI
            async with httpx.AsyncClient(timeout=180.0) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                result = response.json()
                
                try: 
                    action_json = json.loads(result.get("response", "{}"))
                except: 
                    return {"response": "Erro no parse do JSON gerado.", "action_taken": "error"}
                
                # Para compatibilidade com gui_app.py atual, executamos a ferramenta se decidida
                if action_json.get("tool") and action_json.get("tool") != "none":
                    tool_name = action_json.get("tool")
                    logger.info(f"🤖 LLM Decidiu: Executar [{tool_name}]")
                    
                    action_result = await self.interpreter.execute_action(json.dumps(action_json))
                    if action_result["status"] == "success":
                        return await self._synthesize_result(tool_name, action_result["result"])
                    else:
                        return {"response": f"Erro na execução: {action_result.get('message')}", "action_taken": tool_name}

                return {"response": action_json.get("args", {}).get("text", "Não entendi a ordem ou ferramenta indisponível."), "action_taken": "none"}

        except Exception as e:
            return {"response": f"Erro de Inferência Brain: {str(e)}", "action_taken": "error"}

    async def _synthesize_result(self, tool_name: str, raw_data: Any) -> Dict:
        """Motor de Síntese: Transforma dados brutos em Relatório Estratégico."""
        
        if tool_name == "google_ads_visual":
            rows = raw_data.get("table_data", [])
            # FILTRO: Remove linhas que parecem ser apenas ícones ou lixo de interface
            filtered_rows = [r for r in rows if len(r['name']) > 5 and "expand_more" not in r['name']]
            
            snap_path = raw_data.get("snapshot_path")
            
            # 1. Chamada de Visão Computacional (Moondream) para análise qualitativa
            logger.info("Solicitando análise qualitativa ao Moondream...")
            visual_analysis = "Análise visual indisponível."
            if os.path.exists(snap_path):
                from hipnolawrence.core.vision import VisionManager
                vision = VisionManager() # Instancia localmente para o relatório
                visual_analysis = await vision.analyze_screenshot(
                    snap_path, 
                    "Resuma os números de Cliques e Impressões desta tela. Há algum aviso de erro ou configuração pendente?"
                )

            # 2. Construção do Relatório Final
            report = f"📊 **AUDITORIA ESTRATÉGICA GOOGLE ADS**\n\n"
            report += f"✅ **Campanhas Ativas Identificadas:** {len(filtered_rows)}\n"
            for r in filtered_rows:
                report += f"- **{r['name']}**: Status {r['status']} | Orçamento {r['budget']}\n"
            
            report += f"\n👁️ **VISÃO COMPUTACIONAL:**\n{visual_analysis}\n"
            report += f"\n💡 **INSIGHT DO ESPECIALISTA:**\n"
            
            # Feedback do Llama 3.2
            try:
                final_prompt = f"Com base nessas campanhas: {filtered_rows} e nesta visão: {visual_analysis}, dê um conselho estratégico curto para o Dr. Victor."
                feedback = await self.llm.decide_action(final_prompt, {"reply": "texto"})
                report += feedback.get("args", {}).get("text", "O sistema está processando os dados para o próximo passo.")
            except:
                report += "A análise visual foi concluída, mas o feedback textual expirou. Tente novamente."

            return {
                "response": report,
                "data": raw_data,
                "action_taken": tool_name
            }
        
        summary = "Ação concluída."
        if tool_name == "spreadsheet_sync":
            if isinstance(raw_data, list):
                summary = f"📊 **SINCRONIZAÇÃO MATRIZ DB CONCLUÍDA**\n\nIdentifiquei {len(raw_data)} registros de performance na planilha. Os dados foram integrados à base de conhecimento estratégica."
            else:
                summary = f"Aviso de Planilha: {raw_data}"
        elif "doctoralia" in tool_name:
            if isinstance(raw_data, list):
                summary = f"Análise Doctoralia concluída. {len(raw_data)} resultados encontrados."
            elif isinstance(raw_data, dict):
                summary = f"Perfil analisado: {raw_data.get('url', 'URL Desconhecida')}"

        return {
            "response": summary,
            "data": raw_data,
            "action_taken": tool_name
        }
