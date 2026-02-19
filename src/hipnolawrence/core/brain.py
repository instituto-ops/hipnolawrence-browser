import json
import urllib.request
import urllib.error

class BrainManager:
    """
    Cérebro do assistente: processa linguagem natural e define intenções.
    Modelo: llama3.2:1b (leve e rápido para respostas locais).
    """
    def __init__(self, host="http://localhost:11434", model="llama3.2:1b"):
        self.host = host
        self.model = model
        self.api_url = f"{self.host}/api/generate"
        self.system_prompt = (
            "Você é HipnoLawrence, um assistente de navegação perspicaz e objetivo. "
            "Seu objetivo é analisar o comando do usuário e retornar EXCLUSIVAMENTE um JSON válido. "
            "Campos do JSON: "
            "1. 'intent': Uma das opções [VER, IR_PARA, CONVERSAR, CLICAR, STATUS, SAIR]. "
            "2. 'response': Uma resposta curta e natural para o usuário (máx 2 frases). "
            "3. 'args': Um objeto com parâmetros se necessário (ex: {'url': '...'} para IR_PARA, {'text': '...'} para CLICAR). "
            "Se o usuário pedir para analisar/ver/olhar a tela, intent é VER. "
            "Se pedir para ir a um site, intent é IR_PARA. "
            "Se quiser conversar/perguntar algo geral, intent é CONVERSAR. "
            "Se quiser clicar em algo, intent é CLICAR. "
            "Se disser tchau/sair, intent é SAIR. "
            "Responda APENAS com o JSON, sem markdown ou explicações extras."
        )

    def process_command(self, user_input):
        """
        Envia o comando para o Ollama e retorna a intenção estruturada.
        """
        prompt = f"Comando do usuário: '{user_input}'"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": self.system_prompt,
            "stream": False,
            "format": "json"  # Força resposta JSON no modo JSON do Ollama
        }

        try:
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(
                self.api_url,
                data=data,
                headers={'Content-Type': 'application/json'}
            )

            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                response_text = result.get('response', '{}')
                
                # Tenta parsear o JSON retornado pelo modelo
                try:
                    return json.loads(response_text)
                except json.JSONDecodeError:
                    # Fallback se o modelo falhar em gerar JSON limpo
                    print(f"Erro ao parsear JSON do cérebro. Resposta crua: {response_text}")
                    return {
                        "intent": "CONVERSAR",
                        "response": "Desculpe, tive um pensamento confuso. Pode repetir?",
                        "args": {}
                    }

        except Exception as e:
            return {
                "intent": "CONVERSAR",
                "response": f"Erro de conexão neural: {str(e)}",
                "args": {}
            }
