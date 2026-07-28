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

# -----------------------------------
# Website title
# -----------------------------------
st.title("🌿 Animal Advocators")
st.subheader("Helping Wild Animals Around the World")

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

if st.button("Donate"):
    st.success(f"Thank you for donating ${donation}!")

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
        "Description": "One of the rarest big cats in the world."
    },
    {
        "Animal": "Javan Rhino",
        "Region": "Indonesia",
        "Status": "Critically Endangered",
        "Latitude": -6.75,
        "Longitude": 105.37,
        "Description": "Only a small population remains in Java."
    },
    {
        "Animal": "Vaquita",
        "Region": "Gulf of California",
        "Status": "Critically Endangered",
        "Latitude": 31.0,
        "Longitude": -114.0,
        "Description": "The world's rarest marine mammal."
    },
    {
        "Animal": "African Forest Elephant",
        "Region": "Central Africa",
        "Status": "Critically Endangered",
        "Latitude": 0.5,
        "Longitude": 21.0,
        "Description": "Threatened by habitat loss and poaching."
    },
    {
        "Animal": "Red Wolf",
        "Region": "United States",
        "Status": "Critically Endangered",
        "Latitude": 35.5,
        "Longitude": -76.2,
        "Description": "One of the world's most endangered wolves."
    },
    {
        "Animal": "Mountain Gorilla",
        "Region": "Rwanda / Uganda",
        "Status": "Endangered",
        "Latitude": -1.4,
        "Longitude": 29.6,
        "Description": "Lives in the forests of Central Africa."
    },
    {
        "Animal": "Blue Whale",
        "Region": "Pacific Ocean",
        "Status": "Endangered",
        "Latitude": 36.6,
        "Longitude": -122.0,
        "Description": "The largest animal ever known."
    },
    {
        "Animal": "Giant Panda",
        "Region": "China",
        "Status": "Vulnerable",
        "Latitude": 31.2,
        "Longitude": 103.5,
        "Description": "Famous for eating bamboo."
    },
    {
        "Animal": "Snow Leopard",
        "Region": "Himalayas",
        "Status": "Vulnerable",
        "Latitude": 34.0,
        "Longitude": 75.0,
        "Description": "Lives high in the mountains of Asia."
    },
    {
        "Animal": "Sea Otter",
        "Region": "North Pacific",
        "Status": "Endangered",
        "Latitude": 57.0,
        "Longitude": -152.0,
        "Description": "Helps keep kelp forests healthy."
    }
]

df = pd.DataFrame(animals)

# -----------------------------------
# Connect the search bar to the data
# -----------------------------------
if search.strip() != "":
    filtered_df = df[
        df["Animal"].str.contains(search, case=False) |
        df["Region"].str.contains(search, case=False)
    ]
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
# Show information cards
# -----------------------------------
st.header("🐾 Animal Information")

for _, row in filtered_df.iterrows():
    with st.expander(row["Animal"]):
        st.write("**Region:**", row["Region"])
        st.write("**Conservation Status:**", row["Status"])
        st.write("**About:**", row["Description"])

        if st.button(f"Donate to help {row['Animal']}", key=row["Animal"]):
            st.success(
                f"Thank you for supporting the {row['Animal']}!"
            )

# -----------------------------------
# Footer
# -----------------------------------
st.markdown("---")
st.caption("Animal Advocators • Helping Wild Animals Worldwide 🌎")