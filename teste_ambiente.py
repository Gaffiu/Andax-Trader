import sys, requests
from PySide6.QtWidgets import QApplication, QLabel
from PySide6.QtCharts import QCandlestickSeries

app = QApplication(sys.argv)
w = QLabel("Andax — ambiente OK")
w.resize(400, 120)
w.show()

r = requests.post(
    "http://localhost:11434/api/generate",
    json={"model": "qwen2.5:7b", "prompt": "Responda apenas: Andax online.", "stream": False},
    timeout=120,
)
print("OLLAMA:", r.json()["response"].strip())
print("QtCharts: importado com sucesso")

sys.exit(app.exec())
