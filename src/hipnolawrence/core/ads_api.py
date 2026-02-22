import logging
import os
import sys

# Tenta importar a biblioteca oficial. Se falhar, loga o erro mas não quebra o import do módulo.
try:
    from google.ads.googleads.client import GoogleAdsClient
    from google.ads.googleads.errors import GoogleAdsException
    ADS_LIB_AVAILABLE = True
except ImportError:
    ADS_LIB_AVAILABLE = False

# Configuração de Logs Específica para o Módulo de Ads
logger = logging.getLogger("HipnoLawrence.AdsAPI")

class GoogleAdsManager:
    """
    Gerenciador da API do Google Ads (v15+) baseado no padrão 'google-ads-python'.
    
    Responsabilidades:
    1. Autenticação OAuth2 via arquivo YAML.
    2. Execução de consultas GAQL (Google Ads Query Language).
    3. Tratamento de erros oficiais da API.
    
    Ref: Research Tier 1 (googleads/google-ads-python)
    """

    def __init__(self, config_path: str = 'google-ads.yaml'):
        """
        Inicializa o cliente.
        :param config_path: Caminho para o arquivo google-ads.yaml contendo credenciais.
        """
        self.config_path = config_path
        self.client = None
        self.is_ready = False
        
        if not ADS_LIB_AVAILABLE:
            logger.critical("Biblioteca 'google-ads' não encontrada. Instale com: pip install google-ads")
            return

        self._initialize_client()

    def _initialize_client(self):
        """Carrega as credenciais e inicializa o cliente SOAP/REST."""
        if not os.path.exists(self.config_path):
            logger.warning(f"Arquivo de configuração '{self.config_path}' não encontrado. Modo API desativado.")
            return

        try:
            # Carrega do arquivo YAML (Padrão Oficial)
            self.client = GoogleAdsClient.load_from_storage(self.config_path)
            self.is_ready = True
            logger.info("GoogleAdsClient inicializado com sucesso.")
        except Exception as ex:
            logger.error(f"Falha fatal ao inicializar GoogleAdsClient: {ex}")
            self.is_ready = False

    def execute_gaql(self, customer_id: str, query: str):
        """
        Executa uma consulta GAQL pura e retorna o stream de resultados.
        
        :param customer_id: ID da conta (sem traços, string numérica).
        :param query: String contendo a consulta SELECT ... FROM ...
        :return: Generator/Stream de GoogleAdsRow ou None em caso de erro.
        """
        if not self.is_ready or not self.client:
            logger.error("Tentativa de query GAQL com cliente não inicializado.")
            return None

        ga_service = self.client.get_service("GoogleAdsService")

        try:
            # Usa search_stream para eficiência em grandes relatórios (Best Practice)
            # O customer_id deve ser string numérica
            clean_customer_id = str(customer_id).replace("-", "")
            
            logger.debug(f"Executando GAQL em {clean_customer_id}: {query[:50]}...")
            stream = ga_service.search_stream(
                customer_id=clean_customer_id,
                query=query
            )
            return stream

        except GoogleAdsException as ex:
            # Tratamento robusto de erros da API
            for error in ex.failure.errors:
                logger.error(f"Erro GAQL: {error.message} (Domain: {error.error_code})")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado na execução GAQL: {e}")
            return None

    def get_account_hierarchy(self, login_customer_id: str):
        """
        Exemplo de método utilitário para listar contas acessíveis (MCC).
        Útil para descobrir Customer IDs.
        """
        query = """
            SELECT
                customer_client.client_customer,
                customer_client.level,
                customer_client.manager,
                customer_client.descriptive_name,
                customer_client.currency_code,
                customer_client.time_zone,
                customer_client.id
            FROM customer_client
            WHERE customer_client.level <= 1
        """
        return self.execute_gaql(login_customer_id, query)
