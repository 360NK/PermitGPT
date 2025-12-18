import json
import os
import geopandas as gpd
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

import time

load_dotenv()
DB_PATH = "data/chroma_db"
OUTPUT_FILE = "data/zone_dictionary.json"

def load_ai_chain():
    print("🧠 Loading AI Brain...")
    
    # A. Translator
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
    
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database not found at {DB_PATH}. Run ingest.py first.")
        
    vector_db = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
    retriever = vector_db.as_retriever(search_kwargs={"k": 5})
    
    llm = ChatGoogleGenerativeAI(model="models/gemini-flash-latest", temperature=0)
    
    # D. Prompt
    template = """
    You are a Zoning Expert. Analyze the provided context about the zoning category: '{zone_name}'.
    
    Create a structured summary with exactly these 3 sections:
    1. **Permitted Uses**: (List the main allowed building types)
    2. **Physical Rules**: (Max height, setbacks, coverage if mentioned)
    3. **Prohibitions**: (What is strictly explicitly prohibited)
    
    Context from Bylaws:
    {context}
    
    Keep it professional and concise.
    """
    prompt = ChatPromptTemplate.from_template(template)

    # E. The Chain (Retriever | Format | Prompt | LLM | String)
    def format_docs(docs):
        return "\n\n".join([d.page_content for d in docs])

    chain = (
        {"context": retriever | format_docs, "zone_name": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return chain

def generate_zone_summaries():
    print("🗺️  Loading Map Data to find Zone Categories...")
    gdf = gpd.read_file("data/raw/toronto_zoning.geojson")
    unique_zones = gdf['GEN_ZONE'].dropna().unique()
    
    print(f"🔍 Found {len(unique_zones)} unique zone categories: {unique_zones}")
    
    try:
        chain = load_ai_chain()
    except Exception as e:
        print(f"Critical Error loading AI: {e}")
        return

    zone_data = {}

    print("Starting Batch Analysis (This may take 1-2 minutes)...")
    
    for i, zone in enumerate(unique_zones):
        print("🚀 Starting Batch Analysis...")
        print("⏳ We will wait 60 seconds between zones to guarantee success.")
        
        for i, zone in enumerate(unique_zones):
            print(f"\n[{i+1}/{len(unique_zones)}] 🤖 Analyzing Zone: {zone}...")
            
            # RETRY LOGIC: Try up to 3 times per zone
            success = False
            attempts = 0
            
            while not success and attempts < 3:
                try:
                    # We pass the zone name as the input to the chain
                    response = chain.invoke(str(zone))
                    zone_data[str(zone)] = response
                    print("   ✅ Success.")
                    success = True
                except Exception as e:
                    attempts += 1
                    wait_time = 60 * attempts # Wait 60s, then 120s, etc.
                    print(f"   ⚠️ Error (Attempt {attempts}/3): {e}")
                    print(f"   💤 Hit Rate Limit. Waiting {wait_time}s before retrying...")
                    time.sleep(wait_time)
            
            if not success:
                print("   ❌ Failed after 3 attempts. Skipping.")
                zone_data[str(zone)] = "Data unavailable."

            # Standard cool-down between successful calls
            if i < len(unique_zones) - 1:
                time.sleep(10)

    # Save to disk
    with open(OUTPUT_FILE, "w") as f:
        json.dump(zone_data, f, indent=4)
    
    print(f"DONE! Summaries saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_zone_summaries()
