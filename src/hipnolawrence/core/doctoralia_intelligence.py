import logging
import asyncio
import random
from typing import List, Dict
from playwright.async_api import Page

# Configuração de Logs
logger = logging.getLogger("HipnoLawrence.Doctoralia")

class DoctoraliaIntelligence:
    """
    Módulo de Inteligência Competitiva e Auditoria de Ranking.
    V2: Comportamento "Comet" (Bio-Mimetização) e Fallback via Google SERP.
    """

    DOCTORALIA_URL = "https://www.doctoralia.com.br"
    GOOGLE_SEARCH_URL = "https://www.google.com.br/search?q="

    def __init__(self, page: Page):
        self.page = page

    async def _human_delay(self, min_s=2.0, max_s=5.0):
        """Pausa aleatória para simular tempo de leitura/cognição."""
        wait_time = random.uniform(min_s, max_s)
        await asyncio.sleep(wait_time)

    async def _human_scroll(self):
        """Simula rolagem de página de leitura humana (não suave, mas em blocos)."""
        for _ in range(random.randint(3, 6)):
            await self.page.mouse.wheel(0, random.randint(300, 700))
            await asyncio.sleep(random.uniform(0.5, 1.5))

    async def scan_via_google_serp(self, query: str) -> List[Dict]:
        """
        Busca indireta: Pesquisa no Google para ver quem o Google rankeia para a Doctoralia.
        Ex: query = 'psicologo goiania doctoralia'
        Vantagem: Não toca no site da Doctoralia, evita bloqueio.
        """
        logger.info(f"Executando Scan Indireto (SERP) para: {query}")
        search_url = f"{self.GOOGLE_SEARCH_URL}{query.replace(' ', '+')}"
        
        await self.page.goto(search_url, wait_until="domcontentloaded")
        await self._human_delay()
        
        results = []
        # Seletores do Google mudam, mas a estrutura de links h3 > a geralmente se mantém
        links = await self.page.locator("div.g a").all()
        
        for link in links:
            href = await link.get_attribute("href")
            title = await link.inner_text()
            
            if href and "doctoralia.com.br" in href:
                results.append({
                    "source": "google_serp",
                    "title": title.split("\n")[0], # Limpa lixo do título
                    "url": href,
                    "position_on_google": len(results) + 1
                })
        
        logger.info(f"Encontrados {len(results)} links da Doctoralia no Google.")
        return results

    async def scan_ranking_direct(self, specialty: str, city: str, max_pages: int = 2) -> List[Dict]:
        """
        Varredura direta no site (Modo Comet).
        Simula navegação completa com mouse e scroll.
        """
        search_url = f"{self.DOCTORALIA_URL}/pesquisa?filters%5Bspecializations%5D%5B0%5D={specialty}&loc={city}"
        
        logger.info(f"Iniciando varredura 'Comet' direta: {specialty} em {city}")
        
        results = []
        current_page = 1

        try:
            await self.page.goto(search_url, wait_until="domcontentloaded")
            await self._human_delay(3, 6) # Delay inicial maior
            
            while current_page <= max_pages:
                logger.info(f"Lendo página {current_page}...")
                
                # Comportamento Humano: Rolar a página antes de extrair
                await self._human_scroll()
                
                # Extração
                cards = await self.page.locator("li[data-id]").all()
                for index, card in enumerate(cards):
                    try:
                        data_id = await card.get_attribute("data-id")
                        name_locator = card.locator("a.rank-element-name")
                        
                        if await name_locator.count() > 0:
                            name = await name_locator.first.text_content()
                            is_ad = await card.locator(".badge-ad").count() > 0
                            
                            results.append({
                                "rank": (current_page - 1) * 20 + (index + 1),
                                "name": name.strip(),
                                "is_sponsored": is_ad,
                                "id": data_id
                            })
                    except:
                        continue
                
                # Paginação
                next_button = self.page.locator("a[aria-label='next']")
                if await next_button.count() > 0 and current_page < max_pages:
                    # Move o mouse até o botão (simulado) e clica
                    await next_button.scroll_into_view_if_needed()
                    await self._human_delay(1, 2)
                    await next_button.click()
                    await self.page.wait_for_timeout(random.uniform(2000, 4000))
                    current_page += 1
                else:
                    break

        except Exception as e:
            logger.error(f"Erro no scan direto: {e}")
        
        return results
