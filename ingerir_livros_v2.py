import os
import time
import logging
import chromadb
from chromadb.utils import embedding_functions
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

logging.getLogger("pypdf").setLevel(logging.ERROR)
logging.getLogger("fontTools").setLevel(logging.ERROR)

PASTA_LIVROS = "./livros"
DB_PATH = "./chroma_db"

print("🧠 1. Iniciando o cérebro multilíngue do Andax...")
if not os.path.exists(PASTA_LIVROS):
    print(f"❌ ERRO: A pasta '{PASTA_LIVROS}' não existe.")
    exit()

print("   Carregando PDFs da pasta...")
loader = PyPDFDirectoryLoader(PASTA_LIVROS)
docs = loader.load()
print(f"   -> {len(docs)} páginas carregadas.")

if len(docs) == 0:
    print("❌ ERRO: Nenhum PDF encontrado.")
    exit()

print("✂️ 2. Fatiando o texto...")
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=300)
chunks = text_splitter.split_documents(docs)
print(f"   -> {len(chunks)} pedaços gerados.")

print("🗄️ 3. Iniciando o ChromaDB com modelo MULTILÍNGUE...")
print("   (Isso pode demorar um pouco para carregar o modelo na memória)")
multi_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="paraphrase-multilingual-MiniLM-L12-v2")
client = chromadb.PersistentClient(path=DB_PATH)

# O SEGREDO ESTÁ AQUI: Nova coleção com o modelo correto
collection = client.get_or_create_collection(name="livros_trade_multi", embedding_function=multi_ef)

print("📥 4. Inserindo os textos no banco...")
textos = [c.page_content for c in chunks]
metadados = [c.metadata for c in chunks]
ids = [f"id_{i}" for i in range(len(chunks))]

batch_size = 500
inicio = time.time()

for i in range(0, len(textos), batch_size):
    collection.add(
        documents=textos[i:i+batch_size],
        metadatas=metadados[i:i+batch_size],
        ids=ids[i:i+batch_size]
    )
    tempo_decorrido = int(time.time() - inicio)
    print(f"   -> Inseridos {min(i+batch_size, len(textos))} de {len(textos)} pedaços. (Tempo: {tempo_decorrido}s)")

print("\n✅ Ingestão concluída com sucesso! Agora o cérebro do Andax entende português.")
