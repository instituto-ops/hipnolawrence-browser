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
        """Conecta usando as credenciais (Assume que service_account.json existe na raiz)."""
        try:
            scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
            # Maestro: Você precisará colocar o arquivo 'service_account.json' na raiz do projeto
            creds_path = os.path.join(os.getcwd(), 'service_account.json')
            if not os.path.exists(creds_path):
                logger.error("Arquivo service_account.json não encontrado na raiz.")
                return False
                
            creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
            self.client = gspread.authorize(creds)
            return True
        except Exception as e:
            logger.error(f"Falha na conexão com Google Sheets: {e}")
            return False

    def get_performance_summary(self):
        """Lê a Mega-Matrix CAMPAIGN_Config e retorna registros mapeados."""
        if not self.client: 
            if not self.connect():
                return []
        try:
            sheet = self.client.open_by_key(self.sheet_id).worksheet("CAMPAIGN_Config")
            # get_all_records() mapeia automaticamente os 57 cabeçalhos como chaves
            data = sheet.get_all_records()
            return data
        except Exception as e:
            logger.error(f"Falha ao ler Mega-Matrix: {e}")
            return []

    def get_full_matrix(self):
        """Lê todas as abas estratégicas e retorna um pacotão de dados."""
        if not self.client: 
            if not self.connect():
                return None
        try:
            doc = self.client.open_by_key(self.sheet_id)
            return {
                "performance": doc.worksheet("ADS_Performance").get_all_records(),
                "demand": doc.worksheet("INTENTION_Demand").get_all_records(),
                "competitive": doc.worksheet("CAMPAIGN_Competitive").get_all_records(),
                "config": doc.worksheet("CAMPAIGN_Config").get_all_records()
            }
        except Exception as e:
            logger.error(f"Erro ao ler matriz completa: {e}")
            return None
