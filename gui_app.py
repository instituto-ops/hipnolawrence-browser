import customtkinter as ctk
import asyncio
import threading
import sys
import os
import json
from datetime import datetime
from tkinter import filedialog
from PyPDF2 import PdfReader
from docx import Document

# Garante que o diretório src esteja no path para chamadas internas
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

# Imports internos com tratamento de erro
try:
    from hipnolawrence.core.browser import BrowserManager
    from hipnolawrence.core.brain import BrainManager
    from hipnolawrence.core.dom_observer import DOMObserver
except ImportError as e:
    print(f"Erro de Importação Interna: {e}")

class HipnoLawrenceGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("HipnoLawrence OS - Neural Console v5.1 (Restaurado)")
        self.geometry("1000x800")
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- VARIÁVEIS DE ENGINE ---
        self.browser = None
        self.brain = None
        self.dom_observer = None
        self.loop = None

        # --- SIDEBAR (MENU DE FERRAMENTAS) ---
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0)
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        
        self.logo = ctk.CTkLabel(self.sidebar, text="HIPNOLAWRENCE", font=ctk.CTkFont(size=22, weight="bold"))
        self.logo.pack(pady=20)

        # SEÇÃO: GOOGLE ADS COMMAND CENTER
        ctk.CTkLabel(self.sidebar, text="GOOGLE ADS CENTER", text_color="#4285F4", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 5))
        ctk.CTkButton(self.sidebar, text="📊 Diagnóstico Geral", command=lambda: self.external_command("Faça um diagnóstico completo desta tela do Google Ads.")).pack(pady=5, padx=20, fill="x")
        ctk.CTkButton(self.sidebar, text="💰 Analisar ROI/CPA", command=lambda: self.external_command("Analise o custo e conversões desta tela.")).pack(pady=5, padx=20, fill="x")
        ctk.CTkButton(self.sidebar, 
                      text="🔄 Sincronizar Matriz BD", 
                      fg_color="#0F9D58", # Verde Google
                      command=lambda: self.external_command("Sincronize os dados da Planilha NeuroStrategy")
                     ).pack(pady=5, padx=20, fill="x")

        # SEÇÃO: MARKET INTELLIGENCE (MACROS)
        ctk.CTkLabel(self.sidebar, text="MARKET INTELLIGENCE", text_color="#F4B400", font=ctk.CTkFont(weight="bold")).pack(pady=(20, 5))
        ctk.CTkButton(self.sidebar, text="🕵️ Radar Concorrência", command=self.run_macro_competitor).pack(pady=5, padx=20, fill="x")
        ctk.CTkButton(self.sidebar, text="🎯 Meu Posicionamento", command=self.run_macro_authority).pack(pady=5, padx=20, fill="x")

        # SEÇÃO: LIBRARY & TRAINING
        ctk.CTkLabel(self.sidebar, text="LIBRARY & TRAINING", text_color="gray", font=ctk.CTkFont(weight="bold")).pack(pady=(20, 5))
        ctk.CTkButton(self.sidebar, text="📚 Add à Biblioteca", command=self.tool_upload_docs).pack(pady=5, padx=20, fill="x")
        
        self.btn_reset = ctk.CTkButton(self.sidebar, text="🧹 Limpar Cache (FastPath)", fg_color="#444444", command=self.tool_clear_cache)
        self.btn_reset.pack(pady=20, padx=20, side="bottom", fill="x")

        # --- MAIN DISPLAY AREA ---
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(0, weight=3) # Chat
        self.container.grid_rowconfigure(1, weight=1) # Thought Box

        self.chat_display = ctk.CTkTextbox(self.container, state="disabled", font=("Roboto", 14), wrap="word")
        self.chat_display.grid(row=0, column=0, sticky="nsew", pady=(0, 10))

        # JANELA DE PENSAMENTO (THOUGHT BOX)
        self.thought_box = ctk.CTkTextbox(self.container, state="disabled", font=("Consolas", 12), fg_color="#0D0D0D", text_color="#00FF41", border_width=1, border_color="#333333")
        self.thought_box.grid(row=1, column=0, sticky="nsew")

        # INPUT BAR
        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        self.entry = ctk.CTkEntry(self.input_frame, placeholder_text="Maestro, digite sua ordem...")
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry.bind("<Return>", lambda e: self.send_command())
        self.btn_execute = ctk.CTkButton(self.input_frame, text="EXECUTAR", width=100, command=self.send_command)
        self.btn_execute.pack(side="right")

        # --- ENGINE INITIALIZATION ---
        self._initialize_async_engines()

    def _initialize_async_engines(self):
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self._run_async_loop, daemon=True).start()

    def _run_async_loop(self):
        asyncio.set_event_loop(self.loop)
        # Usa run_until_complete para o launch inicial
        self.loop.run_until_complete(self._init_engines())
        self.loop.run_forever()

    async def _init_engines(self):
        """Inicialização protegida."""
        self.append_thought("Iniciando Motores Neurais...")
        try:
            self.browser = BrowserManager()
            await self.browser.launch()
            self.brain = BrainManager(page=self.browser.page)
            self.brain.llm.model = "llama3.2"
            self.dom_observer = DOMObserver()
            self.append_thought("Motores Online. Sistema pronto.")
            self.append_message("Hipno", "Saudações, Maestro. O console v5.1 está operacional. Como posso servir à sua estratégia hoje?")
        except Exception as e:
            self.append_thought(f"Falha ao iniciar motores: {e}")

    def append_thought(self, msg):
        self.after(0, lambda: self._update_thought_ui(msg))

    def _update_thought_ui(self, msg):
        self.thought_box.configure(state="normal")
        self.thought_box.insert("end", f"[{datetime.now().strftime('%H:%M:%S')}] > {msg}\n")
        self.thought_box.see("end")
        self.thought_box.configure(state="disabled")

    def append_message(self, sender, text):
        def update():
            self.chat_display.configure(state="normal")
            ts = datetime.now().strftime("%H:%M")
            
            # Define cores por papel
            if sender == "Maestro":
                color = "#1f538d" # Azul
            elif sender == "Hipno":
                color = "#00FF41" # Verde Matrix
            else:
                color = "gray"

            # Adiciona a tag de cor sem tentar alterar a fonte (que causa o crash)
            tag_name = f"tag_{sender}"
            self.chat_display.tag_config(tag_name, foreground=color)
            
            icon = "👨💼" if sender == "Maestro" else "🤖"
            header = f"[{ts}] {icon} {sender.upper()}: "
            
            # Insere o cabeçalho com a tag de cor e o texto normalmente
            self.chat_display.insert("end", header, tag_name)
            self.chat_display.insert("end", f"{text}\n\n")
            
            self.chat_display.see("end")
            self.chat_display.configure(state="disabled")
        self.after(0, update)

    def run_async(self, coroutine):
        asyncio.run_coroutine_threadsafe(coroutine, self.loop)

    def external_command(self, cmd):
        self.entry.delete(0, "end")
        self.entry.insert(0, cmd)
        self.send_command()

    def run_macro_competitor(self):
        cmd = 'Navegue para https://www.google.com.br/search?q=site:doctoralia.com.br+psicologo+goiania e extraia dados dos concorrentes'
        self.append_message("Maestro", "[MACRO] Iniciar Radar de Concorrência")
        self.external_command(cmd)

    def run_macro_authority(self):
        cmd = 'Faça uma busca por "Victor Lawrence Bernardes Santana" e verifique meu posicionamento na 1ª página'
        self.append_message("Maestro", "[MACRO] Auditoria de Autoridade Digital")
        self.external_command(cmd)
        
    def tool_upload_docs(self):
        """Implementação da Ingestão Universal (PDF, DOCX, MD, TXT, CSV)."""
        files = filedialog.askopenfilenames(filetypes=[("Documentos", "*.txt *.pdf *.docx *.md *.csv")])
        if not files: return
        
        for f_path in files:
            ext = os.path.splitext(f_path)[1].lower()
            try:
                self.append_thought(f"Assimilando: {os.path.basename(f_path)}...")
                if ext == ".csv":
                    self.brain.registry.memory.add_csv_knowledge(f_path)
                    self.append_message("Sistema", f"Relatório CSV '{os.path.basename(f_path)}' integrado à inteligência.")
                elif ext == ".pdf":
                    text = ""
                    reader = PdfReader(f_path)
                    for page in reader.pages: text += page.extract_text() or ""
                    if text.strip(): self.brain.registry.memory.add_knowledge(text, source=os.path.basename(f_path))
                elif ext == ".docx":
                    doc = Document(f_path)
                    text = "\n".join([p.text for p in doc.paragraphs])
                    if text.strip(): self.brain.registry.memory.add_knowledge(text, source=os.path.basename(f_path))
                else: # TXT, MD
                    with open(f_path, "r", encoding="utf-8", errors="ignore") as f:
                        text = f.read()
                    if text.strip(): self.brain.registry.memory.add_knowledge(text, source=os.path.basename(f_path))
                
                self.append_thought("Assimilado com sucesso.")
            except Exception as e:
                self.append_message("Sistema", f"Falha ao ler {os.path.basename(f_path)}: {e}")

    def tool_clear_cache(self):
        """Limpa action_cache.json."""
        try:
            cache_path = self.brain.registry.memory.cache_path
            if os.path.exists(cache_path):
                os.remove(cache_path)
            self.brain.registry.memory.action_cache = {}
            self.append_thought("🧹 Cache de automação (FastPath) limpo com sucesso.")
        except Exception as e:
            self.append_thought(f"❌ Erro ao limpar cache: {e}")

    async def _sync_spreadsheet_data(self):
        """Sincronização Profunda: Mapeia Performance, Intenção e Leilão."""
        try:
            self.append_thought("📡 Iniciando Sincronização Profunda (Performance + Intenção + Leilão)...")
            from hipnolawrence.core.spreadsheet import SpreadsheetManager
            sm = SpreadsheetManager()
            
            if sm.connect():
                matrix = sm.get_full_matrix()
                if matrix:
                    # 1. Processa Performance (Gerador de Fatos Dinâmicos)
                    for row in matrix['performance']:
                        details = ", ".join([f"{k}: {v}" for k, v in row.items() if v])
                        fact = f"Performance Mega-Report: {details}"
                        self.brain.registry.memory.add_knowledge(fact, source="sheet_perf")
                    
                    # 2. Processa Intenção (Fatos de Termos e CPA)
                    for row in matrix['demand']:
                        details = ", ".join([f"{k}: {v}" for k, v in row.items() if v])
                        fact = f"Estratégia/Intenção: {details}"
                        self.brain.registry.memory.add_knowledge(fact, source="sheet_demand")
                    
                    # 3. Processa Competitividade (Leilão)
                    for row in matrix['competitive']:
                        fact = f"Concorrência: Na campanha {row.get('Campanha')}, perdemos {row.get('Perda IS (Orçamento)')} de visualizações por falta de verba."
                        self.brain.registry.memory.add_knowledge(fact, source="sheet_comp")
                    
                    # 4. Processa Configurações (Mega-Matrix v2)
                    if matrix.get('config'):
                        for row in matrix['config']:
                            # Filtra apenas campos com valores para não poluir o prompt
                            active_data = {k: v for k, v in row.items() if v and v != '--'}
                            knowledge_chunk = f"AUDITORIA COMPLETA CAMPANHA {row.get('Campanha_ID', row.get('Campanha'))}: " + json.dumps(active_data)
                            self.brain.registry.memory.add_knowledge(knowledge_chunk, source="mega_matrix_v2")

                    self.append_message("Sistema", "Mega-Matrix Sincronizada. 57 variáveis integradas ao Cérebro.")
                    self.append_thought("✅ Sincronização profunda concluída com sucesso.")
                else:
                    self.append_message("Sistema", "Falha ao recuperar a matriz completa da planilha.")
            else:
                self.append_message("Sistema", "Erro de conexão com o Google Sheets. Verifique o service_account.json.")
        except Exception as e:
            self.append_thought(f"❌ ERRO NO SYNC: {e}")
            self.append_message("Sistema", f"Erro crítico na sincronização profunda: {e}")

    def send_command(self):
        """Envia a ordem do Maestro para o Cérebro."""
        cmd = self.entry.get().strip()
        if not cmd: return
        self.entry.delete(0, "end")
        self.append_message("Maestro", cmd)
        self.run_async(self.process_logic(cmd))

    async def process_logic(self, user_input):
        """Ciclo ReAct completo com monitoramento na Thought Box."""
        try:
            self.append_thought("Iniciando raciocínio...")
            
            if any(x in user_input.lower() for x in ["sincronize", "sincronizar"]):
                await self._sync_spreadsheet_data()
                return
            
            # 1. Radar DOM
            self.append_thought("📡 Mapeando Árvore de Acessibilidade...")
            dom_elements = await self.dom_observer.observe_page(self.browser.page)
            self.append_thought(f"👁️ {len(dom_elements)} elementos capturados.")

            # 2. Inferência
            self.append_thought("🧠 Consultando Cérebro (Ollama)...")
            result = await self.brain.process_intent(user_input)
            
            # 3. Resposta
            self.append_thought(f"✅ Ação Concluída: {result.get('action_taken')}")
            self.append_message("Hipno", result.get("response"))
            
        except Exception as e:
            self.append_thought(f"❌ ERRO: {e}")
            self.append_message("Sistema", f"Erro crítico: {e}")

if __name__ == "__main__":
    app = HipnoLawrenceGUI()
    app.mainloop()
