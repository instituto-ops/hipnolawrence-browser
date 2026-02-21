import os
import asyncio
from playwright.async_api import async_playwright
import playwright_stealth
# Ajuste de importação para garantir que o Python encontre o módulo
try:
    from hipnolawrence.human_mouse import HumanMouse
except ImportError:
    # Fallback caso a estrutura de pastas varie na execução
    from src.hipnolawrence.human_mouse import HumanMouse

class BrowserManager:
    """
    Gerencia a instância do navegador Chromium com Playwright, Stealth e HumanMouse.
    """
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.human_mouse = HumanMouse()
        self.current_mouse_x = 0
        self.current_mouse_y = 0

    async def launch(self):
        """
        Inicia o navegador Chromium maximizado e responsivo.
        """
        self.playwright = await async_playwright().start()
        user_data_dir = os.path.join(os.getcwd(), "data", "user_data")
        os.makedirs(user_data_dir, exist_ok=True)
        
        # Launch persistent context com Viewport Dinâmico
        self.context = await self.playwright.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            viewport=None,  # <--- ESSENCIAL: Permite que o site ocupe toda a janela
            channel="chrome", # Tenta usar o Chrome real se instalado, ou cai para Chromium
            args=[
                "--start-maximized", # <--- ESSENCIAL: Inicia a janela maximizada
                "--disable-blink-features=AutomationControlled"
            ],
            ignore_default_args=["--enable-automation"]
        )
        
        if self.context.pages:
            self.page = self.context.pages[0]
        else:
            self.page = await self.context.new_page()
        
        # Aplica Stealth
        stealth_applied = False
        for func_name in ["stealth_async", "stealth"]:
            if hasattr(playwright_stealth, func_name):
                stealth_func = getattr(playwright_stealth, func_name)
                if callable(stealth_func):
                    try:
                        await stealth_func(self.page)
                        stealth_applied = True
                        break
                    except Exception:
                        continue
        
        if not stealth_applied:
            print("Warning: Could not apply stealth settings.")
        
        return self.page

    async def goto(self, url):
        if not self.page: raise Exception("Browser not launched.")
        await self.page.goto(url)

    async def take_screenshot(self, name):
        if not self.page: raise Exception("Browser not launched.")
        if not name.endswith(".png"): name = f"{name}.png"
        screenshot_path = os.path.join("data", "screenshots", name)
        os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
        await self.page.screenshot(path=screenshot_path)

    async def click_element(self, selector):
        # Método legado (por seletor), mantido para compatibilidade
        if not self.page: raise Exception("Browser not launched.")
        locator = self.page.locator(selector).first
        box = await locator.bounding_box()
        if box:
            target_x = box["x"] + box["width"] / 2
            target_y = box["y"] + box["height"] / 2
            await self.click_coordinates(target_x, target_y)

    async def click_coordinates(self, x, y):
        """
        Move o mouse humanamente até as coordenadas e clica.
        """
        if not self.page: raise Exception("Browser not launched.")
        
        await self.human_mouse.move_to_coordinates(
            self.page,
            self.current_mouse_x,
            self.current_mouse_y,
            x,
            y
        )
        self.current_mouse_x = x
        self.current_mouse_y = y
        await self.page.mouse.click(x, y)

    async def close(self):
        if self.context: await self.context.close()
        if self.playwright: await self.playwright.stop()
