import chromadb
import ollama
from chromadb.utils import embedding_functions

print("🧠 [Andax] Acordando e conectando à biblioteca de livros...")

# Conecta ao banco de dados que acabamos de criar
client = chromadb.PersistentClient(path="./chroma_db")
default_ef = embedding_functions.DefaultEmbeddingFunction()
collection = client.get_collection(name="livros_trade", embedding_function=default_ef)

# O que você quer perguntar ao Andax?
pergunta = "O que os livros dizem sobre como identificar um suporte forte e qual a melhor hora de comprar?"

print(f"\n❓ Pergunta: {pergunta}")
print("🔍 Buscando respostas nos seus livros...")

# 1. Busca os 4 trechos mais relevantes da biblioteca
resultados = collection.query(
    query_texts=[pergunta],
    n_results=4
)

# Junta os trechos encontrados
contexto = "\n\n---\n\n".join(resultados['documents'][0])

print("🤖 [Andax] Analisando o conhecimento e formulando a resposta...\n")

# 2. Monta o prompt para a IA
prompt = f"""
Você é o Andax, um trader profissional especialista em análise técnica.
Responda à pergunta do usuário baseando-se ESTRITAMENTE nos trechos de livros fornecidos abaixo.
Se os livros não tiverem a resposta, diga que não encontrou nos livros.

TRECHOS DOS LIVROS:
{contexto}

PERGUNTA DO USUÁRIO: {pergunta}
"""

# 3. Consulta o Ollama (qwen2.5)
try:
    resposta = ollama.chat(model='qwen2.5:7b', messages=[
        {'role': 'user', 'content': prompt}
    ])
    print("💡 [RESPOSTA DO ANDAX]:")
    print("="*50)
    print(resposta['message']['content'])
    print("="*50)
except Exception as e:
    print(f"❌ Erro na IA: {e}")
