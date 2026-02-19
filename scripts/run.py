import sys
import os
import asyncio
from datetime import datetime

# Adiciona a raiz do projeto ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.hipnolawrence.core.browser import BrowserManager
from src.hipnolawrence.config import GOOGLE_ADS_URL, SCREENSHOTS_DIR
from src.hipnolawrence.core.vision import VisionManager
from src.hipnolawrence.core.brain import BrainManager

async def chat_mode():
    print("=== HipnoLawrence: Modo Chat Interativo ===")
    print("Conectando aos sistemas neurais...")
    
    browser = BrowserManager()
    vision = VisionManager()   # Carrega moondream
    brain = BrainManager()     # Carrega llama3.2:1b
    
    try:
        print("Lançando navegador (Persistente)...")
        await browser.launch()
        
        print(f"Navegando para inicial: {GOOGLE_ADS_URL}")
        try:
            await browser.goto(GOOGLE_ADS_URL)
        except Exception as e:
            print(f"Aviso: Não foi possível carregar a página inicial: {e}")
            
        print("\n--- Sistema Online ---")
        print("Converse naturalmente com o HipnoLawrence.")
        print("Exemplos: 'O que você vê?', 'Vá para o youtube', 'Analise esta tela', 'Tchau'.")
        print("----------------------")

        while True:
            # Captura input do usuário
            try:
                user_input = await asyncio.to_thread(input, "\nVictor> ")
                user_input = user_input.strip()
            except EOFError:
                break
            except KeyboardInterrupt:
                print("\nEncerrando...")
                break
            
            if not user_input:
                continue

            print("HipnoLawrence está pensando...")
            
            # Processa a intenção com o cérebro (llama3.2:1b)
            # Retorna dict: {'intent': ..., 'response': ..., 'args': ...}
            thought = brain.process_command(user_input)
            
            intent = thought.get("intent", "CONVERSAR")
            response = thought.get("response", "")
            args = thought.get("args", {})
            
            # Responde ao usuário primeiro
            if response:
                print(f"HipnoLawrence: {response}")

            # Executa ações baseadas na intenção
            if intent == "SAIR":
                break

            elif intent == "VER":
                timestamp = datetime.now().strftime("%H%M%S")
                filename = f"chat_view_{timestamp}.png"
                print(f"[Ação] Olhando para a tela ({filename})...")
                
                try:
                    await browser.take_screenshot(filename)
                    image_path = os.path.join(SCREENSHOTS_DIR, filename)
                    
                    print("[Ação] Analisando visualmente (Moondream)...")
                    visual_analysis = vision.analyze_screenshot(
                        image_path, 
                        prompt="Descreva esta tela do navegador detalhadamente para o usuário. Identifique o site, elementos principais e qualquer alerta."
                    )
                    print(f"\n[Visão]: {visual_analysis}")
                except Exception as e:
                    print(f"[Erro Visual]: {e}")

            elif intent == "IR_PARA":
                url = args.get("url")
                if url:
                    if not url.startswith("http"):
                        url = "https://" + url
                    print(f"[Ação] Navegando para: {url}")
                    try:
                        await browser.goto(url)
                        print("[Ação] Navegação concluída.")
                    except Exception as e:
                        print(f"[Erro Navegação]: {e}")
                else:
                    print("[Erro] URL não fornecida pelo cérebro.")

            elif intent == "CLICAR":
                text_to_click = args.get("text") or args.get("target")
                if text_to_click:
                    print(f"[Ação] Tentando clicar em: '{text_to_click}'")
                    try:
                        # Tenta clicar por texto
                        await browser.page.click(f"text={text_to_click}", timeout=5000)
                        print("[Ação] Clique realizado.")
                    except Exception as e:
                        print(f"[Erro Clique]: {e}")
                else:
                    print("[Erro] Texto para clique não identificado.")

            elif intent == "STATUS":
                if browser.page:
                    try:
                        title = await browser.page.title()
                        url = browser.page.url
                        print(f"[Status] Título: {title}")
                        print(f"[Status] URL: {url}")
                    except:
                        pass

    except Exception as e:
        print(f"Erro Crítico: {e}")
    finally:
        print("Desligando HipnoLawrence...")
        await browser.close()

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(chat_mode())
