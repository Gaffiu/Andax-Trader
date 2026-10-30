import asyncio
import json
import os
from playwright.async_api import async_playwright

SESSAO_DIR = "./sessao_axion"

async def configurar_plataforma(page):
    print("\n🛠️ [Andax] Configurando a plataforma (Tempo e Valor)...")
    try:
        # 1. Clicar no tempo de 5 minutos (usando JavaScript para ignorar a viewport)
        botao_5m = page.locator("span.timeframe-btn", has_text="5m").first
        if await botao_5m.count() > 0:
            await botao_5m.evaluate("el => el.click()")
            print("✅ Tempo alterado para 5 minutos.")
            await asyncio.sleep(1)
        
        # 2. Clicar no valor de 10
        botao_10 = page.locator("button:has-text('10')").first
        if await botao_10.count() > 0:
            await botao_10.evaluate("el => el.click()")
            print("✅ Valor alterado para $10.")
            await asyncio.sleep(1)
            
    except Exception as e:
        print(f"⚠️ Aviso: Não consegui alterar tempo/valor automaticamente: {e}")

async def vigiar_decisao(page):
    ultima_decisao = None
    em_operacao = False 
    
    while True:
        try:
            if os.path.exists("decisao_atual.json"):
                with open("decisao_atual.json", "r") as f:
                    dados = json.load(f)
                    decisao = dados.get("decisao", "AGUARDAR")
                    
                if decisao != ultima_decisao and not em_operacao:
                    print(f"\n🎯 Nova Decisão Detectada: {decisao}")
                    ultima_decisao = decisao
                    
                    if decisao == "COMPRAR":
                        botao = page.locator("button.btn-call").first
                        if await botao.count() > 0:
                            await botao.evaluate("el => el.style.boxShadow = '0 0 20px 5px #00ff00'")
                            print("🟢 Botão ACIMA destacado! Executando em 2s...")
                            await asyncio.sleep(2)
                            await botao.evaluate("el => el.click()") # Força o clique
                            print("✅ ORDEM DE COMPRA ENVIADA!")
                            await botao.evaluate("el => el.style.boxShadow = 'none'")
                            em_operacao = True
                            
                    elif decisao == "VENDER":
                        botao = page.locator("button.btn-put").first
                        if await botao.count() > 0:
                            await botao.evaluate("el => el.style.boxShadow = '0 0 20px 5px #ff0000'")
                            print("🔴 Botão ABAIXO destacado! Executando em 2s...")
                            await asyncio.sleep(2)
                            await botao.evaluate("el => el.click()") # Força o clique
                            print("✅ ORDEM DE VENDA ENVIADA!")
                            await botao.evaluate("el => el.style.boxShadow = 'none'")
                            em_operacao = True

                if em_operacao:
                    await asyncio.sleep(310) # Espera 5 minutos + 10s
                    print("⏱️ Tempo de trade (5m) concluído. Liberando nova operação...")
                    em_operacao = False
                    ultima_decisao = None 
                    
        except Exception as e:
            pass
            
        await asyncio.sleep(2)

async def main():
    async with async_playwright() as p:
        print("🤖 [Andax Corpo] Abrindo a Axion Trade...")
        # Aumentando a janela para 1920x1080 para caber tudo na tela
        context = await p.chromium.launch_persistent_context(
            user_data_dir=SESSAO_DIR, headless=False, viewport={"width": 1920, "height": 1080}
        )
        page = context.pages[0]
        await page.goto("https://axion-trade.com/trade") 
        
        print("\n⚠️ AÇÃO NECESSÁRIA:")
        print("1. Se não estiver logado, faça o login.")
        print("2. Vá para a tela de trade.")
        input("3. Pressione ENTER quando estiver na tela...")
        
        await configurar_plataforma(page)
        
        print("\n👁️ [Andax] Vigilância ativada. Aguardando sinais do cérebro...")
        await vigiar_decisao(page)

if __name__ == "__main__":
    asyncio.run(main())
