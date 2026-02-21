import os
import json
import uuid
import math
import ollama

class MemoryManager:
    """
    Hipocampo Híbrido v3:
    1. Memória Vetorial (RAG) nativa via JSON/Cosine (Sem ChromaDB).
    2. Memória Muscular (Fast Path) para automação determinística.
    """
    def __init__(self):
        # Configuração RAG (Vetores)
        self.db_path = os.path.join(os.getcwd(), "data", "library_db.json")
        self.embed_model = "nomic-embed-text"
        self.collection = []
        self._load_db()

        # Configuração Fast Path (Cache de Ações - Stagehand)
        self.cache_path = os.path.join(os.getcwd(), "data", "action_cache.json")
        self.action_cache = {}
        self._load_cache()

    # --- MÉTODOS DE RAG (VETORES) ---
    def _load_db(self):
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, "r", encoding="utf-8") as f:
                    self.collection = json.load(f)
            except: self.collection = []

    def _save_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(self.collection, f, indent=4)

    def get_embedding(self, text):
        try:
            response = ollama.embeddings(model=self.embed_model, prompt=text)
            return response["embedding"]
        except: return []

    def cosine_similarity(self, vec1, vec2):
        dot = sum(a * b for a, b in zip(vec1, vec2))
        mag1 = math.sqrt(sum(a * a for a in vec1))
        mag2 = math.sqrt(sum(b * b for b in vec2))
        return dot / (mag1 * mag2) if mag1 * mag2 > 0 else 0

    def add_knowledge(self, text, source="maestro_chat"):
        if not text.strip(): return
        vec = self.get_embedding(text)
        if not vec: return
        self.collection.append({
            "id": str(uuid.uuid4()), "text": text, "embedding": vec, "source": source
        })
        self._save_db()

    def query_knowledge(self, query_text, n_results=2):
        q_vec = self.get_embedding(query_text)
        if not q_vec or not self.collection: return []
        results = [(self.cosine_similarity(q_vec, d["embedding"]), d["text"]) for d in self.collection]
        results.sort(key=lambda x: x[0], reverse=True)
        return [text for sim, text in results[:n_results] if sim > 0.3]

    # --- MÉTODOS DE FAST PATH (CACHE DETERMINÍSTICO) ---
    def _load_cache(self):
        if os.path.exists(self.cache_path):
            try:
                with open(self.cache_path, "r", encoding="utf-8") as f:
                    self.action_cache = json.load(f)
            except: self.action_cache = {}

    def _save_cache(self):
        os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
        with open(self.cache_path, "w", encoding="utf-8") as f:
            json.dump(self.action_cache, f, indent=4)

    def save_action(self, url_base, command, action_data):
        """Salva um XPath funcional para um comando específico nesta URL."""
        key = f"{url_base}|{command.lower()}"
        self.action_cache[key] = action_data
        self._save_cache()

    def get_action(self, url_base, command):
        """Recupera a ação salva para execução instantânea."""
        return self.action_cache.get(f"{url_base}|{command.lower()}")
