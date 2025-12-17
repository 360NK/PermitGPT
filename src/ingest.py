import os
import shutil
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv

load_dotenv()
if not os.getenv("GOOGLE_API_KEY"):
    print("ERROR: GOOGLE_API_KEY not found in .env file.")
    exit()

PDF_FOLDER = "data/raw/"
DB_PATH = "data/chroma_db"

def ingest_documents():
    if os.path.exists(DB_PATH):
        print("Clearing old database...")
        shutil.rmtree(DB_PATH)

    documents = []
    
    print("Scanning data/raw/ for PDFs...")
    pdf_files = [f for f in os.listdir(PDF_FOLDER) if f.endswith('.pdf') and not f.startswith('._')]

    if not pdf_files:
        print("❌ No PDFs found! Please put volume2.pdf in data/raw/")
        return

    for pdf_file in pdf_files:
        path = os.path.join(PDF_FOLDER, pdf_file)
        print(f"   📖 Loading {pdf_file}...")
        loader = PyPDFLoader(path)
        docs = loader.load()
        documents.extend(docs)
    
    print(f"✅ Loaded {len(documents)} pages total.")

    print("✂️  Splitting text into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = text_splitter.split_documents(documents)
    print(f"   Created {len(chunks)} chunks.")

    print("🧠 Creating Vector Database (sending to Google Gemini)...")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=DB_PATH
    )

    print("🎉 SUCCESS: Knowledge Base built with Google Gemini! Saved to 'data/chroma_db'")


if __name__ == "__main__":
    ingest_documents()

