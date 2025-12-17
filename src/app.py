import streamlit as st
import geopandas as gpd
import pydeck as pdk
import os
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser


st.set_page_config(layout="wide", page_title="PermitGPT")
load_dotenv()

@st.cache_resource
def load_ai_engine():
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
    
    if not os.path.exists("data/chroma_db"):
        return None
        
    vector_db = Chroma(persist_directory="data/chroma_db", embedding_function=embeddings)
    
    retriever = vector_db.as_retriever(search_kwargs={"k": 3})
    
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
    
    template = """Answer the question based only on the following context:
    {context}

    Question: {question}
    """
    prompt = ChatPromptTemplate.from_template(template)

    # E. The "Chain" (This is the LCEL magic: Search -> Prompt -> AI -> String)
    # This replaces the broken 'RetrievalQA' class entirely.
    def format_docs(docs):
        return "\n\n".join([d.page_content for d in docs])

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return chain

qa_chain = None
if os.getenv("GOOGLE_API_KEY"):
    try:
        qa_chain = load_ai_engine()
    except Exception as e:
        st.warning(f"AI failed to load: {e}")


@st.cache_data

def load_data():
    gdf = gpd.read_file("data/raw/toronto_zoning.geojson")

    if gdf.crs.to_string() != "EPSG:4326":
        gdf = gdf.to_crs(epsg=4326)
    return gdf

st.title("PermitGPT: Ontario Zoning Decoder")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### Click on any zone to see its 'Secret Code'")

    try:    
        data = load_data()

        layer = pdk.Layer(
            "GeoJsonLayer",
            data,
            opacity=0.4,
            stroked=True,
            filled=True,
            get_fill_color="[0, 150, 255, 100]",
            get_line_color="[255, 255, 255]",
            pickable=True,
            auto_highlight=True,
        )

        view_state = pdk.ViewState(
            latitude=43.6532,
            longitude=-79.3832,
            zoom=13,
            pitch=0,
        )

        st.pydeck_chart(pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip={"text": "Zone: {ZN_STRING}\nCategory: {GEN_ZONE}"}
        ))
    except Exception as e:
        st.error(f"Error loading map: {e}")

with col2:
    st.markdown("### 🤖 Zoning Assistant")
    st.info("Ask questions based on the Toronto Zoning Bylaw PDFs.")

    query = st.text_input("Question:", placeholder="e.g., What is the max height in Residential zones?")
    if st.button("Ask AI") and query:
        if not qa_chain:
            st.error("AI is not connected. Check API Key or run ingest.py.")
        else:
            with st.spinner("Reading Bylaws..."):
                try:
                    # Invoke the LCEL chain directly
                    response = qa_chain.invoke(query)
                    st.success("Answer found:")
                    st.write(response)
                except Exception as e:
                    st.error(f"Error during analysis: {e}")

                with st.expander("See Source Context"):
                    st.caption("Information retrieved from Vector Database based on semantic similarity.")

