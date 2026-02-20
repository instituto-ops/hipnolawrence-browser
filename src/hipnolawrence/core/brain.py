import json
import urllib.request
import urllib.error

class Brain:
    """
    Processa a intenção do usuário usando um modelo LLM local (Ollama)
    e retorna comandos estruturados em JSON para o navegador autônomo.
    """
    def __init__(self, host="http://localhost:11434", model="llama3.2"):
        self.host = host
        self.model = model
        self.api_url = f"{self.host}/api/generate"

    def process_command(self, user_input: str, context: str = "") -> dict:
        """
        Envia o comando do usuário para o Ollama e retorna a intenção estruturada.
        """
        prompt = f"""
        Você é o cérebro de um navegador web autônomo. Sua tarefa é analisar o comando do usuário e retornar EXCLUSIVAMENTE um JSON com a intenção e os argumentos necessários.
        NÃO inclua markdown, explicações ou texto adicional. Apenas o JSON puro.

        Intenções permitidas:
        - NAVIGATE: Para abrir URLs ou sites. Args: "url" (string).
        - CLICK: Para clicar em elementos (botões, links, imagens). Args: "target" (descrição textual do elemento).
        - TYPE: Para digitar texto em campos. Args: "text" (o que digitar), "target" (onde digitar).
        - EXTRACT: Para ler ou extrair informações da página. Args: "info_to_extract" (o que buscar).
        - SCROLL: Para rolar a página. Args: "direction" ("up", "down"), "amount" (opcional).
        - ASK_VISION: Quando o usuário pede para "ver", "analisar" ou "descrever" algo visual na tela. Args: "question" (o que o usuário quer saber).
        - EXIT: Para fechar o navegador ou encerrar a sessão. Args: {}.

        Contexto atual da página (se houver): "{context}"

        Comando do usuário: "{user_input}"

        Responda APENAS com o JSON:
        """

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }

        try:
            req = urllib.request.Request(
                self.api_url, 
                data=json.dumps(payload).encode('utf-8'), 
                headers={'Content-Type': 'application/json'}
            )

            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                llm_response = result.get("response", "{}")
                
                # Tenta parsear a resposta do LLM como JSON
                try:
                    command_data = json.loads(llm_response)
                    # Normaliza chaves para minúsculo para consistência interna se necessário, 
                    # mas o prompt já pede estrutura específica.
                    return command_data
                except json.JSONDecodeError:
                    # Fallback se o LLM alucinar texto fora do JSON
                    return {
                        "intent": "ERROR", 
                        "args": {"error": "Falha no parse do JSON do LLM", "raw_response": llm_response}
                    }

        except urllib.error.URLError as e:
            return {
                "intent": "ERROR", 
                "args": {"error": f"Falha na conexão com Ollama: {e}"}
            }
        except Exception as e:
            return {
                "intent": "ERROR", 
                "args": {"error": f"Erro inesperado no Brain: {e}"}
            }
