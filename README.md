# PermitGPT: The AI Zoning Decoder

**PermitGPT** is a Geospatial AI tool that helps Hamilton & Toronto residents understand complex zoning 
bylaws instantly. Instead of paying lawyers to read 500-page PDF documents, users can click any property on 
a 3D map to see exactly what they are allowed to build (e.g., Garden Suites, Laneway Houses).

## Features
* **Interactive 3D Map:** Visualizes zoning districts using **PyDeck** and **Streamlit**.
* **RAG "Brain":** Uses **LangChain** and **ChromaDB** to index thousands of pages of municipal bylaws.
* **AI Analysis:** Powered by **Google Gemini**, translating legal jargon into plain English.
* **Geospatial Engine:** Built on **Geopandas** for precise coordinate transformations.

## Tech Stack
* **Frontend:** Streamlit, PyDeck
* **Spatial:** Geopandas, Shapely
* **AI/LLM:** LangChain, Google Gemini (1.5 Flash), ChromaDB (Vector Store)

## How to Run Locally
1. Clone the repo
2. Install dependencies: `pip install -r requirements.txt`
3. Add your API Key to `.env`: `GOOGLE_API_KEY=...`
4. Run the app: `streamlit run src/app.py`

## Status
* [x] Map Engine (Live)
* [x] PDF Ingestion Pipeline (Live)
* [ ] AI Chat Integration (In Progress)
