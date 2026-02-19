from pathlib import Path

# Base Directory (Project Root)
# .../src/hipnolawrence/config.py -> .../Navegador HipnoLawrence
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Data Directories
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = DATA_DIR / "logs"
SCREENSHOTS_DIR = DATA_DIR / "screenshots"

# Target URLs
GOOGLE_ADS_URL = "https://ads.google.com"
WHATSAPP_URL = "https://web.whatsapp.com"
DOCTORALIA_URL = "https://www.doctoralia.com.br"

# Browser Configuration
HEADLESS = False
VIEWPORT = {"width": 1920, "height": 1080}
