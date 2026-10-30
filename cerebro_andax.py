import asyncio
import websockets
import json
import requests

# O cérebro do Andax (Ollama)
OLLAMA_URL = "http://localhost:11434/api/generate"
MODELO = "qwen2.5:7b"

# Guardaremos os candles aqui
candles = []

async def analisar_mercado():
    print("🧠 [Andax Cérebro] Conectando aos dados da Binance (BTC/USDT)...")
    uri = "wss://data-stream.binance.vision/ws/btcusdt@kline_1m"
    
    async with websockets.connect(uri) as websocket:
        while len(candles) < 5: # Vamos esperar 5 candles para ter contexto
            mensagem = await websocket.recv()
            dados = json.loads(mensagem)
            
            # Verifica se é um candle e se ele fechou (x=true)
            if dados['e'] == 'kline' and dados['k']['x'] == True:
                candle = {
                    "abertura": dados['k']['o'],
                    "fechamento": dados['k']['c'],
                    "maxima": dados['k']['h'],
                    "minima": dados['k']['l'],
                    "volume": dados['k']['v']
                }
                candles.append(candle)
                print(f"📊 Candle fechado! Preço: {candle['fechamento']}")
        
        print("\n🧠 [Andax Cérebro] Analisando dados com base nos livros...")
        
        # Prepara o prompt para a IA
        prompt = f"""
        Você é o Andax, um trader profissional que estudou os livros de análise técnica de Murphy, Flávio Lemos e Steve Nison.
        Aqui estão os últimos 5 candles de 1 minuto do BTC/USDT:
        {json.dumps(candles, indent=2)}
        
        Com base na análise de candles (candle patterns) e tendências, qual é a sua decisão?
        Responda de forma direta: COMPRAR, VENDER ou AGUARDAR. Justifique em uma frase.
        """
        
        # Envia para o Ollama
        payload = {
            "model": MODELO,
            "prompt": prompt,
            "stream": False
        }
        
        try:
            resposta = requests.post(OLLAMA_URL, json=payload, timeout=120)
            resultado = resposta.json()['response']
            print("\n🤖 [DECISÃO DO ANDAX]:")
            print(resultado)
        except Exception as e:
            print(f"❌ Erro ao consultar a IA: {e}")

if __name__ == "__main__":
    asyncio.run(analisar_mercado())
