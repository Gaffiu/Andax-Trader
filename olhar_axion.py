import asyncio
from playwright.async_api import async_playwright

SESSAO_DIR = "./sessao_axion"

async def main():
    async with async_playwright() as p:
        print("🤖 [Andax] Acordando e abrindo o navegador com a sessão salva...")
        
        # Abre o navegador usando a sessão salva (não deve pedir login de novo)
        context = await p.chromium.launch_persistent_context(
            user_data_dir=SESSAO_DIR,
            headless=False, 
            viewport={"width": 1280, "height": 800}
        )
        
        page = context.pages[0]
        
        # Vai para a página inicial (já deve entrar logado)
        await page.goto("https://axion-trade.com")
        await page.wait_for_timeout(3000)

        print("\n⚠️ AÇÃO NECESSÁRIA:")
        print("1. Se o robô não foi direto para a tela de trade, navegue até ela.")
        print("2. Certifique-se de que o gráfico está visível.")
        print("3. Volte ao terminal e aperte ENTER.\n")
        
        input("Pressione ENTER quando o gráfico estiver na tela...")
        
        print("\n📸 [Andax] Tirando foto da tela de trade...")
        # Salva a imagem na pasta do projeto
        await page.screenshot(path="tela_axion.png", full_page=False)
        print("✅ Foto salva como 'tela_axion.png'!")
        
        print("\n👁️ [Andax] Iniciando captura de dados (WebSockets) por 10 segundos...")
        def on_websocket(ws):
            print(f"📡 [WebSocket Conectado] {ws.url}")
            ws.on("framereceived", lambda payload: print(f"📥 [Dados Recebidos] {str(payload)[:120]}..."))
        
        page.on("websocket", on_websocket)
        await asyncio.sleep(10)
        
        print("\n✅ Teste concluído. Fechando navegador...")
        await context.close()

if __name__ == "__main__":
    asyncio.run(main())
