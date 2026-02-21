import asyncio
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from hipnolawrence.core.browser import BrowserManager
from hipnolawrence.core.brain import Brain
from hipnolawrence.core.vision import VisionManager
from hipnolawrence.core.vision_ocr import VisionOCR

async def main():
    print("🧠 Inicializando o Copiloto Estratégico HipnoLawrence...")
    browser = BrowserManager()
    brain = Brain()
    vision = VisionManager()
    ocr = VisionOCR()

    print("🌐 Acordando o navegador persistente...")
    await browser.launch()
    print("✅ Sistema pronto. Modo Chatbot ativado.")

    chat_history = [] # Memória de curto prazo

    while True:
        user_input = await asyncio.get_event_loop().run_in_executor(
            None, input, "\n👨💼 Maestro: "
        )

        if user_input.lower() in ["sair", "exit", "quit"]:
            print("🛑 Desligando o sistema...")
            await browser.close()
            break

        if not user_input.strip():
            continue

        # Formata o histórico (mantém apenas as últimas 4 interações para não estourar o contexto do LLM local)
        history_text = "\n".join(chat_history[-8:])
        
        print("🧠 Pensando...")
        action = brain.process_command(user_input, history=history_text)
        intent = action.get("intent", "UNKNOWN")
        args = action.get("args", {})

        # Atualiza histórico com a ação do agente
        chat_history.append(f"Usuário: {user_input}")
        chat_history.append(f"HipnoLawrence (Intenção {intent}): {args}")

        try:
            if intent == "REPLY":
                # Modo Conversacional
                resposta = args.get("text", "Não consegui formular uma resposta.")
                print(f"\n🤖 HipnoLawrence: {resposta}\n")

            elif intent == "NAVIGATE":
                url = args.get("url")
                if url:
                    print(f"🤖 HipnoLawrence: Navegando para {url}...")
                    await browser.goto(url)

            elif intent == "CLICK" or intent == "TYPE":
                target = args.get("target", "")
                text_to_type = args.get("text", "")
                
                print(f"👁️ Escaneando a tela em busca de '{target}'...")
                screenshot_name = "temp_action.png"
                await browser.take_screenshot(screenshot_name)
                screenshot_path = os.path.abspath(os.path.join("data", "screenshots", screenshot_name))
                
                elements = ocr.extract_elements(screenshot_path)
                target_found = False
                
                for el in elements:
                    text_el = el.get("text", "")
                    if target.lower() in text_el.lower() and len(text_el.strip()) > 1:
                        cx = el['x'] + (el['width'] / 2)
                        cy = el['y'] + (el['height'] / 2)
                        
                        await browser.click_coordinates(cx, cy)
                        target_found = True
                        
                        if intent == "TYPE":
                            print(f"⌨️ Digitando: '{text_to_type}'...")
                            # Usa o teclado do Playwright para digitar no local clicado
                            await browser.page.keyboard.type(text_to_type, delay=50) # Delay simula digitação humana
                            
                        else:
                            print(f"🎯 Cliquei em '{target}'.")
                        break
                
                if not target_found:
                    print(f"🤖 HipnoLawrence: Não encontrei '{target}' na tela para interagir.")

            elif intent == "ASK_VISION":
                question = args.get("question", "Descreva esta imagem.")
                print("👁️ Analisando visualmente...")
                screenshot_name = "temp_vision.png"
                await browser.take_screenshot(screenshot_name)
                screenshot_path = os.path.abspath(os.path.join("data", "screenshots", screenshot_name))
                
                answer = vision.analyze_image(screenshot_path, question)
                print(f"\n🤖 HipnoLawrence (Visão): {answer}\n")

            elif intent == "EXIT":
                print("🤖 HipnoLawrence: Até logo, Maestro!")
                await browser.close()
                break

            else:
                print(f"🤖 HipnoLawrence: Ação interna não reconhecida ({intent}).")

        except Exception as e:
            print(f"❌ Erro de execução física: {e}")

if __name__ == "__main__":
    asyncio.run(main())
