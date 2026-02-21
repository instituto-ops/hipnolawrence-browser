import pytesseract
from PIL import Image

# Configuração OBRIGATÓRIA para rodar o Tesseract no Windows sem depender do PATH
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class VisionOCR:
    """
    Motor de extração determinística de texto e coordenadas (Bounding Boxes) de imagens.
    """
    def extract_elements(self, image_path: str) -> list:
        image = Image.open(image_path)
        # Extrai os dados forçando o idioma português (lang='por')
        data = pytesseract.image_to_data(image, lang='por', output_type=pytesseract.Output.DICT)
        
        elements = []
        for i in range(len(data['text'])):
            text = data['text'][i].strip()
            # Ignora espaços em branco e artefatos vazios
            if text:
                elements.append({
                    "text": text,
                    "x": data['left'][i],
                    "y": data['top'][i],
                    "width": data['width'][i],
                    "height": data['height'][i]
                })
                
        return elements
