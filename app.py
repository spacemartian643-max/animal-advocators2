import streamlit as st
import pandas as pd
import pydeck as pdk

# -----------------------------------
# This sets up the page.
# -----------------------------------
st.set_page_config(
    page_title="Animal Advocators",
    page_icon="🦁",
    layout="wide"
)
from streamlit_option_menu import option_menu

# ----------------------------
# Navigation Menu
# ----------------------------
with st.sidebar:
    selected = option_menu(
        menu_title="☰ Animal Advocators",
        options=[
            "Home Page",
            "Overview",
            "Endangered Animal Library"
        ],
        icons=[
            "house-fill",
            "info-circle-fill",
            "book-fill"
        ],
        menu_icon="list",
        default_index=0,
    )

    # ----------------------------
# HOME PAGE
# ----------------------------
if selected == "Home Page":

    st.title("🌿 Animal Advocators")
    st.subheader("Voice the Voiceless")

    st.image(
        "https://images.unsplash.com/photo-1546182990-dffeafbe841d",
        use_container_width=True
    )

    st.markdown("""
    ## Welcome!

    Animal Advocators helps raise awareness for endangered animals around the world.

    Use the navigation menu on the left to:
    - Learn about endangered animals
    - Search the animal library
    - View animals on an interactive map
    - Donate to support conservation
    """)

    # ----------------------------
# OVERVIEW
# ----------------------------
elif selected == "Overview":

    st.title("🌎 Overview")

    st.write("""
    Animal Advocators is a website dedicated to educating people
    about endangered animals and promoting conservation efforts.

    Features include:
    - Animal Library
    - Interactive World Map
    - Search Function
    - Donation System
    """)

# ----------------------------
# ENDANGERED ANIMAL LIBRARY
# ----------------------------
elif selected == "Endangered Animal Library":

    # Paste ALL of your existing code beginning with:
    st.header("📚 Endangered Animal Library")

    # dataframe
    # map
    # animal information
    # donation buttons
    
# -----------------------------------
# Website title
# -----------------------------------
st.title("🌿 Animal Advocators")
st.subheader("Voice the Voiceless")

# -----------------------------------
# Search bar
# -----------------------------------
search = st.text_input(
    "Search for an endangered animal or region:"
)

# -----------------------------------
# Donation section
# -----------------------------------
st.header("💚 Donate")

donation = st.slider(
    "Choose a donation amount ($)",
    min_value=5,
    max_value=500,
    value=25,
    step=5
)

st.subheader("Choose a Payment Method")

# Store the selected payment method
if "payment_method" not in st.session_state:
    st.session_state.payment_method = None

# Create payment boxes
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("💳 Visa", use_container_width=True):
        st.session_state.payment_method = "Visa"

with col2:
    if st.button("💳 Mastercard", use_container_width=True):
        st.session_state.payment_method = "Mastercard"

with col3:
    if st.button("💳 American Express", use_container_width=True):
        st.session_state.payment_method = "American Express"

with col4:
    if st.button("💳 Chase", use_container_width=True):
        st.session_state.payment_method = "Chase Credit Card"

col5, col6, col7 = st.columns(3)

with col5:
    if st.button("🎁 Visa Gift Card", use_container_width=True):
        st.session_state.payment_method = "Visa Gift Card"

with col6:
    if st.button("🎁 Mastercard Gift Card", use_container_width=True):
        st.session_state.payment_method = "Mastercard Gift Card"

# Show payment form after a method is selected
if st.session_state.payment_method:

    st.markdown("---")
    st.subheader(f"Payment - {st.session_state.payment_method}")

    if "Gift Card" in st.session_state.payment_method:
        gift_code = st.text_input("Gift Card Code")
    else:
        card_number = st.text_input("Card Number")
        card_name = st.text_input("Name on Card")
        expiry = st.text_input("Expiration Date (MM/YY)")
        cvv = st.text_input("CVV", type="password")

    if st.button("Complete Donation"):

        if "Gift Card" in st.session_state.payment_method:
            if gift_code:
                st.success(
                    f"🎉 Thank you for donating ${donation} using {st.session_state.payment_method}!"
                )
            else:
                st.error("Please enter your gift card code.")
        else:
            if card_number and card_name and expiry and cvv:
                st.success(
                    f"🎉 Thank you for donating ${donation} using {st.session_state.payment_method}!"
                )
            else:
                st.error("Please complete all payment information.")

