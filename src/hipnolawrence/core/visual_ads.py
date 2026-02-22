import logging
import asyncio
import random
from datetime import datetime
from typing import List, Dict, Any
from playwright.async_api import Page

# Configuração de Logs
logger = logging.getLogger("HipnoLawrence.VisualAds")

class VisualAdsManager:
    """
    Gerenciador Visual do Google Ads (No-API / No-Token).
    
    Estratégia:
    1. Navegação via Playwright em sessão autenticada.
    2. Extração de dados via DOM (tabelas de campanha).
    3. Captura de evidências visuais (Screenshots) para processamento por VLM.
    """

    # URL base do Dashboard de Campanhas (ajustar conforme a view do usuário)
    ADS_DASHBOARD_URL = "https://ads.google.com/aw/campaigns"

    def __init__(self, page: Page):
        self.page = page

    async def navigate_to_campaigns(self):
        """Força a navegação para a aba de campanhas e aguarda renderização."""
        logger.info("Navegando visualmente para o Painel de Campanhas...")
        
        # Verifica se já não estamos lá para economizar tempo
        if "campaigns" not in self.page.url:
            await self.page.goto(self.ADS_DASHBOARD_URL, wait_until="domcontentloaded")
        
        # Humanização: Espera aleatória + movimento de mouse
        await self.page.wait_for_timeout(random.uniform(2000, 5000))
        
        # Tenta identificar a tabela de dados (essGrid ou similar - seletor genérico do Google Material)
        # Nota: Seletores do Google Ads são dinâmicos e ofuscados. 
        # Estratégia: Buscar por texto visível ou estrutura de tabela.
        try:
            # Espera genérica por algo que pareça uma linha de tabela
            await self.page.wait_for_selector("div[role='row']", timeout=15000)
            logger.info("Tabela de campanhas detectada visualmente.")
        except Exception as e:
            logger.warning(f"Não foi possível confirmar carregamento da tabela: {e}")

    async def extract_campaigns_data(self) -> List[Dict[str, Any]]:
        """Extração de alta precisão: Ignora totais e lixo de interface."""
        await self.navigate_to_campaigns()
        data = []
        rows = await self.page.locator("div[role='row']").all()

        for row in rows:
            text = await row.inner_text()
            lines = [l.strip() for l in text.split('\n') if l.strip()]
            
            # FILTRO DE ELITE: 
            # 1. Deve ter nome, status e orçamento.
            # 2. NÃO pode ser linha de Total ou Rascunho.
            # 3. Deve ter um indicador de status real.
            if len(lines) >= 3:
                name = lines[0]
                status = lines[1]
                # Ignora linhas de sistema
                if any(x in name.lower() for x in ["total", "rascunho", "help_outline", "ajuda"]):
                    continue
                
                data.append({
                    "name": name,
                    "status": status,
                    "budget": lines[2],
                    "metrics_raw": " | ".join(lines[3:])
                })
        
        logger.info(f"Filtro aplicado: {len(data)} campanhas reais encontradas.")
        return data

    async def capture_kpi_snapshot(self, output_path: str = "kpi_snapshot.png"):
        """
        Tira um screenshot da área superior (Visão Geral) para análise via OCR/VLM.
        """
        logger.info("Capturando screenshot dos Cards de KPI...")
        
        # Foca no topo da página onde ficam os gráficos/cards
        # Scroll para o topo
        await self.page.evaluate("window.scrollTo(0, 0)")
        await self.page.wait_for_timeout(1000)

        # Captura a viewport
        await self.page.screenshot(path=output_path)
        logger.info(f"Screenshot salvo em {output_path}. Pronto para envio ao VLM.")
        
        return output_path
