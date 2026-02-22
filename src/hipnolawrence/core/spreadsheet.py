import gspread
from oauth2client.service_account import ServiceAccountCredentials
import logging
import os

logger = logging.getLogger("HipnoLawrence.Spreadsheet")

class SpreadsheetManager:
    """
    Sincroniza a Matriz NeuroStrategy DB com o Cérebro do Agente.
    """
    def __init__(self, sheet_id="1vAho1pFtyn8StKdZHrSrzSksFnY281g8BTA_hKbHsKw"):
        self.sheet_id = sheet_id
        self.client = None

    def connect(self):
        """Conecta usando as credenciais de Conta de Serviço."""
        try:
            scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
            key_path = os.path.join(os.getcwd(), 'service_account.json')
            
            if not os.path.exists(key_path):
                logger.error(f"Arquivo de credenciais não encontrado em: {key_path}")
                return False
                
            creds = ServiceAccountCredentials.from_json_keyfile_name(key_path, scope)
            self.client = gspread.authorize(creds)
            logger.info("Conexão com Google Sheets autorizada via Service Account.")
            return True
        except Exception as e:
            logger.error(f"Falha na autenticação com Google Sheets: {e}", exc_info=True)
            return False

    def get_full_matrix(self):
        """Lê todas as abas estratégicas, incluindo o Gabarito de Configuração."""
        if not self.client: 
            logger.error("Tentativa de ler planilha sem cliente conectado.")
            return None
            
        try:
            doc = self.client.open_by_key(self.sheet_id)
            logger.info("Planilha localizada com sucesso. Iniciando download de abas...")
            
            return {
                "performance": doc.worksheet("ADS_Performance").get_all_records(),
                "demand": doc.worksheet("INTENTION_Demand").get_all_records(),
                "competitive": doc.worksheet("CAMPAIGN_Competitive").get_all_records(),
                "config": doc.worksheet("CAMPAIGN_Config").get_all_records()
            }
        except Exception as e:
            logger.error(f"Erro fatal ao ler matriz completa: {e}", exc_info=True)
            return None