# -----------------------------------
# Endangered animal library
# -----------------------------------
animals = [
    {
        "Animal": "Amur Leopard",
        "Region": "Russia / China",
        "Status": "Critically Endangered",
        "Latitude": 43.2,
        "Longitude": 131.9,
        "Description": "One of the rarest big cats in the world.",
        "Keywords": "leopard leopards cat cats feline felines big cat"
    },
    {
        "Animal": "Javan Rhino",
        "Region": "Indonesia",
        "Status": "Critically Endangered",
        "Latitude": -6.75,
        "Longitude": 105.37,
        "Description": "Only a small population remains in Java.",
        "Keywords": "rhino rhinos rhinoceros rhinoceroses"
    },
    {
        "Animal": "Vaquita",
        "Region": "Gulf of California",
        "Status": "Critically Endangered",
        "Latitude": 31.0,
        "Longitude": -114.0,
        "Description": "The world's rarest marine mammal.",
        "Keywords": "vaquita porpoise porpoises marine mammal mammals"
    },
    {
        "Animal": "African Forest Elephant",
        "Region": "Central Africa",
        "Status": "Critically Endangered",
        "Latitude": 0.5,
        "Longitude": 21.0,
        "Description": "Threatened by habitat loss and poaching.",
        "Keywords": "elephant elephants"
    },
    {
        "Animal": "Red Wolf",
        "Region": "United States",
        "Status": "Critically Endangered",
        "Latitude": 35.5,
        "Longitude": -76.2,
        "Description": "One of the world's most endangered wolves.",
        "Keywords": "wolf wolves canine canines"
    },
    {
        "Animal": "Mountain Gorilla",
        "Region": "Rwanda / Uganda",
        "Status": "Endangered",
        "Latitude": -1.4,
        "Longitude": 29.6,
        "Description": "Lives in the forests of Central Africa.",
        "Keywords": "gorilla gorillas ape apes primate primates"
    },
    {
        "Animal": "Blue Whale",
        "Region": "Pacific Ocean",
        "Status": "Endangered",
        "Latitude": 36.6,
        "Longitude": -122.0,
        "Description": "The largest animal ever known.",
        "Keywords": "whale whales marine mammal mammals"
    },
    {
        "Animal": "Giant Panda",
        "Region": "China",
        "Status": "Vulnerable",
        "Latitude": 31.2,
        "Longitude": 103.5,
        "Description": "Famous for eating bamboo.",
        "Keywords": "panda pandas bear bears"
    },
    {
        "Animal": "Snow Leopard",
        "Region": "Himalayas",
        "Status": "Vulnerable",
        "Latitude": 34.0,
        "Longitude": 75.0,
        "Description": "Lives high in the mountains of Asia.",
        "Keywords": "leopard leopards snow leopard cat cats feline felines"
    },
    {
        "Animal": "Sea Otter",
        "Region": "North Pacific",
        "Status": "Endangered",
        "Latitude": 57.0,
        "Longitude": -152.0,
        "Description": "Helps keep kelp forests healthy.",
        "Keywords": "otter otters marine mammal mammals"
    },
    {
        "Animal": "Siberian Tiger",
        "Region": "Russia / China",
        "Status": "Endangered",
        "Latitude": 45.0,
        "Longitude": 134.0,
        "Description": "The largest wild cat, threatened by poaching and habitat loss.",
        "Keywords": "tiger tigers big cat feline"
    },
    {
        "Animal": "Chinese Giant Salamander",
        "Region": "China",
        "Status": "Critically Endangered",
        "Latitude": 31.0,
        "Longitude": 107.0,
        "Description": "The world's largest amphibian.",
        "Keywords": "salamander amphibian amphibians"
    },
    {
        "Animal": "Sumatran Orangutan",
        "Region": "Indonesia",
        "Status": "Critically Endangered",
        "Latitude": 3.3,
        "Longitude": 98.5,
        "Description": "Lives only on the island of Sumatra.",
        "Keywords": "orangutan ape primate"
    },
    {
        "Animal": "Sumatran Tiger",
        "Region": "Indonesia",
        "Status": "Critically Endangered",
        "Latitude": -1.5,
        "Longitude": 101.5,
        "Description": "The smallest surviving tiger subspecies.",
        "Keywords": "tiger big cat feline"
    },
    {
        "Animal": "Hawksbill Sea Turtle",
        "Region": "Pacific Ocean",
        "Status": "Critically Endangered",
        "Latitude": 10.0,
        "Longitude": -140.0,
        "Description": "A sea turtle known for its beautiful shell.",
        "Keywords": "turtle turtles sea turtle marine reptile"
    },
    {
        "Animal": "North Pacific Right Whale",
        "Region": "North Pacific",
        "Status": "Endangered",
        "Latitude": 55.0,
        "Longitude": -160.0,
        "Description": "One of the rarest whale species in the world.",
        "Keywords": "whale whales marine mammal"
    },
    {
        "Animal": "California Condor",
        "Region": "United States",
        "Status": "Critically Endangered",
        "Latitude": 36.5,
        "Longitude": -118.5,
        "Description": "North America's largest flying bird.",
        "Keywords": "condor bird birds vulture"
    },
    {
        "Animal": "Florida Panther",
        "Region": "United States",
        "Status": "Endangered",
        "Latitude": 26.2,
        "Longitude": -81.0,
        "Description": "A rare cougar found in southern Florida.",
        "Keywords": "panther cougar mountain lion cat feline"
    },
    {
        "Animal": "Bonobo",
        "Region": "Central Africa",
        "Status": "Endangered",
        "Latitude": -2.0,
        "Longitude": 23.0,
        "Description": "A great ape found only in the Democratic Republic of the Congo.",
        "Keywords": "bonobo ape primate chimpanzee"
    },
    {
        "Animal": "Okapi",
        "Region": "Central Africa",
        "Status": "Endangered",
        "Latitude": 2.5,
        "Longitude": 28.5,
        "Description": "A unique relative of the giraffe found in Congo.",
        "Keywords": "okapi giraffe mammal"
    },
    {
        "Animal": "Golden Monkey",
        "Region": "Rwanda / Uganda",
        "Status": "Endangered",
        "Latitude": -1.5,
        "Longitude": 29.6,
        "Description": "A colorful monkey living in the Virunga Mountains.",
        "Keywords": "monkey monkeys primate"
    },
    {
        "Animal": "Black Rhinoceros",
        "Region": "Rwanda",
        "Status": "Critically Endangered",
        "Latitude": -1.9,
        "Longitude": 30.1,
        "Description": "A rhinoceros threatened by illegal poaching.",
        "Keywords": "rhino rhinoceros"
    },
    {
        "Animal": "Snowy Owl",
        "Region": "North Pacific",
        "Status": "Vulnerable",
        "Latitude": 60.0,
        "Longitude": -150.0,
        "Description": "A large white owl adapted to cold climates.",
        "Keywords": "owl bird birds"
    },
    {
        "Animal": "Pallas's Cat",
        "Region": "Himalayas",
        "Status": "Near Threatened",
        "Latitude": 35.5,
        "Longitude": 78.0,
        "Description": "A small wild cat with thick fur for mountain climates.",
        "Keywords": "cat feline wildcat"
    },
    {
        "Animal": "Red Panda",
        "Region": "Himalayas",
        "Status": "Endangered",
        "Latitude": 27.8,
        "Longitude": 88.2,
        "Description": "A tree-dwelling mammal known for its reddish fur.",
        "Keywords": "red panda panda bear"
    },
    {
        "Animal": "Whale Shark",
        "Region": "Pacific Ocean",
        "Status": "Endangered",
        "Latitude": 15.0,
        "Longitude": -145.0,
        "Description": "The largest fish species in the world.",
        "Keywords": "shark sharks fish whale shark"
    },
    {
        "Animal": "Manta Ray",
        "Region": "Pacific Ocean",
        "Status": "Vulnerable",
        "Latitude": 12.0,
        "Longitude": -150.0,
        "Description": "A graceful giant ray threatened by fishing.",
        "Keywords": "ray manta ray fish"
    },
    {
        "Animal": "Guadalupe Fur Seal",
        "Region": "Gulf of California",
        "Status": "Endangered",
        "Latitude": 29.0,
        "Longitude": -113.0,
        "Description": "A marine mammal native to the eastern Pacific.",
        "Keywords": "seal seals marine mammal"
    },
    {
        "Animal": "Totoaba",
        "Region": "Gulf of California",
        "Status": "Critically Endangered",
        "Latitude": 30.8,
        "Longitude": -114.2,
        "Description": "A large fish threatened by illegal fishing.",
        "Keywords": "fish totoaba"
    },
    {
        "Animal": "Saiga Antelope",
        "Region": "Russia",
        "Status": "Critically Endangered",
        "Latitude": 49.5,
        "Longitude": 46.0,
        "Description": "A distinctive antelope known for its large, flexible nose. It faces threats from poaching and disease.",
        "Keywords": "saiga antelope antelopes mammal mammals"
    },
    {
        "Animal": "Chinese Pangolin",
        "Region": "China",
        "Status": "Critically Endangered",
        "Latitude": 27.5,
        "Longitude": 112.5,
        "Description": "A shy, nocturnal mammal covered in protective scales and threatened by illegal wildlife trade.",
        "Keywords": "pangolin pangolins mammal mammals scales"
    },
    {
        "Animal": "Arctic Wolf",
        "Region": "North Pacific",
        "Status": "Least Concern",
        "Latitude": 71.0,
        "Longitude": -156.0,
        "Description": "A white-furred subspecies of the gray wolf adapted to the Arctic tundra.",
        "Keywords": "wolf wolves arctic wolf canine canines"
    },
    {
        "Animal": "Mexican Gray Wolf",
        "Region": "United States",
        "Status": "Endangered",
        "Latitude": 33.5,
        "Longitude": -109.0,
        "Description": "The rarest gray wolf subspecies in North America, reintroduced to the southwestern United States.",
        "Keywords": "wolf wolves mexican gray wolf canine canines"
    },
    {
        "Animal": "Himalayan Wolf",
        "Region": "Himalayas",
        "Status": "Vulnerable",
        "Latitude": 34.5,
        "Longitude": 78.5,
        "Description": "An ancient lineage of wolf that lives at high elevations in the Himalayan Mountains.",
        "Keywords": "wolf wolves himalayan wolf canine canines"
    },
    {
        "Animal": "Eurasian Wolf",
        "Region": "Russia",
        "Status": "Least Concern",
        "Latitude": 58.0,
        "Longitude": 90.0,
        "Description": "A widespread gray wolf subspecies found throughout Europe and northern Asia.",
        "Keywords": "wolf wolves eurasian wolf gray wolf canine canines"
    },
    {
        "Animal": "Alexander Archipelago Wolf",
        "Region": "United States",
        "Status": "Near Threatened",
        "Latitude": 56.5,
        "Longitude": -133.0,
        "Description": "A coastal wolf that inhabits the forests and islands of southeastern Alaska.",
        "Keywords": "wolf wolves alexander archipelago wolf alaska canine canines"
    },
]

