import streamlit as st
import geopandas as gpd
import pydeck as pdk

st.set_page_config(layout="wide", page_title="PermitGPT")

@st.cache_data

def load_data():
    gdf = gpd.read_file("data/raw/toronto_zoning.geojson")

    if gdf.crs.to_string() != "EPSG:4326":
        gdf = gdf.to_crs(epsg=4326)
    return gdf

st.title("PermitGPT: Ontario Zoning Decoder")
st.markdown("### Click on any zone to see its 'Secret Code'")

with st.spinner("Reading satellite data..."):
    try:    
        data = load_data()
        st.success(f"Loaded {len(data)} zoning districts.")
    except Exception as e:
        st.error(f"Error loading data. check your 'data/raw' folder. Details: {e}")
        st.stop()

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

st.write("### Data Inspector")
st.dataframe(data[['ZN_STRING', 'GEN_ZONE']].head(10))
