import customtkinter as ctk
import asyncio
import threading
import sys
import os
from datetime import datetime
from tkinter import filedialog

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from hipnolawrence.core.browser import BrowserManager
from hipnolawrence.core.brain import Brain
from hipnolawrence.core.vision import VisionManager
from hipnolawrence.core.dom_observer import DOMObserver

class HipnoLawrenceGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("HipnoLawrence OS - Neural Console v4")
        self.geometry("700x800")
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        
        # Título
        self.logo = ctk.CTkLabel(self.sidebar, text="HIPNOLAWRENCE", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo.pack(pady=(20, 10))

        # SEÇÃO: GENERAL
        self.label_gen = ctk.CTkLabel(self.sidebar, text="FERRAMENTAS GERAIS", font=ctk.CTkFont(size=12, weight="bold"), text_color="gray")
        self.label_gen.pack(pady=(10, 5), padx=10, anchor="w")
        
        ctk.CTkButton(self.sidebar, text="📚 Add à Biblioteca", command=self.tool_add_to_library).pack(pady=5, padx=20, fill="x")
        ctk.CTkButton(self.sidebar, text="🕵️ Radar Mercado", command=lambda: self.external_command("Abra a Doctoralia e analise o mercado")).pack(pady=5, padx=20, fill="x")

        # SEÇÃO: GOOGLE ADS CENTER
        self.label_ads = ctk.CTkLabel(self.sidebar, text="GOOGLE ADS CENTER", font=ctk.CTkFont(size=12, weight="bold"), text_color="#4285F4")
        self.label_ads.pack(pady=(20, 5), padx=10, anchor="w")
        
        ctk.CTkButton(self.sidebar, text="📊 Diagnóstico Geral", command=lambda: self.external_command("Faça um diagnóstico completo desta tela do Google Ads")).pack(pady=5, padx=20, fill="x")
        ctk.CTkButton(self.sidebar, text="💰 Analisar ROI/CPA", command=lambda: self.external_command("Extraia os dados de custo e conversão e calcule o ROI")).pack(pady=5, padx=20, fill="x")
        ctk.CTkButton(self.sidebar, text="🔎 Auditoria de Termos", command=lambda: self.external_command("Analise os termos de pesquisa e identifique desperdícios")).pack(pady=5, padx=20, fill="x")
        ctk.CTkButton(self.sidebar, text="📝 Sugerir Criativos", command=lambda: self.external_command("Use a biblioteca para sugerir 3 títulos de anúncios persuasivos para esta página")).pack(pady=5, padx=20, fill="x")

        # Rodapé Sidebar
        self.btn_reset = ctk.CTkButton(self.sidebar, text="🧹 Limpar Cache", fg_color="indianred", command=self.tool_clear_cache)
        self.btn_reset.pack(pady=20, padx=20, side="bottom", fill="x")

        # --- CHAT AREA ---
        self.chat_display = ctk.CTkTextbox(self, state="disabled", font=("Roboto", 14), wrap="word")
        self.chat_display.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.grid(row=1, column=1, padx=10, pady=(0, 10), sticky="ew")
        
        self.entry = ctk.CTkEntry(self.input_frame, placeholder_text="Sua ordem, Maestro...", font=("Roboto", 14))
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.entry.bind("<Return>", self.send_command)

        self.send_btn = ctk.CTkButton(self.input_frame, text="Enviar", width=60, command=self.send_command)
        self.send_btn.pack(side="right")

        # --- MOTORES ---
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
        icon = "👨💼" if sender == "Maestro" else "🤖"
        if sender == "Sistema": icon = "🔧"
        self.chat_display.insert("end", f"[{ts}] {icon} {sender.upper()}: {text}\n\n")
        self.chat_display.see("end")
        self.chat_display.configure(state="disabled")

    def external_command(self, cmd):
        self.append_message("Maestro", cmd)
        self.run_async(self.process_logic(cmd))

    def tool_add_to_library(self):
        files = filedialog.askopenfilenames(filetypes=[("Text files", "*.txt")])
        if files:
            for f_path in files:
                with open(f_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    self.brain.memory.add_knowledge(content, source=os.path.basename(f_path))
            self.append_message("Sistema", f"{len(files)} arquivos adicionados à biblioteca neural.")

    def tool_clear_cache(self):
        cache_path = self.brain.memory.cache_path
        if os.path.exists(cache_path):
            os.remove(cache_path)
            self.brain.memory.action_cache = {}
            self.append_message("Sistema", "Cache limpo.")

    def send_command(self, event=None):
        text = self.entry.get()
        if not text.strip(): return
        self.entry.delete(0, "end")
        self.append_message("Maestro", text)
        self.run_async(self.process_logic(text))

    async def process_logic(self, user_input):
        try:
            current_url = self.browser.page.url if self.browser.page else ""
            dom_elements = await self.dom_observer.observe_page(self.browser.page) if current_url and current_url != "about:blank" else []
            
            action = self.brain.process_command(user_input, dom_elements=dom_elements, current_url=current_url)
            intent = action.get("intent", "UNKNOWN")
            args = action.get("args", {})
            
            if intent == "FAST_ACT":
                self.gui_callback("⚡ FAST PATH...")
                locator = self.browser.page.locator(f"xpath={args.get('xpath')}").first
                if await locator.count() > 0:
                    if args.get("action") == "click": await locator.click()
                    else: await locator.fill(args.get("text", ""))
                    self.gui_callback("✅ Concluído.")
                else: self.gui_callback("⚠️ Fast Path falhou.")
            
            elif intent == "ACT":
                target_el = next((el for el in dom_elements if el["id"] == args.get("id")), None)
                if target_el:
                    self.gui_callback(f"🎯 Agindo em: {target_el['text']}")
                    await self.browser.click_coordinates(target_el["x"], target_el["y"])
                    if args.get("action") == "type": await self.browser.page.keyboard.type(args.get("text", ""), delay=30)
                    self.brain.memory.save_action(current_url.split("?")[0], user_input, {"xpath": target_el["xpath"], "action": args.get("action"), "text": args.get("text", "")})
                else: self.gui_callback("❌ Não encontrado.")

            elif intent == "NAVIGATE": await self.browser.goto(args.get("url"))
            elif intent == "ASK_VISION":
                self.gui_callback("👁️ Analisando tela...")
                await self.browser.take_screenshot("temp_gui.png")
                ans = self.vision.analyze_image(os.path.join("data", "screenshots", "temp_gui.png"), args.get("question", "Descreva."))
                self.gui_callback(f"Análise: {ans}")
            elif intent == "EXTRACT": self.gui_callback(f"📊 Dados Extraídos:\n{args.get('data', '')}")
            elif intent == "REPLY": self.gui_callback(args.get("text"))
            elif intent == "EXIT":
                await self.browser.close()
                self.quit()
        except Exception as e: self.gui_callback(f"Erro: {str(e)}")

    def gui_callback(self, text):
        self.after(0, lambda: self.append_message("Hipno", text))

if __name__ == "__main__":
    app = HipnoLawrenceGUI()
    app.mainloop()
