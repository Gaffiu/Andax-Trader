import asyncio
from playwright.async_api import async_playwright

SESSAO_DIR = "./sessao_axion"

async def main():
    async with async_playwright() as p:
        print("🤖 [Mapeador] Abrindo a Axion Trade...")
        context = await p.chromium.launch_persistent_context(
            user_data_dir=SESSAO_DIR, headless=False, viewport={"width": 1280, "height": 800}
        )
        page = context.pages[0]
        await page.goto("https://axion-trade.com/trade")

        print("\n⚠️ AÇÃO NECESSÁRIA:")
        print("1. Faça o login (se necessário).")
        print("2. Vá para a tela do gráfico.")
        print("3. CLIQUE NO MENU DE TEMPO (onde está '1min') e no MENU DE MOEDA (onde está 'BTC/USDT') para abrir as opções.")
        input("\nPressione ENTER aqui no terminal quando os menus estiverem abertos...")

        print("\n🔍 [Andax] Extraindo elementos da tela...")

        # Pega todos os elementos clicáveis ou textos visíveis
        elementos = await page.evaluate('''() => {
            const all = Array.from(document.querySelectorAll('button, a, div, span, li'));
            return all.map(el => {
                return {
                    tag: el.tagName,
                    texto: (el.innerText || '').trim(),
                    classe: el.className,
                    id: el.id
                };
            }).filter(el => el.texto !== '' && el.texto.length < 50);
        }''')

        # Remove duplicatas para facilitar a leitura
        unicos = []
        vistos = set()
        for el in elementos:
            chave = f"{el['texto']}-{el['classe']}"
            if chave not in vistos:
                vistos.add(chave)
                unicos.append(el)

        print("\n" + "="*50)
        print("ELEMENTOS ENCONTRADOS (Copie e cole no chat):")
        for i, el in enumerate(unicos):
            print(f"{i+1}. Texto: '{el['texto']}' | Tag: {el['tag']} | Classe: '{el['classe']}'")
        print("="*50)

        input("\nPressione ENTER para fechar o navegador...")
        await context.close()

if __name__ == "__main__":
    asyncio.run(main())
