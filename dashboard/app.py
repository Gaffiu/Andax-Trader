import streamlit as st
import json
import os
import time

st.set_page_config(page_title="Andax Trader", page_icon="🤖", layout="centered")
st.title("🤖 Andax Trader - Painel")
st.markdown("Acompanhe as decisões da IA em tempo real.")

placeholder = st.empty()

while True:
    if os.path.exists("decisao_atual.json"):
        with open("decisao_atual.json", "r") as f:
            try:
                dados = json.load(f)
                decisao = dados.get("decisao", "AGUARDAR")
                justificativa = dados.get("justificativa", "")
                
                with placeholder.container():
                    if decisao == "COMPRAR":
                        st.success(f"📈 SINAL: **COMPRAR**")
                    elif decisao == "VENDER":
                        st.error(f"📉 SINAL: **VENDER**")
                    else:
                        st.warning(f"⏳ SINAL: **AGUARDAR**")
                        
                    st.write(f"**Justificativa da IA:** {justificativa}")
            except:
                st.info("Lendo dados...")
    else:
        st.info("Aguardando o Cérebro gerar a primeira decisão...")
        
    time.sleep(2)
