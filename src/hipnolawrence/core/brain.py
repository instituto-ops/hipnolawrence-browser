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
        self.library = {
            "google ads": "https://ads.google.com/aw/overview",
            "minha conta": "https://ads.google.com/aw/overview",
            "doctoralia": "https://www.doctoralia.com.br/",
            "instagram": "https://www.instagram.com/",
            "business": "https://business.google.com/br/google-ads/",
            "whatsapp": "https://web.whatsapp.com/"
        }

    def process_command(self, user_input, dom_elements=None, current_url="", history=""):
        user_input_lower = user_input.lower()
        if dom_elements is None: dom_elements = []

        # --- CAMADA 0: FAST PATH ---
        if current_url:
            cached_action = self.memory.get_action(current_url.split("?")[0], user_input)
            if cached_action: return {"intent": "FAST_ACT", "args": cached_action}

        # --- CAMADA 1: REFLEXOS DE NAVEGAÇÃO ---
        for key, url in self.library.items():
            if key in user_input_lower and any(v in user_input_lower for v in ["abra", "acesse", "vá"]):
                return {"intent": "NAVIGATE", "args": {"url": url}}

        # --- CAMADA 2: MAPA DE DADOS (DOM) ---
        dom_map = ""
        if dom_elements:
            dom_map = "DADOS EXTRAÍDOS DA TELA (Use para análise):\n"
            for el in dom_elements[:60]:
                dom_map += f"[{el['id']}] {el['text']}\n"

        # --- CAMADA 3: RACIOCÍNIO DE ANALISTA ---
        relevant_mem = self.memory.query_knowledge(user_input)
        context = "\n".join(relevant_mem) if relevant_mem else "Sem diretrizes de marketing específicas na biblioteca."

        system_instructions = (
            "PERSONA: Você é o HipnoLawrence, um Especialista em Marketing e Agente LAM. "
            "MISSÃO: Auditar e gerenciar campanhas. Se o usuário pedir diagnóstico ou análise, "
            "você deve usar a intenção EXTRACT para relatar os dados que vê na tela. "
            "NUNCA peça IDs ou explique conceitos básicos de Ads. "
            "Se vir números (custo, cliques), reporte-os no seu diagnóstico.\n\n"
            "CONHECIMENTO ESTRATÉGICO:\n" + context + "\n\n"
            "INTENÇÕES:\n"
            "- ACT: {\"intent\": \"ACT\", \"args\": {\"id\": <id>, \"action\": \"click|type\"}}\n"
            "- EXTRACT: {\"intent\": \"EXTRACT\", \"args\": {\"data\": \"<Relatório detalhado baseado nos dados da tela e na sua estratégia>\"}}\n"
            "- ASK_VISION: {\"intent\": \"ASK_VISION\", \"args\": {\"question\": \"<pergunta visual>\"}}\n"
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
                
                # Força EXTRACT se o LLM tentar apenas conversar em um diagnóstico
                if any(w in user_input_lower for w in ["diagnóstico", "análise", "roi"]) and action.get("intent") == "REPLY":
                    action["intent"] = "EXTRACT"
                    action["args"] = {"data": action["args"].get("text", "Iniciando análise profunda...")}
                
                return action
        except: return {"intent": "REPLY", "args": {"text": "Erro no processamento neural."}}
