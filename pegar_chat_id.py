import requests
import json

TOKEN = "9011607401:AAHg5BxZvuiXxTX7U4aCAuwPS9CEY1B7L38"

print("🔍 Buscando o seu Chat ID no Telegram...")
url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
resposta = requests.get(url).json()

if resposta.get("result"):
    # Pega a última mensagem enviada para o bot
    chat_id = resposta["result"][-1]["message"]["chat"]["id"]
    print(f"✅ Chat ID encontrado: {chat_id}")
    
    # Salva no arquivo de configuração
    with open("telegram_config.json", "r") as f:
        config = json.load(f)
    
    config["chat_id"] = str(chat_id)
    
    with open("telegram_config.json", "w") as f:
        json.dump(config, f, indent=4)
        
    print("✅ Arquivo telegram_config.json atualizado com sucesso!")
    
    # Envia mensagem de teste
    msg_teste = "🤖 Andax: Conexão estabelecida com sucesso! Seu robô está online."
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": chat_id, "text": msg_teste})
    print("📩 Mensagem de teste enviada para o seu Telegram!")
else:
    print("❌ Nenhuma mensagem encontrada. Vá no Telegram e mande um 'Oi' para o seu bot, depois rode este script de novo.")