df = pd.DataFrame(animals)

# -----------------------------------
# Improved Search
# -----------------------------------
def normalize_search(text):
    text = text.lower().strip()
    terms = {text}

    if text.endswith("ies"):
        terms.add(text[:-3] + "y")

    if text.endswith("ves"):
        terms.add(text[:-3] + "f")
        terms.add(text[:-3] + "fe")

    if text.endswith("s"):
        terms.add(text[:-1])

    return list(terms)

if search.strip():
    search_terms = normalize_search(search)

    def matches(row):
        searchable = (
            f"{row['Animal']} "
            f"{row['Region']} "
            f"{row['Description']} "
            f"{row['Keywords']}"
        ).lower()

        return any(term in searchable for term in search_terms)

    filtered_df = df[df.apply(matches, axis=1)]
else:
    filtered_df = df

# -----------------------------------
# Display matching animals
# -----------------------------------
st.header("📚 Endangered Animal Library")

if filtered_df.empty:
    st.warning("No animals were found.")
else:
    st.dataframe(
        filtered_df[
            ["Animal", "Region", "Status", "Description"]
        ],
        use_container_width=True
    )

# -----------------------------------
# Show the map
# -----------------------------------
st.header("🗺️ Endangered Animal Map")

if not filtered_df.empty:

    view_state = pdk.ViewState(
        latitude=float(filtered_df["Latitude"].mean()),
        longitude=float(filtered_df["Longitude"].mean()),
        zoom=1,
        pitch=0,
    )

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=filtered_df,
        get_position='[Longitude, Latitude]',
        get_radius=250000,
        get_fill_color='[34, 139, 34, 180]',
        pickable=True,
    )

    tooltip = {
        "html": """
        <b>{Animal}</b><br/>
        Region: {Region}<br/>
        Status: {Status}<br/>
        {Description}
        """
    }

    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip=tooltip,
    )

    st.pydeck_chart(deck)

# -----------------------------------
# Footer
# -----------------------------------
st.markdown("---")
st.caption("Animal Advocators • Helping Wild Animals Worldwide 🌍")