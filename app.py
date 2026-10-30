import asyncio
import websockets
import json
import os
import re
import pandas as pd
import requests
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Configurações
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
client_groq = Groq(api_key=GROQ_API_KEY)

def enviar_telegram(msg):
    try:
        if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": msg}, timeout=5)
    except: pass

print("🧠 [Andax Cloud] Iniciando Cérebro na Nuvem...")
candles = []
fechamentos = []
em_pausa = False
tempo_pausa = 0

def calcular_rsi(precos, periodo=14):
    if len(precos) < periodo: return 50 
    deltas = pd.Series(precos).diff()
    ganhos = deltas.clip(lower=0)
    perdas = -deltas.clip(upper=0)
    media_ganhos = ganhos.rolling(window=periodo).mean()
    media_perdas = perdas.rolling(window=periodo).mean()
    rs = media_ganhos / media_perdas
    return (100 - (100 / (1 + rs))).iloc[-1]

async def analisar_e_decidir():
    global em_pausa, tempo_pausa
    if len(candles) < 15: return 
    
    if em_pausa:
        tempo_pausa -= 1
        if tempo_pausa <= 0:
            em_pausa = False
            enviar_telegram("▶️ Andax: Pausa encerrada. Voltando a operar.")
        else:
            return

    rsi = calcular_rsi(fechamentos)
    ultimo_candle = candles[-1]
    preco_atual = float(ultimo_candle['fechamento'])
    cor_candle = "VERDE" if float(ultimo_candle['fechamento']) > float(ultimo_candle['abertura']) else "VERMELHO"
    
    maximas = [float(c['maxima']) for c in candles]
    minimas = [float(c['minima']) for c in candles]
    amplitude = max(maximas) - min(minimas)
    volatilidade = (amplitude / preco_atual) * 100
    
    print(f"🧮 [Indicadores] RSI: {rsi:.2f} | Candle: {cor_candle} | Vol: {volatilidade:.3f}%")
    
    if volatilidade < 0.05:
        print("💤 [Andax] Mercado lateral. Pausando por 30 minutos.")
        enviar_telegram("💤 Andax: Mercado lateral detectado. Pausando operações por 30 minutos.")
        em_pausa = True
        tempo_pausa = 30
        return

    prompt = f"""
    Você é o Andax, um trader profissional e conservador.
    - RSI: {rsi:.2f} (Abaixo de 35 sobrevendido, acima de 65 sobrecomprado)
    - Cor do último candle: {cor_candle}
    
    REGRAS OBRIGATÓRIAS:
    - Só COMPRE se o RSI < 35 E o candle for VERDE.
    - Só VENDA se o RSI > 65 E o candle for VERMELHO.
    - Caso contrário, AGUARDAR.
    
    Responda ESTRITAMENTE em JSON: {{"decisao": "COMPRAR" | "VENDER" | "AGUARDAR", "justificativa": "curta"}}
    """
    
    try:
        chat_completion = client_groq.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192", 
        )
        texto = chat_completion.choices[0].message.content
        texto_limpo = re.sub(r'```json|```', '', texto).strip()
        
        with open("decisao_atual.json", "w") as f:
            f.write(texto_limpo)
            
        print("🤖 [DECISÃO]:", texto_limpo)
        
        dados_decisao = json.loads(texto_limpo)
        if dados_decisao.get("decisao") in ["COMPRAR", "VENDER"]:
            enviar_telegram(f"🎯 Andax: Sinal de {dados_decisao['decisao']} no BTC! Entrando...")
            
    except Exception as e:
        print(f"❌ Erro na Groq: {e}")

async def loop_trading():
    uri = "wss://data-stream.binance.vision/ws/btcusdt@kline_1m"
    while True:
        try:
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
                        print(f"📊 Candle: {fechamento}")
                        await analisar_e_decidir()
        except Exception as e:
            print(f"⚠️ Erro: {e}. Reconectando...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(loop_trading())
