import chromadb
import ollama
from chromadb.utils import embedding_functions

print("🧠 [Andax] Acordando com o cérebro multilíngue...")

client = chromadb.PersistentClient(path="./chroma_db")
multi_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="paraphrase-multilingual-MiniLM-L12-v2")

# O SEGREDO ESTÁ AQUI: Apontando para a coleção correta!
collection = client.get_collection(name="livros_trade_multi", embedding_function=multi_ef)

pergunta = "O que os livros dizem sobre como identificar um suporte forte e qual a melhor hora de comprar?"

print(f"\n❓ Pergunta: {pergunta}")
print("🔍 Buscando respostas nos seus livros...")

resultados = collection.query(
    query_texts=[pergunta],
    n_results=3
)

contexto = "\n\n---\n\n".join(resultados['documents'][0])

print("\n📖 [O QUE O ANDAX ENCONTROU NOS LIVROS]:")
print("="*50)
for i, doc in enumerate(resultados['documents'][0]):
    print(f"Trecho {i+1}: {doc[:400]}...\n")
print("="*50)

print("🤖 [Andax] Analisando o conhecimento e formulando a resposta...\n")

prompt = f"""
Você é o Andax, um trader profissional especialista em análise técnica.
Responda à pergunta baseando-se nos trechos fornecidos. Seja direto e prático.

TRECHOS DOS LIVROS:
{contexto}

PERGUNTA: {pergunta}
"""

try:
    # Usando o modelo mais leve e rápido (qwen2.5:3b)
    resposta = ollama.chat(model='qwen2.5:3b', messages=[
        {'role': 'user', 'content': prompt}
    ])
    print("💡 [RESPOSTA DO ANDAX]:")
    print("="*50)
    print(resposta['message']['content'])
    print("="*50)
except Exception as e:
    print(f"❌ Erro na IA: {e}")
