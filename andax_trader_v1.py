import asyncio
import websockets
import json
import ollama
import chromadb
import re
import pandas as pd
import requests
import os
from dotenv import load_dotenv
from chromadb.utils import embedding_functions

# Carrega as variáveis do arquivo .env
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# --- Configurações do Telegram ---
def enviar_telegram(msg):
    try:
        if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": msg}, timeout=5)
    except: pass

print("🧠 [Andax] Carregando biblioteca e ligando os indicadores matemáticos...")
# O resto do código continua igual...
