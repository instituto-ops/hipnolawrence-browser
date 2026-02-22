import logging
import json
import httpx
from typing import Dict, Any, Optional

logger = logging.getLogger("HipnoLawrence.LLM")

class OllamaClient:
    """
    Cliente para comunicação com modelos locais via Ollama.
    Especializado em:
    1. Raciocínio (Reasoning) para escolha de ferramentas.
    2. Formatação estrita de saída JSON (Action Output).
    """

    def __init__(self, model: str = "llama3.2", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = f"{base_url}/api/generate"
        self.timeout = 180.0  # Tempo limite para inferência

    async def decide_action(self, user_context: str, available_tools: Dict[str, str]) -> Dict[str, Any]:
        """
        Envia o contexto do usuário e as ferramentas disponíveis para o LLM.
        Retorna um dicionário com a ação escolhida.
        """
        
        # Prompt de Sistema (System Prompt) - Engenharia de Prompt para Agente
        tools_desc = json.dumps(available_tools, indent=2)
        system_prompt = f"""
        Você é o HipnoLawrence, um Agente de Navegação Autônomo.
        Sua missão é ajudar o usuário escolhendo a ferramenta correta para a tarefa.
        
        FERRAMENTAS DISPONÍVEIS:
        {tools_desc}
        
        REGRAS DE RESPOSTA:
        1. Você DEVE responder APENAS com um JSON válido.
        2. O JSON deve ter o formato: {{"tool": "nome_da_tool", "args": {{ "arg1": "valor" }} }}
        3. Se não souber o que fazer, responda com {{"tool": "none", "args": {{}} }}
        4. Não inclua explicações ou texto fora do JSON.
        
        Exemplo: Para "ver ranking de cardiologista em SP", responda:
        {{"tool": "doctoralia_ranking", "args": {{"specialty": "cardiologista", "city": "sao paulo"}} }}
        """

        payload = {
            "model": self.model,
            "prompt": f"USUÁRIO: {user_context}\nAGENTE (JSON):",
            "system": system_prompt,
            "stream": False,
            "format": "json"  # Força modo JSON do Ollama (se suportado pelo modelo)
        }

        try:
            async with httpx.AsyncClient() as client:
                logger.debug(f"Enviando prompt para Ollama ({self.model})...")
                response = await client.post(self.base_url, json=payload, timeout=self.timeout)
                response.raise_for_status()
                
                result = response.json()
                raw_response = result.get("response", "")
                
                logger.debug(f"Resposta bruta do LLM: {raw_response}")
                
                # Tenta parsear o JSON retornado
                try:
                    return json.loads(raw_response)
                except json.JSONDecodeError:
                    # Fallback: Tenta limpar o texto caso o modelo seja "falador"
                    logger.warning("LLM não retornou JSON puro. Tentando limpar...")
                    return self._fallback_json_parsing(raw_response)

        except Exception as e:
            logger.error(f"Erro na conexão com Ollama: {e}")
            return {"tool": "error", "args": {"message": str(e)}}

    def _fallback_json_parsing(self, text: str) -> Dict:
        """Tenta extrair JSON de texto sujo."""
        import re
        match = re.search(r"(\{.*\})", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except:
                pass
        return {"tool": "error", "args": {"raw": text}}
