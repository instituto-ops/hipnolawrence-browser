import os
import asyncio
from playwright.async_api import async_playwright
import playwright_stealth
from hipnolawrence.human_mouse import HumanMouse

class BrowserManager:
    """
    Gerencia a instância do navegador Chromium com Playwright e Stealth.
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
        Inicia o navegador Chromium em modo não-headless, configura viewport e aplica stealth.
        """
        self.playwright = await async_playwright().start()
        # Create user data directory for persistence
        user_data_dir = os.path.join(os.getcwd(), "data", "user_data")
        os.makedirs(user_data_dir, exist_ok=True)
        
        # Launch persistent context
        self.context = await self.playwright.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            args=["--disable-blink-features=AutomationControlled"],
            ignore_default_args=["--enable-automation"]
        )
        
        # Get the first page or create a new one
        if self.context.pages:
            self.page = self.context.pages[0]
        else:
            self.page = await self.context.new_page()
        
        # Apply stealth to avoid detection
        # Apply stealth to avoid detection via dynamic lookup
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
        """
        Navega para a URL especificada.
        """
        if not self.page:
            raise Exception("Browser not launched. Call launch() first.")
        await self.page.goto(url)

    async def take_screenshot(self, name):
        """
        Salva um screenshot na pasta data/screenshots/.
        """
        if not self.page:
            raise Exception("Browser not launched. Call launch() first.")
        
        # Ensure name ends with .png
        if not name.endswith(".png"):
            name = f"{name}.png"
            
        # Path relative to where script is run (assumed root)
        screenshot_path = os.path.join("data", "screenshots", name)
        
        # Ensure directory exists (redundant but safe)
        os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
        
        await self.page.screenshot(path=screenshot_path)
        print(f"Screenshot salvo em: {screenshot_path}")

    async def click_element(self, selector):
        """
        Clica em um elemento usando movimento humano.
        """
        if not self.page:
            raise Exception("Browser not launched. Call launch() first.")

        locator = self.page.locator(selector).first
        box = await locator.bounding_box()

        if box:
            target_x = box["x"] + box["width"] / 2
            target_y = box["y"] + box["height"] / 2

            await self.human_mouse.move_to_coordinates(
                self.page,
                self.current_mouse_x,
                self.current_mouse_y,
                target_x,
                target_y
            )

            self.current_mouse_x = target_x
            self.current_mouse_y = target_y

            await locator.click()

    async def click_coordinates(self, x: float, y: float):
        """
        Clica em coordenadas específicas usando movimento humano.
        """
        if not self.page:
            raise Exception("Browser not launched. Call launch() first.")

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
        """
        Encerra o navegador e o contexto com segurança.
        """
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
