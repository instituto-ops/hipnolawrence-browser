import os
import base64
import json
import urllib.request
import urllib.error

class VisionManager:
    """
    Gerencia a comunicação com a API local do Ollama para análise de imagens.
    """

    def __init__(self, host="http://localhost:11434", model="moondream"):
        self.host = host
        self.model = model
        self.api_url = f"{self.host}/api/generate"

    def _encode_image(self, image_path):
        """
        Lê e converte a imagem para Base64.
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Imagem não encontrada: {image_path}")

        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            raise Exception(f"Erro ao converter imagem em Base64: {e}")

    def analyze_screenshot(self, image_path, prompt="Descreva esta imagem em detalhes."):
        """
        Envia a imagem para o Ollama (modelo moondream) e retorna a descrição.
        """
        try:
            print(f"Codificando imagem: {image_path}")
            image_base64 = self._encode_image(image_path)
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "images": [image_base64],
                "stream": False  # Receber resposta completa de uma vez
            }

            data = json.dumps(payload).encode('utf-8')
            
            print(f"Enviando para Ollama ({self.model})...")
            req = urllib.request.Request(
                self.api_url,
                data=data,
                headers={'Content-Type': 'application/json'}
            )

            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                if 'response' in result:
                    return result['response']
                else:
                    return f"Resposta inesperada do Ollama: {result}"

        except urllib.error.URLError as e:
            return f"Erro de conexão com o Ollama: {e}. Verifique se o serviço está rodando."
        except Exception as e:
            return f"Erro ao analisar a imagem: {e}"

if __name__ == "__main__":
    # Teste rápido se executado diretamente
    print("Módulo VisionManager carregado.")
