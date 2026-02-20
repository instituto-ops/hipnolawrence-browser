import pytesseract
from PIL import Image

class VisionOCR:
    def extract_elements(self, image_path: str) -> list:
        image = Image.open(image_path)
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
        
        elements = []
        n_boxes = len(data['text'])
        for i in range(n_boxes):
            text = data['text'][i].strip()
            if not text:
                continue
            
            element = {
                'text': text,
                'x': data['left'][i],
                'y': data['top'][i],
                'width': data['width'][i],
                'height': data['height'][i]
            }
            elements.append(element)
            
        return elements
