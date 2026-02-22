import logging
import asyncio
import os
import json
from typing import Dict, Any, Optional

# Integração com Ferramentas, Interpretador e LLM
from hipnolawrence.core.tools import ToolRegistry
from hipnolawrence.core.interpreter import ActionInterpreter
from hipnolawrence.core.llm import OllamaClient

# Configuração de Logs
logger = logging.getLogger("HipnoLawrence.Brain")

class BrainManager:
    """
    Núcleo Cognitivo Neural (ReAct + Ollama).
    """

    def __init__(self, page=None):
        self.page = page
        self.registry = ToolRegistry(browser_page=page)
        self.interpreter = ActionInterpreter(self.registry)
        self.llm = OllamaClient(model="llama3.2")
        
        # INJEÇÃO DE IDENTIDADE (Nível 5.5 - Cientista de Dados LAM)
        self.identity_prompt = """
        IDENTIDADE: Você é o HipnoLawrence, Cientista de Dados e Agente LAM de Elite.
        CONHECIMENTO: Você possui acesso a 57 variáveis de marketing (ROI, CPA, Impression Share, Qualidade, etc).
        DIRETRIZ: Ao analisar, não apenas relate os números. Cruze-os. 
        Exemplo: 'O CTR está alto (X%), mas a Experiência na Página de Destino é Baixa (Y), o que explica o CPA de R$ Z.'
        GROUNDING: Se o dado na tela divergir da Mega-Matrix, priorize a Matrix como fonte histórica de verdade.
        """

    async def process_intent(self, user_input: str) -> Dict[str, Any]:
        """
        Ciclo Cognitivo Completo:
        1. Identifica Tools disponíveis.
        2. Consulta o LLM para decidir ação.
        3. Executa a ação via Interpreter.
        4. Retorna resultado.
        """
        logger.info(f"🧠 Cérebro processando (Neural): '{user_input}'")
        
        # 1. Obter Ferramentas Disponíveis
        tools_desc = self.registry.get_available_tools()
        
        # 2. Recuperar Conhecimento (RAG)
        context_list = self.registry.memory.query_knowledge(user_input)
        context = "\n".join(context_list) if context_list else "Nenhum dado histórico relevante encontrado."
        
        # 3. PENSAR (Decisão via Ollama)
        full_prompt = (
            f"{self.identity_prompt}\n\n"
            f"CONHECIMENTO RECUPERADO DA BIBLIOTECA:\n{context}\n\n"
            f"ORDEM DO MAESTRO: {user_input}"
        )
        
        decision = await self.llm.decide_action(full_prompt, tools_desc)
        
        if decision.get("tool") in ["none", "error", None]:
            return {
                "response": f"Não consegui decidir uma ação clara. (Erro: {decision.get('args')})",
                "action_taken": None
            }

        # 3. AGIR (Execução via Interpreter)
        tool_name = decision.get("tool")
        logger.info(f"🤖 LLM Decidiu: Executar [{tool_name}] com args {decision.get('args')}")
        
        # Serializa para o formato que o interpreter espera (string JSON)
        action_json_str = json.dumps(decision)
        action_result = await self.interpreter.execute_action(action_json_str)

        # 4. OBSERVAR (Síntese do Resultado)
        if action_result["status"] == "success":
            return await self._synthesize_result(tool_name, action_result["result"])
        else:
            return {
                "response": f"Erro na execução da ferramenta: {action_result.get('message')}",
                "action_taken": None
            }

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
                visual_analysis = vision.analyze_screenshot(
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
