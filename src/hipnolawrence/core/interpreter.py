import logging
import json
import re
from typing import Dict, Any, Optional
from hipnolawrence.core.tools import ToolRegistry

# Configuração de Logs
logger = logging.getLogger("HipnoLawrence.Interpreter")

class ActionInterpreter:
    """
    Tradutor de Intenções do Cérebro para Ferramentas Reais.
    Compatível com Arquitetura Visual/Comet (Sem APIs oficiais).
    """

    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    async def execute_action(self, llm_response: str) -> Dict[str, Any]:
        """
        Recebe uma string JSON do Brain e executa a ferramenta correspondente.
        
        Exemplo de entrada: '{"tool": "google_ads_visual", "args": {}}'
        """
        action_data = self._extract_json_block(llm_response)
        
        if not action_data:
            logger.warning("Nenhuma ação estruturada detectada na resposta do Cérebro.")
            return {"status": "no_action", "result": None}

        tool_name = action_data.get("tool")
        args = action_data.get("args", {})

        logger.info(f"⚡ Executando Ação: [{tool_name}] | Args: {args}")

        try:
            result = None
            
            # --- Roteamento Doctoralia ---
            if tool_name == "doctoralia_ranking":
                # Busca Direta (Comet Mode)
                if "specialty" in args and "city" in args:
                    result = await self.registry.run_doctoralia_scan(
                        specialty=args["specialty"], 
                        city=args["city"]
                    )
                else:
                    raise ValueError("Faltam argumentos 'specialty' ou 'city' para ranking.")

            elif tool_name == "doctoralia_serp":
                # Busca Indireta (Google SERP)
                if "query" in args:
                    result = await self.registry.run_doctoralia_serp(args["query"])
                else:
                    raise ValueError("Falta argumento 'query' para busca SERP.")

            elif tool_name == "doctoralia_profile":
                # Análise de Perfil Específico
                if "url" in args and self.registry.doctoralia:
                    result = await self.registry.doctoralia.analyze_competitor_profile(args["url"])
                else:
                    raise ValueError("URL não fornecida ou Doctoralia Tool indisponível.")

            # --- Roteamento Google Ads (Visual) ---
            elif tool_name == "google_ads_visual":
                # Extração via DOM e Screenshot
                # Não requer argumentos, pois lê a tela atual/dashboard
                result = await self.registry.run_ads_visual_extraction()

            else:
                return {"status": "error", "message": f"Ferramenta '{tool_name}' desconhecida ou não implementada."}

            return {"status": "success", "tool": tool_name, "result": result}

        except Exception as e:
            logger.error(f"❌ Erro Crítico na Execução da Ação: {e}", exc_info=True)
            return {"status": "error", "message": str(e)}

    def _extract_json_block(self, text: str) -> Optional[Dict]:
        """
        Tenta extrair um JSON válido de uma string que pode conter texto antes ou depois.
        """
        try:
            # Caso o texto já seja puramente JSON
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        try:
            # Procura por blocos Markdown ```json ... ```
            match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
            if match:
                return json.loads(match.group(1))
            
            # Procura pelo primeiro objeto JSON { ... }
            match_loose = re.search(r"(\{.*\})", text, re.DOTALL)
            if match_loose:
                return json.loads(match_loose.group(1))
                
        except json.JSONDecodeError:
            pass
            
        return None
