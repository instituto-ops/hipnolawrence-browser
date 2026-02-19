import os
import asyncio
from playwright.async_api import async_playwright
import playwright_stealth

class BrowserManager:
    """
    Gerencia a instância do navegador Chromium com Playwright e Stealth.
    """
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

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
