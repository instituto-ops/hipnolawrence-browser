import json
import urllib.request
import urllib.error
import sys
import os

try:
    from hipnolawrence.core.memory import MemoryManager
except ImportError:
    from src.hipnolawrence.core.memory import MemoryManager

class Brain:
    def __init__(self, host="http://localhost:11434", model="llama3.2"):
        self.host = host
        self.model = model
        self.memory = MemoryManager()
        # BIBLIOTECA DE ATALHOS (Navegação Rápida e OSINT)
        self.library = {
            "google ads": "https://ads.google.com/aw/overview",
            "minha conta": "https://ads.google.com/aw/overview",
            "doctoralia": "https://www.google.com.br/search?q=site:doctoralia.com.br+psicologo+goiania",
            "instagram": "https://www.instagram.com/",
            "business": "https://business.google.com/br/google-ads/",
            "whatsapp": "https://web.whatsapp.com/"
        }

    def process_command(self, user_input, dom_elements=None, current_url="", history=""):
        user_input_lower = user_input.lower()
        if dom_elements is None: dom_elements = []

        if current_url:
            cached_action = self.memory.get_action(current_url.split("?")[0], user_input)
            if cached_action: return {"intent": "FAST_ACT", "args": cached_action}

        for key, url in self.library.items():
            if key in user_input_lower and any(v in user_input_lower for v in ["abra", "acesse", "vá"]):
                return {"intent": "NAVIGATE", "args": {"url": url}}

        dom_map = ""
        if dom_elements:
            dom_map = "DADOS EXTRAÍDOS DA TELA (Use para análise):\n"
            for el in dom_elements[:60]:
                dom_map += f"[{el['id']}] {el['text']}\n"

        relevant_mem = self.memory.query_knowledge(user_input)
        context = "\n".join(relevant_mem) if relevant_mem else "Sem diretrizes extras."

        # DIRETRIZ DE IDENTIDADE E GROUNDING
        system_instructions = (
            "PERSONA E IDENTIDADE: Você é o Analista Estratégico de Elite (HipnoLawrence). "
            "Você trabalha PARA o Dr. Victor Lawrence Bernardes Santana (Psicólogo Clínico, CRP 09/012681, Goiânia). "
            "A pegada digital dele (O Maestro) inclui: hipnolawrence.com, instagram.com/hipnolawrence, "
            "doctoralia.com.br/victor-lawrence-bernardes-santana, lattes.cnpq.br/7486371353673780 e WhatsApp Oficial. "
            "Se for pedido um diagnóstico de posicionamento, procure por esses links e destaque o domínio dele nos resultados.\n\n"
            "REGRA DE OURO (GROUNDING): Você NÃO PODE inventar métricas ou nomes. "
            "Baseie-se EXCLUSIVAMENTE no mapa 'DADOS EXTRAÍDOS DA TELA' abaixo. "
            "Se não encontrar a resposta, diga que os dados não estão visíveis.\n\n"
            "CONHECIMENTO DA BIBLIOTECA:\n" + context + "\n\n"
            "INTENÇÕES PERMITIDAS:\n"
            "- ACT: {\"intent\": \"ACT\", \"args\": {\"id\": <id numérico>, \"action\": \"click|type\"}}\n"
            "- EXTRACT: {\"intent\": \"EXTRACT\", \"args\": {\"data\": \"<Relatório baseado nos dados extraídos>\"}}\n"
            "- ASK_VISION: {\"intent\": \"ASK_VISION\", \"args\": {\"question\": \"<pergunta>\"}}\n"
            "- REPLY: {\"intent\": \"REPLY\", \"args\": {\"text\": \"<resposta>\"}}\n"
        )
        
        full_prompt = f"{system_instructions}\n\n{dom_map}\n\nUsuário: {user_input}"

        try:
            url = self.host + "/api/generate"
            data = {"model": self.model, "prompt": full_prompt, "stream": False, "format": "json"}
            req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                action = json.loads(result.get("response", "{}"))
                
                if any(w in user_input_lower for w in ["diagnóstico", "análise", "roi"]) and action.get("intent") == "REPLY":
                    action["intent"] = "EXTRACT"
                    action["args"] = {"data": action["args"].get("text", "Iniciando análise...")}
                
                return action
        except: return {"intent": "REPLY", "args": {"text": "Erro no processamento neural."}}
