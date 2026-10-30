import asyncio
import websockets
import json
import ollama
import chromadb
import re
import pandas as pd
from chromadb.utils import embedding_functions

print("🧠 [Andax] Carregando biblioteca e ligando os indicadores matemáticos...")
client_db = chromadb.PersistentClient(path="./chroma_db")
multi_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="paraphrase-multilingual-MiniLM-L12-v2")
collection = client_db.get_collection(name="livros_trade_multi", embedding_function=multi_ef)

candles = []
fechamentos = []

def calcular_rsi(precos, periodo=14):
    if len(precos) < periodo: return 50 
    deltas = pd.Series(precos).diff()
    ganhos = deltas.clip(lower=0)
    perdas = -deltas.clip(upper=0)
    media_ganhos = ganhos.rolling(window=periodo).mean()
    media_perdas = perdas.rolling(window=periodo).mean()
    rs = media_ganhos / media_perdas
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

async def analisar_e_decidir():
    if len(candles) < 15: 
        print("⏳ Coletando dados para calcular os indicadores (precisa de 15 candles)...")
        return 
    
    rsi = calcular_rsi(fechamentos)
    ultimo_candle = candles[-1]
    preco_atual = float(ultimo_candle['fechamento'])
    
    # Verifica a cor do último candle
    cor_candle = "VERDE (Alta)" if float(ultimo_candle['fechamento']) > float(ultimo_candle['abertura']) else "VERMELHO (Baixa)"
    
    print(f"🧮 [Indicadores] RSI: {rsi:.2f} | Candle: {cor_candle} | Preço: {preco_atual:.2f}")
    print("🧠 [Andax] Analisando com base nos livros e na matemática...")
    
    pergunta = "Como identificar reversão usando RSI sobrevendido/sobrecomprado e candles de reversão?"
    resultados = collection.query(query_texts=[pergunta], n_results=2)
    contexto = "\n".join(resultados['documents'][0])

    prompt = f"""
    Você é o Andax, um trader profissional e conservador.
    
    INDICADORES ATUAIS:
    - RSI: {rsi:.2f} (Abaixo de 30 é sobrevendido, acima de 70 é sobrecomprado)
    - Cor do último candle: {cor_candle}
    - Preço Atual: {preco_atual:.2f}
    
    REGRAS OBRIGATÓRIAS:
    - Só COMPRE se o RSI estiver abaixo de 35 E a cor do último candle for VERDE (Alta).
    - Só VENDA se o RSI estiver acima de 65 E a cor do último candle for VERMELHO (Baixa).
    - Se estiver no meio, responda AGUARDAR.
    
    Responda ESTRITAMENTE em formato JSON: {{"decisao": "COMPRAR" | "VENDER" | "AGUARDAR", "justificativa": "curta"}}
    
    TRECHOS DOS LIVROS:
    {contexto[:1000]} 
    """
    
    try:
        resposta = ollama.chat(model='qwen2.5:3b', messages=[{'role': 'user', 'content': prompt}])
        texto_limpo = re.sub(r'```json|```', '', resposta['message']['content']).strip()
        
        with open("decisao_atual.json", "w") as f:
            f.write(texto_limpo)
            
        print("🤖 [DECISÃO DO ANDAX]:")
        print(texto_limpo)
    except Exception as e:
        print(f"❌ Erro na IA: {e}")

async def loop_trading():
    uri = "wss://data-stream.binance.vision/ws/btcusdt@kline_1m"
    while True:
        try:
            print("\n📡 [Andax] Conectando aos dados da Binance...")
            async with websockets.connect(uri, ping_interval=20, ping_timeout=20) as websocket:
                while True:
                    mensagem = await websocket.recv()
                    dados = json.loads(mensagem)
                    if dados['e'] == 'kline' and dados['k']['x'] == True:
                        fechamento = dados['k']['c']
                        candles.append({"abertura": dados['k']['o'], "fechamento": fechamento, "maxima": dados['k']['h'], "minima": dados['k']['l']})
                        fechamentos.append(float(fechamento))
                        
                        if len(candles) > 50: 
                            candles.pop(0)
                            fechamentos.pop(0)
                            
                        print(f"\n📊 Candle Fechado! Preço: {fechamento}")
                        
                        await analisar_e_decidir()
                        print("⏳ Aguardando próximo candle...")
        except Exception as e:
            print(f"⚠️ Erro: {e}. Reconectando em 5s...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(loop_trading())
