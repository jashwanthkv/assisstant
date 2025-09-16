from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import os
# Config
PDF_PATH = r"C:\Users\HP\PycharmProjects\MyAssiss\javanotes5-17-699.pdf"
CHROMA_DB_DIR = "./chromas_db"

if not os.path.exists(CHROMA_DB_DIR):
    os.makedirs(CHROMA_DB_DIR)
# Step 1: Load PDF lazily
print(f"db created at {CHROMA_DB_DIR}")
loader = PyPDFLoader(PDF_PATH)
pages = loader.load_and_split()   # loads page by page

# Step 2: Chunk pages
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
docs = splitter.split_documents(pages)

# Step 3: Embeddings
embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Step 4: Store in persistent Chroma
db = Chroma.from_documents(
    documents=docs,
    embedding=embedding,
    persist_directory=CHROMA_DB_DIR
)
db.persist()
print(f"Stored {len(docs)} chunks in Chroma DB")
