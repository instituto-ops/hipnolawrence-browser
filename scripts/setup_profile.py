import asyncio
import sys
import os

# Garante que o Python encontre a pasta src para importar o hipnolawrence
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from hipnolawrence.core.browser import BrowserManager

async def main():
    print("Iniciando o navegador para configuração de perfil...")
    manager = BrowserManager()
    await manager.launch()
    
    await manager.goto("https://ads.google.com")
    
    print("\n" + "="*60)
    print("⚠️  AÇÃO HUMANA REQUERIDA!")
    print("1. O navegador foi aberto com seu perfil persistente.")
    print("2. Faça o login na sua conta do Google Ads.")
    print("3. Resolva qualquer verificação de 2 Fatores (Celular/SMS).")
    print("4. Quando o painel do Google Ads carregar completamente...")
    print("="*60 + "\n")
    
    # Pausa segura aguardando o Maestro apertar ENTER no terminal
    await asyncio.get_event_loop().run_in_executor(None, input, "👉 PRESSIONE ENTER AQUI NO TERMINAL PARA SALVAR E FECHAR... ")
    
    print("Salvando perfil e encerrando...")
    await manager.close()
    print("Perfil salvo com sucesso na pasta data/user_data/!")

if __name__ == "__main__":
    asyncio.run(main())
