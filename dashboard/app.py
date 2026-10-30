import streamlit as st
import requests
import time

st.set_page_config(page_title="Andax Trader", page_icon="🤖", layout="centered")
st.title("🤖 Andax Trader - Painel Live")
st.markdown("Conectado à Nuvem via Telegram em tempo real.")

# Lê as credenciais dos Secrets do Streamlit
try:
    TOKEN = st.secrets["TELEGRAM_TOKEN"]
    CHAT_ID = st.secrets["TELEGRAM_CHAT_ID"]
except Exception as e:
    st.error("Erro ao carregar as credenciais do Telegram. Verifique os Secrets no Streamlit Cloud.")
    st.stop()

url_api = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
placeholder = st.empty()

ultimo_id = None
while True:
    try:
        params = {"timeout": 5, "limit": 5}
        resp = requests.get(url_api, params=params, timeout=10).json()
        
        if resp.get("result"):
            msgs = resp["result"]
            ultima_msg = msgs[-1]["message"]["text"]
            
            with placeholder.container():
                if "SINAL: COMPRAR" in ultima_msg:
                    st.success(f"📈 **{ultima_msg}**")
                elif "SINAL: VENDER" in ultima_msg:
                    st.error(f"📉 **{ultima_msg}**")
                elif "RESULTADO: WIN" in ultima_msg:
                    st.balloons()
                    st.info(f"🟢 **{ultima_msg}**")
                elif "RESULTADO: LOSS" in ultima_msg:
                    st.warning(f"🔴 **{ultima_msg}**")
                else:
                    st.write(f"📩 **{ultima_msg}**")
    except Exception as e:
        pass 
        
    time.sleep(3)
