import os
import sys

# Garante acesso ao core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

try:
    from hipnolawrence.core.memory import MemoryManager
except ImportError:
    from src.hipnolawrence.core.memory import MemoryManager

def ingest():
    memory = MemoryManager()
    library_path = os.path.join(os.getcwd(), "data", "library")
    
    if not os.path.exists(library_path):
        os.makedirs(library_path)
        print(f"Pasta criada em {library_path}. Coloque seus arquivos .txt lá.")
        return

    files = [f for f in os.listdir(library_path) if f.endswith(".txt")]
    
    if not files:
        print("Nenhum arquivo .txt encontrado para ingestão.")
        return

    for file_name in files:
        path = os.path.join(library_path, file_name)
        print(f"📖 Lendo {file_name}...")
        
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            # Quebra por parágrafos para não estourar o limite de contexto
            paragraphs = [p.strip() for p in content.split('\n\n') if len(p.strip()) > 10]
            
            for p in paragraphs:
                memory.add_knowledge(p, source=f"file:{file_name}")
                
    print("✅ Ingestão concluída. Sua biblioteca de inteligência foi atualizada.")

if __name__ == "__main__":
    ingest()
