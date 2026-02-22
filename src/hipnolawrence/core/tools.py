import logging
from typing import Dict, Any, Optional
from hipnolawrence.core.doctoralia_intelligence import DoctoraliaIntelligence
from hipnolawrence.core.visual_ads import VisualAdsManager
from hipnolawrence.core.memory import MemoryManager

logger = logging.getLogger("HipnoLawrence.Tools")

class ToolRegistry:
    """
    Registro Central de Ferramentas (Agente Visual & Comet).
    """

    def __init__(self, browser_page=None):
        self._visual_ads = None
        self._doctoralia_intel = None
        self._browser_page = browser_page
        self.memory = MemoryManager()

    @property
    def ads(self) -> VisualAdsManager:
        """Carrega o Gerenciador Visual de Ads (No-Token)."""
        if not self._visual_ads:
            if not self._browser_page:
                logger.error("VisualAds requer Browser Page.")
                return None
            self._visual_ads = VisualAdsManager(self._browser_page)
        return self._visual_ads

    @property
    def doctoralia(self) -> DoctoraliaIntelligence:
        """Carrega Inteligência Doctoralia."""
        if not self._doctoralia_intel:
            if not self._browser_page:
                return None
            self._doctoralia_intel = DoctoraliaIntelligence(self._browser_page)
        return self._doctoralia_intel

    def get_available_tools(self) -> Dict[str, str]:
        return {
            "doctoralia_ranking": "Busca direta na Doctoralia (comportamento humano).",
            "doctoralia_serp": "Busca indireta via Google Search (mais seguro contra bloqueios).",
            "google_ads_visual": "Extrai dados de campanhas e screenshots do painel Google Ads via navegação visual."
        }

    # --- Wrappers ---

    async def run_ads_visual_extraction(self):
        if not self.ads: return "Erro: Browser não conectado."
        data = await self.ads.extract_campaigns_data()
        snapshot = await self.ads.capture_kpi_snapshot()
        return {"table_data": data, "snapshot_path": snapshot}

    async def run_doctoralia_serp(self, query: str):
        if not self.doctoralia: return "Erro: Browser não conectado."
        return await self.doctoralia.scan_via_google_serp(query)

    async def run_doctoralia_scan(self, specialty: str, city: str):
        if not self.doctoralia: return "Erro: Browser não conectado."
        return await self.doctoralia.scan_ranking_direct(specialty, city)
