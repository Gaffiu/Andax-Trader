import asyncio
import json
import requests
from playwright.async_api import async_playwright

with open("telegram_config.json", "r") as f:
    config = json.load(f)
TOKEN = config["token"]
CHAT_ID = config["chat_id"]

url_api = f"https://api.telegram.org/bot{TOKEN}/getUpdates"

def enviar_telegram(msg):
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": msg})

async def executar_trade(page, acao):
    print(f"⚡ Executando {acao} na Axion...")
    botao = page.locator("button.btn-call").first if acao == "COMPRAR" else page.locator("button.btn-put").first
        
    if await botao.count() > 0:
        await botao.evaluate("el => el.style.boxShadow = '0 0 20px 5px #00ff00'")
        await asyncio.sleep(1)
        await botao.click()
        print(f"✅ Ordem de {acao} enviada! Aguardando 5 minutos...")
        
        await asyncio.sleep(305) # Espera 5 min + 5 seg (delay da Axion)
        
        # LÊ O RESULTADO NA TELA (Histórico da Axion)
        try:
            # Pega o texto do primeiro item do histórico
            item_historico = await page.locator("div.flex.items-center.gap-2\\.5.py-1\\.5").first.inner_text()
            print(f"Histórico lido: {item_historico}")
            
            if "+$" in item_historico:
                enviar_telegram("RESULTADO: WIN")
                print("🟢 GREEN! Avisando o Cérebro.")
            elif "-$" in item_historico:
                enviar_telegram("RESULTADO: LOSS")
                print("🔴 RED! Avisando o Cérebro.")
        except Exception as e:
            print(f"⚠️ Erro ao ler histórico: {e}")

async def vigiar_telegram(page):
    print("👁️ [Andax Corpo] Escutando o Telegram...")
    ultimo_id = None
    
    while True:
        try:
            params = {"timeout": 10}
            if ultimo_id: params["offset"] = ultimo_id + 1
                
            resp = requests.get(url_api, params=params, timeout=15).json()
            
            if resp.get("result"):
                for update in resp["result"]:
                    ultimo_id = update["update_id"]
                    
                    if "message" in update and "text" in update["message"]:
                        texto = update["message"]["text"]
                        chat_id_msg = str(update["message"]["chat"]["id"])
                        
                        if chat_id_msg == str(CHAT_ID) and ("COMPRAR" in texto or "VENDER" in texto):
                            acao = "COMPRAR" if "COMPRAR" in texto else "VENDER"
                            await executar_trade(page, acao)
                            
        except Exception:
            pass
            
        await asyncio.sleep(3)

async def main():
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir="./sessao_axion", headless=False, viewport={"width": 1920, "height": 1080}
        )
        page = context.pages[0]
        await page.goto("https://axion-trade.com/trade")
        
        input("1. Faça login na Axion.\n2. Aperte ENTER para o robô assumir...")
        
        await page.locator("span.timeframe-btn", has_text="5m").first.evaluate("el => el.click()")
        await page.locator("button:has-text('10')").first.evaluate("el => el.click()")
        
        await vigiar_telegram(page)

if __name__ == "__main__":
    asyncio.run(main())
