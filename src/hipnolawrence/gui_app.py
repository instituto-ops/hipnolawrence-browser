import customtkinter as ctk
import asyncio
import threading
import sys
import os
from datetime import datetime
from tkinter import filedialog
from PyPDF2 import PdfReader
from docx import Document

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from hipnolawrence.core.browser import BrowserManager
from hipnolawrence.core.brain import Brain
from hipnolawrence.core.vision import VisionManager
from hipnolawrence.core.dom_observer import DOMObserver

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class HipnoLawrenceGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("HipnoLawrence OS - Neural Console v5.1 (Macros)")
        self.geometry("950x850")
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self, width=260, corner_radius=0)
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.logo = ctk.CTkLabel(self.sidebar, text="HIPNOLAWRENCE", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo.pack(pady=(20, 10))

        # ADS CENTER
        ctk.CTkLabel(self.sidebar, text="GOOGLE ADS CENTER", text_color="#4285F4", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        ctk.CTkButton(self.sidebar, text="📊 Diagnóstico Geral", command=lambda: self.external_command("Faça um diagnóstico completo desta tela do Google Ads. Extraia números exatos.")).pack(pady=5, padx=20, fill="x")
        ctk.CTkButton(self.sidebar, text="💰 Analisar ROI/CPA", command=lambda: self.external_command("Extraia os dados de custo e conversão reais da tela")).pack(pady=5, padx=20, fill="x")

        # MARKET INTELLIGENCE (MACROS)
        ctk.CTkLabel(self.sidebar, text="INTELIGÊNCIA DE MERCADO", text_color="#F4B400", font=ctk.CTkFont(weight="bold")).pack(pady=(15, 5))
        ctk.CTkButton(self.sidebar, text="🕵️ Radar Concorrência", command=self.btn_macro_radar).pack(pady=5, padx=20, fill="x")
        ctk.CTkButton(self.sidebar, text="🎯 Meu Posicionamento", command=self.btn_macro_posicionamento).pack(pady=5, padx=20, fill="x")

        # LIBRARY
        ctk.CTkLabel(self.sidebar, text="LIBRARY & TRAINING", text_color="gray", font=ctk.CTkFont(weight="bold")).pack(pady=(15, 5))
        ctk.CTkButton(self.sidebar, text="📚 Add à Biblioteca", command=self.tool_add_to_library).pack(pady=5, padx=20, fill="x")
        
        self.btn_reset = ctk.CTkButton(self.sidebar, text="🧹 Limpar Cache", fg_color="indianred", command=self.tool_clear_cache)
        self.btn_reset.pack(pady=20, padx=20, side="bottom", fill="x")

        # --- ÁREA PRINCIPAL ---
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(0, weight=3)
        self.main_container.grid_rowconfigure(1, weight=1)

        self.chat_display = ctk.CTkTextbox(self.main_container, state="disabled", font=("Roboto", 14), wrap="word")
        self.chat_display.grid(row=0, column=0, sticky="nsew", pady=(0, 10))

        self.thought_box = ctk.CTkTextbox(self.main_container, state="disabled", font=("Consolas", 12), fg_color="#1a1a1a", text_color="#00FF00", border_color="#333333", border_width=1)
        self.thought_box.grid(row=1, column=0, sticky="nsew")
        self.append_thought("Sistema inicializado. Motores neurais prontos.")

        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.grid(row=1, column=1, padx=10, pady=(0, 10), sticky="ew")
        
        self.entry = ctk.CTkEntry(self.input_frame, placeholder_text="Ordem direta...", font=("Roboto", 14))
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.entry.bind("<Return>", self.send_command)
        ctk.CTkButton(self.input_frame, text="Enviar", width=60, command=self.send_command).pack(side="right")

        self.browser = BrowserManager()
        self.brain = Brain()
        self.vision = VisionManager()
        self.dom_observer = DOMObserver()
        
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self.start_async_loop, daemon=True).start()
        self.run_async(self.browser.launch())

    def start_async_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def run_async(self, coro):
        asyncio.run_coroutine_threadsafe(coro, self.loop)

    def append_message(self, sender, text):
        self.chat_display.configure(state="normal")
        ts = datetime.now().strftime("%H:%M")
        icon = "👨💼" if sender == "Maestro" else "🤖" if sender == "Hipno" else "⚙️"
        self.chat_display.insert("end", f"[{ts}] {icon} {sender.upper()}: {text}\n\n")
        self.chat_display.see("end")
        self.chat_display.configure(state="disabled")

    def append_thought(self, text):
        self.thought_box.configure(state="normal")
        ts = datetime.now().strftime("%H:%M:%S")
        self.thought_box.insert("end", f"[{ts}] > {text}\n")
        self.thought_box.see("end")
        self.thought_box.configure(state="disabled")

    # --- SISTEMA DE MACROS ---
    def btn_macro_radar(self):
        self.append_message("Maestro", "[MACRO] Iniciar Radar de Concorrência")
        self.run_async(self.macro_radar())

    async def macro_radar(self):
        self.gui_callback_thought("⚙️ MACRO: Iniciando varredura OSINT de concorrência...")
        await self.browser.goto("https://www.google.com.br/search?q=site:doctoralia.com.br+psicologo+goiania")
        self.gui_callback_thought("⏳ Aguardando renderização do Google (3s)...")
        await asyncio.sleep(3)
        self.gui_callback_thought("📡 Forçando extração de dados do DOM...")
        await self.process_logic("Esta é uma tela do Google. Extraia os nomes dos psicólogos, suas especialidades e avaliações que aparecem nos resultados de busca.")

    def btn_macro_posicionamento(self):
        self.append_message("Maestro", "[MACRO] Analisar meu Posicionamento Digital")
        self.run_async(self.macro_posicionamento())

    async def macro_posicionamento(self):
        self.gui_callback_thought("⚙️ MACRO: Iniciando auditoria de pegada digital (Victor Lawrence)...")
        await self.browser.goto('https://www.google.com.br/search?q="Victor+Lawrence+Bernardes+Santana"+Psicologo+Goiania')
        self.gui_callback_thought("⏳ Aguardando renderização do Google (3s)...")
        await asyncio.sleep(3)
        self.gui_callback_thought("📡 Forçando auditoria do DOM...")
        await self.process_logic("Faça uma auditoria do meu posicionamento online nesta tela de resultados. Liste quais dos meus sites/redes estão aparecendo na primeira página.")

    # --- FERRAMENTAS BASE ---
    def tool_add_to_library(self):
        files = filedialog.askopenfilenames(filetypes=[("Docs", "*.txt *.md *.pdf *.docx *.csv"), ("All", "*.*")])
        if not files: return
        for f_path in files:
            ext = os.path.splitext(f_path)[1].lower()
            text = ""
            try:
                self.append_thought(f"Lendo: {os.path.basename(f_path)}")
                if ext == ".pdf":
                    reader = PdfReader(f_path)
                    for page in reader.pages: text += page.extract_text() or ""
                elif ext == ".docx":
                    doc = Document(f_path)
                    text = "\n".join([p.text for p in doc.paragraphs])
                else:
                    with open(f_path, "r", encoding="utf-8", errors="ignore") as f: text = f.read()
                
                if text.strip():
                    self.brain.memory.add_knowledge(text, source=os.path.basename(f_path))
                    self.append_message("Sistema", f"{os.path.basename(f_path)} memorizado.")
            except Exception as e: self.append_message("Sistema", f"Erro: {e}")

    def tool_clear_cache(self):
        if os.path.exists(self.brain.memory.cache_path):
            os.remove(self.brain.memory.cache_path)
            self.brain.memory.action_cache = {}
            self.append_message("Sistema", "Cache limpo.")

    def external_command(self, cmd):
        self.append_message("Maestro", cmd)
        self.run_async(self.process_logic(cmd))

    def send_command(self, event=None):
        text = self.entry.get()
        if not text.strip(): return
        self.entry.delete(0, "end")
        self.append_message("Maestro", text)
        self.run_async(self.process_logic(text))

    async def process_logic(self, user_input):
        try:
            current_url = self.browser.page.url if self.browser.page else ""
            dom_elements = []
            if current_url and current_url != "about:blank":
                dom_elements = await self.dom_observer.observe_page(self.browser.page)
                self.gui_callback_thought(f"👁️ Mapeados {len(dom_elements)} elementos visíveis.")

            self.gui_callback_thought("🧠 Processando LLM...")
            action = self.brain.process_command(user_input, dom_elements=dom_elements, current_url=current_url)
            intent = action.get("intent", "UNKNOWN")
            args = action.get("args", {})
            
            self.gui_callback_thought(f"🎯 Intenção: {intent}")

            if intent == "FAST_ACT":
                locator = self.browser.page.locator(f"xpath={args.get('xpath')}").first
                if await locator.count() > 0:
                    if args.get("action") == "click": await locator.click()
                    else: await locator.fill(args.get("text", ""))
                    self.gui_callback("Fast Path concluído.")
                else: self.gui_callback_thought("⚠️ Falha Fast Path.")
            
            elif intent == "ACT":
                target_el = next((el for el in dom_elements if el["id"] == args.get("id")), None)
                if target_el:
                    await self.browser.click_coordinates(target_el["x"], target_el["y"])
                    if args.get("action") == "type": await self.browser.page.keyboard.type(args.get("text", ""), delay=30)
                    self.brain.memory.save_action(current_url.split("?")[0], user_input, {"xpath": target_el["xpath"], "action": args.get("action"), "text": args.get("text", "")})
                else: self.gui_callback("Alvo não encontrado.")

            elif intent == "NAVIGATE": await self.browser.goto(args.get("url"))
            elif intent == "ASK_VISION":
                await self.browser.take_screenshot("temp_gui.png")
                ans = self.vision.analyze_image(os.path.join("data", "screenshots", "temp_gui.png"), args.get("question", "Descreva."))
                self.gui_callback(f"Análise:\n{ans}")
            elif intent == "EXTRACT": self.gui_callback(f"📊 Relatório:\n{args.get('data', '')}")
            elif intent == "REPLY": self.gui_callback(args.get("text"))

        except Exception as e: self.gui_callback_thought(f"❌ ERRO: {str(e)}")

    def gui_callback(self, text):
        self.after(0, lambda: self.append_message("Hipno", text))
        
    def gui_callback_thought(self, text):
        self.after(0, lambda: self.append_thought(text))

if __name__ == "__main__":
    app = HipnoLawrenceGUI()
    app.mainloop()
