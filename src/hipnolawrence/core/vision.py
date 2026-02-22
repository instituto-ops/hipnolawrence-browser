import os
import base64
import json
import httpx
import logging

logger = logging.getLogger("HipnoLawrence.Vision")

class VisionManager:
    """
    Gerencia a comunicação com a API local do Ollama para análise de imagens.
    Versão Assíncrona.
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

    async def analyze_screenshot(self, image_path, prompt="Descreva esta imagem em detalhes."):
        """
        Envia a imagem para o Ollama (modelo moondream) e retorna a descrição.
        """
        try:
            logger.info(f"Codificando imagem: {image_path}")
            image_base64 = self._encode_image(image_path)
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "images": [image_base64],
                "stream": False
            }

            logger.info(f"Enviando para Ollama ({self.model})...")
            async with httpx.AsyncClient(timeout=180.0) as client:
                response = await client.post(self.api_url, json=payload)
                response.raise_for_status()
                result = response.json()
                
                if 'response' in result:
                    return result['response']
                else:
                    return f"Resposta inesperada do Ollama: {result}"

        except Exception as e:
            return f"Erro ao analisar a imagem: {e}"

if __name__ == "__main__":
    # Teste rápido se executado diretamente
    print("Módulo VisionManager carregado.")
