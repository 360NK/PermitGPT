import streamlit as st
import geopandas as gpd
import pydeck as pdk
import json
import os

# --- CONFIGURATION ---
st.set_page_config(layout="wide", page_title="SiteFeasibility v1")

# --- 1. LOAD DATA (Fast & Free) ---
@st.cache_data
def load_static_data():
    # A. Load Map
    gdf = gpd.read_file("data/raw/toronto_zoning.geojson")
    # Ensure correct coordinate system for PyDeck
    if gdf.crs.to_string() != "EPSG:4326":
        gdf = gdf.to_crs(epsg=4326)
        
    # B. Load AI Summaries (The file you just made)
    if not os.path.exists("data/zone_dictionary.json"):
        st.error("❌ 'data/zone_dictionary.json' not found. Run precompute.py first!")
        return None, {}
        
    with open("data/zone_dictionary.json", "r") as f:
        summaries = json.load(f)
        
    return gdf, summaries

# Run the loader
try:
    data, zone_summaries = load_static_data()
    if data is None:
        st.stop()
except Exception as e:
    st.error(f"Critical Error loading data: {e}")
    st.stop()

# --- 2. HEADER ---
st.title("🏗️ Site Feasibility Engine")
st.caption("Select a zone category to see instant development rights (Pre-computed by Gemini).")


# --- 3. LAYOUT ---
col1, col2 = st.columns([3, 1])

# --- LEFT COLUMN: THE MAP ---
with col1:
    # 1. Get all available zones
    all_zones = sorted(data['GEN_ZONE'].unique().astype(str))
    
    # 2. The Filter
    zone_filter = st.multiselect(
        "Filter Map by Zone Category:", 
        options=all_zones,
        default=all_zones[:1] # Default to just the first one so it's clean
    )
    
    # 3. Apply Filter to Map
    if zone_filter:
        filtered_data = data[data['GEN_ZONE'].astype(str).isin(zone_filter)]
    else:
        filtered_data = data

    # ... (Keep your PyDeck Code exactly the same) ...
    layer = pdk.Layer(
        "GeoJsonLayer",
        filtered_data,
        opacity=0.5,
        stroked=True,
        filled=True,
        get_fill_color="[0, 150, 255, 140]",
        get_line_color="[255, 255, 255, 200]",
        pickable=True,
        auto_highlight=True,
    )
    
    view_state = pdk.ViewState(latitude=43.6532, longitude=-79.3832, zoom=12, pitch=0)

    st.pydeck_chart(pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/dark-v11",
        tooltip={"text": "Zone Code: {ZN_STRING}\nCategory: {GEN_ZONE}"}
    ))

# --- RIGHT COLUMN: THE DASHBOARD ---
with col2:
    st.subheader("📋 Development Specs")
    
    # INTELLIGENT LOGIC:
    # If the user filtered the map, automatically pick the first filtered zone.
    # If they didn't filter, just pick the first zone in the list.
    
    if zone_filter:
        # User filtered map -> Auto-select that zone for the dashboard
        default_index = all_zones.index(zone_filter[0])
    else:
        default_index = 0

    def format_zone_labels(option):
        # A simple dictionary to map codes to human names
        # You can add more mappings as you discover them
        mapping = {
            "1": "1 - Residential (Low Density)",
            "2": "2 - Residential (Multi-Unit)",
            "6": "6 - Commercial",
            "201": "201 - Mixed Use"
        }
        # If the code isn't in the list, just show "Zone Code: X"
        return mapping.get(option, f"Zone Code: {option}")
        
    # The Selector now "listens" to the map filter via `index=default_index`
    selected_zone_cat = st.selectbox(
        "Inspect Rules for Category:", 
        options=all_zones,
        index=default_index,  # <--- THIS IS THE MAGIC LINK
        format_func=format_zone_labels
    )
    
    if selected_zone_cat:
        st.markdown("---")
        
        # LOOKUP: Get the text from the JSON file
        summary_text = zone_summaries.get(str(selected_zone_cat), "No summary available.")
        
        st.markdown(f"### Category: {selected_zone_cat}")
        st.info(summary_text)
        st.caption("ℹ️ Data extracted from Toronto Zoning Bylaw (Chapter 10-90).")