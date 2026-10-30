import asyncio
from playwright.async_api import async_playwright
import time

# URL da Polarium (ajuste se necessário)
URL_POLARIUM = "https://polarium.com/pt-br/" 
# Pasta onde salvaremos o login para não precisar logar toda vez
SESSAO_DIR = "./sessao_polarium"

async def main():
    async with async_playwright() as p:
        print("🤖 [Andax Corpo] Iniciando navegador...")
        
        # Abre o navegador salvando a sessão
        context = await p.chromium.launch_persistent_context(
            user_data_dir=SESSAO_DIR,
            headless=False, # False para você poder ver e fazer o login manual
            viewport={"width": 1280, "height": 800}
        )
        
        page = context.pages[0]
        
        # Função para escutar os WebSockets (dados brutos)
        def on_websocket(ws):
            print(f"📡 [WebSocket Conectado] {ws.url}")
            # Aqui o Andax vai "escutar" o fluxo de preços
            ws.on("framesent", lambda payload: None) # Ignora o que enviamos
            ws.on("framereceived", lambda payload: print(f"📥 [Dados Recebidos] {payload[:100]}...")) # Mostra os primeiros 100 caracteres

        page.on("websocket", on_websocket)

        print("🌐 [Andax Corpo] Acessando a Polarium...")
        await page.goto(URL_POLARIUM)
        
        print("\n⚠️ AÇÃO NECESSÁRIA:")
        print("1. Faça o login na sua conta Polarium na janela que abriu.")
        print("2. Entre na tela de negociação (onde fica o gráfico).")
        print("3. Volte aqui no terminal e aperte ENTER quando estiver pronto.\n")
        
        # Espera você apertar Enter no terminal
        input("Pressione ENTER após estar logado e na tela do gráfico...")
        
        print("\n👁️ [Andax Corpo] Iniciando captura de dados em tempo real...")
        print("Deixe a janela do navegador aberta. Vamos capturar os dados por 15 segundos.")
        
        # Fica rodando por 15 segundos para capturarmos os dados
        await asyncio.sleep(15)
        
        print("\n✅ Teste concluído. Fechando navegador...")
        await context.close()

if __name__ == "__main__":
    asyncio.run(main())
