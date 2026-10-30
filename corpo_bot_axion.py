import asyncio
from playwright.async_api import async_playwright

# --- CONFIGURAÇÕES DA CONTA ---
URL_AXION = "https://axion-trade.com" 
EMAIL = "tff2415@gmail.com"
SENHA = "tt787890"
SESSAO_DIR = "./sessao_axion"

async def main():
    async with async_playwright() as p:
        print("🤖 [Andax Corpo] Iniciando navegador para a Axion Trade...")
        
        # Abre o navegador salvando a sessão para não precisar logar toda vez
        context = await p.chromium.launch_persistent_context(
            user_data_dir=SESSAO_DIR,
            headless=False, 
            viewport={"width": 1280, "height": 800}
        )
        
        page = context.pages[0]

        # Função para escutar os WebSockets (os dados brutos do mercado)
        def on_websocket(ws):
            print(f"📡 [WebSocket Conectado] {ws.url}")
            ws.on("framereceived", lambda payload: print(f"📥 [Dados Recebidos] {str(payload)[:150]}..."))

        page.on("websocket", on_websocket)

        print("🌐 [Andax Corpo] Acessando a Axion Trade...")
        await page.goto(URL_AXION)
        
        # Tenta pré-preencher o login automaticamente
        try:
            print("⌨️ Tentando preencher as credenciais automaticamente...")
            # Espera um pouco para a página carregar
            await page.wait_for_timeout(3000) 
            
            # Procura o campo de email (ajuste os seletores se necessário)
            email_input = await page.query_selector('input[type="email"], input[name="email"], input[placeholder*="mail" i]')
            if email_input:
                await email_input.fill(EMAIL)
                print("✅ Email preenchido.")
            
            # Procura o campo de senha
            pass_input = await page.query_selector('input[type="password"]')
            if pass_input:
                await pass_input.fill(SENHA)
                print("✅ Senha preenchida.")
            
            # Clica no botão de login (se encontrar)
            # Nota: O botão pode ter textos como "Login", "Entrar", "Sign In"
            # await page.click('button[type="submit"]') 
            
        except Exception as e:
            print(f"⚠️ Não foi possível pré-preencher automaticamente: {e}")
            print("Você pode preencher manualmente na janela do navegador.")

        print("\n⚠️ AÇÃO NECESSÁRIA:")
        print("1. Na janela do navegador, conclua o login na sua conta Axion Trade.")
        print("2. Se for pedido um código de verificação (OTP) enviado por e-mail, insira-o.")
        print("3. Vá para a tela de negociação (onde fica o gráfico).")
        print("4. Volte aqui no terminal e aperte ENTER.\n")
        
        input("Pressione ENTER após estar logado e na tela do gráfico...")
        
        print("\n👁️ [Andax Corpo] Iniciando captura de dados em tempo real por 20 segundos...")
        await asyncio.sleep(20)
        
        print("\n✅ Teste concluído. Fechando navegador...")
        await context.close()

if __name__ == "__main__":
    asyncio.run(main())
