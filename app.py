import streamlit as st

st.set_page_config(page_title="Animal Advocators")

# Custom CSS for earthy and watery color scheme
st.markdown("""
    <style>
    /* Main background - earthy cream */
    .main {
        background-color: #F5F1E8;
    }
    
    /* Header styling */
    h1, h2, h3 {
        color: #3D5A3D !important;
    }
    
    /* Sidebar background - watery blue */
    [data-testid="stSidebar"] {
        background-color: #4A90A4 !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: #FFFFFF !important;
    }
    
    /* Button styling - earthy brown */
    .stButton > button {
        background-color: #8B6F47 !important;
        color: #FFFFFF !important;
        border: 2px solid #6B5A3D !important;
        font-weight: bold !important;
        border-radius: 8px !important;
    }
    
    .stButton > button:hover {
        background-color: #A0845C !important;
        border-color: #8B6F47 !important;
    }
    
    /* Slider styling - green earthy */
    .stSlider [role="slider"] {
        background-color: #7CB342 !important;
    }
    
    .stSlider [data-testid="stTickBar"] {
        background-color: #558B2F !important;
    }
    
    /* Input fields - light cream with green accent */
    .stTextInput input, .stNumberInput input {
        background-color: #FFFEF9 !important;
        color: #3D5A3D !important;
        border: 2px solid #7CB342 !important;
    }
    
    /* Success message - green */
    .stSuccess {
        background-color: #E8F5E9 !important;
        color: #2E7D32 !important;
    }
    
    /* Map container - watery blue background */
    .stDeckGlJsonChart {
        background-color: #B3D9E8 !important;
    }
    
    /* Text color - earthy brown */
    .stMarkdown, p {
        color: #5C4033 !important;
    }
    
    /* Accent color for highlights - golden yellow */
    .stMetricValue {
        color: #D4A500 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# This shows the title of the website.
st.title("🌿 Animal Advocators 💧")

# This lets users search for an animal or location.
st.markdown("### 🔍 Search for Animals or Locations")
search = st.text_input("Enter animal name or location", placeholder="e.g., Tiger, Amazon Rainforest")

# This lets users choose a donation amount.
st.markdown("### 💚 Support Our Mission")
st.markdown("Your donation helps protect wildlife and their habitats.")
amount = st.slider("Donation amount ($)", 0, 500, 25)
if st.button("🌍 Donate Now"):
    st.success(f"🎉 Thank you for donating ${amount}! Your contribution helps protect endangered species.")

# This lets users pick a location on a simple map.
st.markdown("### 📍 Choose a Location")
st.markdown("Select or adjust the location on the map to explore wildlife in that area.")
st.map({"lat": [37.7749], "lon": [-122.4194]})

col1, col2 = st.columns(2)
with col1:
    lat = st.number_input("Latitude", value=37.7749, format="%.4f")
with col2:
    lon = st.number_input("Longitude", value=-122.4194, format="%.4f")

st.markdown(f"""
    <div style="background-color: #E8F5E9; padding: 15px; border-radius: 8px; border-left: 4px solid #7CB342;">
        <p style="color: #2E7D32; font-weight: bold;">📌 Selected Location: {lat}°N, {lon}°E</p>
    </div>
    """, unsafe_allow_html=True)


