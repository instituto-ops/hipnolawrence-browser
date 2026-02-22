import sys
import os
import logging

# 1. AJUSTE DE PATH: Configura a raiz antes de importar o projeto
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(base_dir, "src"))

# Configuração de Log
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("HipnoLawrence.Main")

def launch():
    """Inicia a aplicação de forma segura."""
    try:
        from gui_app import HipnoLawrenceGUI
        logger.info("Lançando Neural Console v5.1...")
        app = HipnoLawrenceGUI()
        # CustomTkinter usa mainloop() por padrão
        app.mainloop()
    except Exception as e:
        logger.critical(f"Erro fatal na execução: {e}", exc_info=True)

if __name__ == "__main__":
    launch()
