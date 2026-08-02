import pandas as pd
import pydeck as pdk
import streamlit as st

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="Animal Advocators",
    page_icon="🦁",
    layout="wide" if st.session_state.get("logged_in") else "centered",
)

# -----------------------------
# Initialize Session State
# -----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = "Guest"

if "payment_method" not in st.session_state:
    st.session_state.payment_method = None


# =============================================================================
# 🔑 LOGIN / SIGN UP / GUEST VIEW
# =============================================================================
if not st.session_state.logged_in:

    st.title("🌿 Animal Advocators")
    st.subheader("Voice the Voiceless")
    st.write("Please log in, create an account, or continue as a guest.")

    # Login / Sign Up Tabs
    login_tab, signup_tab = st.tabs(["🔑 Log In", "📝 Sign Up"])

    # LOG IN TAB
    with login_tab:
        login_username = st.text_input("Username", key="login_user")
        login_password = st.text_input(
            "Password", type="password", key="login_pass"
        )

        if st.button("Log In"):
            if login_username and login_password:
                st.session_state.logged_in = True
                st.session_state.username = login_username
                st.rerun()
            else:
                st.error("Please enter both username and password.")

    # SIGN UP TAB
    with signup_tab:
        username = st.text_input("Create Username", key="signup_user")
        email = st.text_input("Email Address", key="signup_email")
        phone = st.text_input("Phone Number (Optional)", key="signup_phone")
        password = st.text_input(
            "Create Password", type="password", key="signup_pass"
        )
        confirm = st.text_input(
            "Confirm Password", type="password", key="signup_confirm"
        )

        if st.button("Create Account"):
            if not username or not email or not password:
                st.error("Please complete all required fields.")
            elif password != confirm:
                st.error("Passwords do not match.")
            else:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()

    # GUEST OPTION
    st.markdown("---")
    st.write("Don't want to make an account?")

    if st.button("Continue as Guest"):
        st.session_state.logged_in = True
        st.session_state.username = "Guest"
        st.rerun()


# =============================================================================
# 🏠 HOME / MAIN APP VIEW (Shown after logging in or continuing as guest)
# =============================================================================
else:

    # -----------------------------
    # Shared Data Load
    # -----------------------------
    animals = [
        {
            "Animal": "Amur Leopard",
            "Region": "Russia / China",
            "Status": "Critically Endangered",
            "Latitude": 43.2,
            "Longitude": 131.9,
            "Description": "One of the rarest big cats in the world.",
            "Keywords": "leopard leopards cat cats feline felines big cat",
            "Image": "https://images.unsplash.com/photo-1534177616072-ef7dc120449d?w=400",
        },
        {
            "Animal": "Javan Rhino",
            "Region": "Indonesia",
            "Status": "Critically Endangered",
            "Latitude": -6.75,
            "Longitude": 105.37,
            "Description": "Only a small population remains in Java.",
            "Keywords": "rhino rhinos rhinoceros rhinoceroses",
            "Image": "https://images.unsplash.com/photo-1535591273668-578e31182c4f?w=400",
        },
        {
            "Animal": "Vaquita",
            "Region": "Gulf of California",
            "Status": "Critically Endangered",
            "Latitude": 31.0,
            "Longitude": -114.0,
            "Description": "The world's rarest marine mammal.",
            "Keywords": "vaquita porpoise porpoises marine mammal mammals",
            "Image": "https://images.unsplash.com/photo-1568430460464-02e3cb1845b3?w=400",
        },
        {
            "Animal": "African Forest Elephant",
            "Region": "Central Africa",
            "Status": "Critically Endangered",
            "Latitude": 0.5,
            "Longitude": 21.0,
            "Description": "Threatened by habitat loss and poaching.",
            "Keywords": "elephant elephants",
            "Image": "https://images.unsplash.com/photo-1557050543-4d5f4e07ef46?w=400",
        },
        {
            "Animal": "Red Wolf",
            "Region": "United States",
            "Status": "Critically Endangered",
            "Latitude": 35.5,
            "Longitude": -76.2,
            "Description": "One of the world's most endangered wolves.",
            "Keywords": "wolf wolves canine canines",
            "Image": "https://images.unsplash.com/photo-1564466809058-bf4114d55352?w=400",
        },
        {
            "Animal": "Mountain Gorilla",
            "Region": "Rwanda / Uganda",
            "Status": "Endangered",
            "Latitude": -1.4,
            "Longitude": 29.6,
            "Description": "Lives in the forests of Central Africa.",
            "Keywords": "gorilla gorillas ape apes primate primates",
            "Image": "https://images.unsplash.com/photo-1534567153574-2b12153a87f0?w=400",
        },
        {
            "Animal": "Blue Whale",
            "Region": "Pacific Ocean",
            "Status": "Endangered",
            "Latitude": 36.6,
            "Longitude": -122.0,
            "Description": "The largest animal ever known.",
            "Keywords": "whale whales marine mammal mammals",
            "Image": "https://images.unsplash.com/photo-1568430460464-02e3cb1845b3?w=400",
        },
        {
            "Animal": "Giant Panda",
            "Region": "China",
            "Status": "Vulnerable",
            "Latitude": 31.2,
            "Longitude": 103.5,
            "Description": "Famous for eating bamboo.",
            "Keywords": "panda pandas bear bears",
            "Image": "https://images.unsplash.com/photo-1564349683136-77e08dba1ef9?w=400",
        },
        {
            "Animal": "Snow Leopard",
            "Region": "Himalayas",
            "Status": "Vulnerable",
            "Latitude": 34.0,
            "Longitude": 75.0,
            "Description": "Lives high in the mountains of Asia.",
            "Keywords": (
                "leopard leopards snow leopard cat cats feline felines"
            ),
            "Image": "https://images.unsplash.com/photo-1546182990-dffeafbe841d?w=400",
        },
        {
            "Animal": "Sea Otter",
            "Region": "North Pacific",
            "Status": "Endangered",
            "Latitude": 57.0,
            "Longitude": -152.0,
            "Description": "Helps keep kelp forests healthy.",
            "Keywords": "otter otters marine mammal mammals",
            "Image": "https://images.unsplash.com/photo-1590420485404-f86d22b8abf8?w=400",
        },
        {
            "Animal": "Siberian Tiger",
            "Region": "Russia / China",
            "Status": "Endangered",
            "Latitude": 45.0,
            "Longitude": 134.0,
            "Description": (
                "The largest wild cat, threatened by poaching and habitat"
                " loss."
            ),
            "Keywords": "tiger tigers big cat feline",
            "Image": "https://images.unsplash.com/photo-1561731216-c3a4d99437d5?w=400",
        },
        {
            "Animal": "Chinese Giant Salamander",
            "Region": "China",
            "Status": "Critically Endangered",
            "Latitude": 31.0,
            "Longitude": 107.0,
            "Description": "The world's largest amphibian.",
            "Keywords": "salamander amphibian amphibians",
            "Image": "https://images.unsplash.com/photo-1550358864-518f202c02ba?w=400",
        },
        {
            "Animal": "Sumatran Orangutan",
            "Region": "Indonesia",
            "Status": "Critically Endangered",
            "Latitude": 3.3,
            "Longitude": 98.5,
            "Description": "Lives only on the island of Sumatra.",
            "Keywords": "orangutan ape primate",
            "Image": "https://images.unsplash.com/photo-1581009146145-b5ef050c2e1e?w=400",
        },
        {
            "Animal": "Sumatran Tiger",
            "Region": "Indonesia",
            "Status": "Critically Endangered",
            "Latitude": -1.5,
            "Longitude": 101.5,
            "Description": "The smallest surviving tiger subspecies.",
            "Keywords": "tiger big cat feline",
            "Image": "https://images.unsplash.com/photo-1561731216-c3a4d99437d5?w=400",
        },
        {
            "Animal": "Hawksbill Sea Turtle",
            "Region": "Pacific Ocean",
            "Status": "Critically Endangered",
            "Latitude": 10.0,
            "Longitude": -140.0,
            "Description": "A sea turtle known for its beautiful shell.",
            "Keywords": "turtle turtles sea turtle marine reptile",
            "Image": "https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=400",
        },
        {
            "Animal": "North Pacific Right Whale",
            "Region": "North Pacific",
            "Status": "Endangered",
            "Latitude": 55.0,
            "Longitude": -160.0,
            "Description": "One of the rarest whale species in the world.",
            "Keywords": "whale whales marine mammal",
            "Image": "https://images.unsplash.com/photo-1568430460464-02e3cb1845b3?w=400",
        },
        {
            "Animal": "California Condor",
            "Region": "United States",
            "Status": "Critically Endangered",
            "Latitude": 36.5,
            "Longitude": -118.5,
            "Description": "North America's largest flying bird.",
            "Keywords": "condor bird birds vulture",
            "Image": "https://images.unsplash.com/photo-1611095790444-1dfa35e37b52?w=400",
        },
        {
            "Animal": "Florida Panther",
            "Region": "United States",
            "Status": "Endangered",
            "Latitude": 26.2,
            "Longitude": -81.0,
            "Description": "A rare cougar found in southern Florida.",
            "Keywords": "panther cougar mountain lion cat feline",
            "Image": "https://images.unsplash.com/photo-1534177616072-ef7dc120449d?w=400",
        },
        {
            "Animal": "Bonobo",
            "Region": "Central Africa",
            "Status": "Endangered",
            "Latitude": -2.0,
            "Longitude": 23.0,
            "Description": (
                "A great ape found only in the Democratic Republic of the"
                " Congo."
            ),
            "Keywords": "bonobo ape primate chimpanzee",
            "Image": "https://images.unsplash.com/photo-1540573133985-778788177267?w=400",
        },
        {
            "Animal": "Okapi",
            "Region": "Central Africa",
            "Status": "Endangered",
            "Latitude": 2.5,
            "Longitude": 28.5,
            "Description": (
                "A unique relative of the giraffe found in Congo."
            ),
            "Keywords": "okapi giraffe mammal",
            "Image": "https://images.unsplash.com/photo-1534567153574-2b12153a87f0?w=400",
        },
        {
            "Animal": "Golden Monkey",
            "Region": "Rwanda / Uganda",
            "Status": "Endangered",
            "Latitude": -1.5,
            "Longitude": 29.6,
            "Description": (
                "A colorful monkey living in the Virunga Mountains."
            ),
            "Keywords": "monkey monkeys primate",
            "Image": "https://images.unsplash.com/photo-1540573133985-778788177267?w=400",
        },
        {
            "Animal": "Black Rhinoceros",
            "Region": "Rwanda",
            "Status": "Critically Endangered",
            "Latitude": -1.9,
            "Longitude": 30.1,
            "Description": "A rhinoceros threatened by illegal poaching.",
            "Keywords": "rhino rhinoceros",
            "Image": "https://images.unsplash.com/photo-1535591273668-578e31182c4f?w=400",
        },
        {
            "Animal": "Snowy Owl",
            "Region": "North Pacific",
            "Status": "Vulnerable",
            "Latitude": 60.0,
            "Longitude": -150.0,
            "Description": "A large white owl adapted to cold climates.",
            "Keywords": "owl bird birds",
            "Image": "https://images.unsplash.com/photo-1551085254-e96b210df58a?w=400",
        },
        {
            "Animal": "Pallas's Cat",
            "Region": "Himalayas",
            "Status": "Near Threatened",
            "Latitude": 35.5,
            "Longitude": 78.0,
            "Description": (
                "A small wild cat with thick fur for mountain climates."
            ),
            "Keywords": "cat feline wildcat",
            "Image": "https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?w=400",
        },
        {
            "Animal": "Red Panda",
            "Region": "Himalayas",
            "Status": "Endangered",
            "Latitude": 27.8,
            "Longitude": 88.2,
            "Description": (
                "A tree-dwelling mammal known for its reddish fur."
            ),
            "Keywords": "red panda panda bear",
            "Image": "https://images.unsplash.com/photo-1546182990-dffeafbe841d?w=400",
        },
        {
            "Animal": "Whale Shark",
            "Region": "Pacific Ocean",
            "Status": "Endangered",
            "Latitude": 15.0,
            "Longitude": -145.0,
            "Description": "The largest fish species in the world.",
            "Keywords": "shark sharks fish whale shark",
            "Image": "https://images.unsplash.com/photo-1560275619-4662e36fa65c?w=400",
        },
        {
            "Animal": "Manta Ray",
            "Region": "Pacific Ocean",
            "Status": "Vulnerable",
            "Latitude": 12.0,
            "Longitude": -150.0,
            "Description": "A graceful giant ray threatened by fishing.",
            "Keywords": "ray manta ray fish",
            "Image": "https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=400",
        },
        {
            "Animal": "Guadalupe Fur Seal",
            "Region": "Gulf of California",
            "Status": "Endangered",
            "Latitude": 29.0,
            "Longitude": -113.0,
            "Description": "A marine mammal native to the eastern Pacific.",
            "Keywords": "seal seals marine mammal",
            "Image": "https://images.unsplash.com/photo-1590420485404-f86d22b8abf8?w=400",
        },
        {
            "Animal": "Totoaba",
            "Region": "Gulf of California",
            "Status": "Critically Endangered",
            "Latitude": 30.8,
            "Longitude": -114.2,
            "Description": "A large fish threatened by illegal fishing.",
            "Keywords": "fish totoaba",
            "Image": "https://images.unsplash.com/photo-1522069169874-c58ec4b76be5?w=400",
        },
        {
            "Animal": "Saiga Antelope",
            "Region": "Russia",
            "Status": "Critically Endangered",
            "Latitude": 49.5,
            "Longitude": 46.0,
            "Description": (
                "A distinctive antelope known for its large, flexible nose."
                " It faces threats from poaching and disease."
            ),
            "Keywords": "saiga antelope antelopes mammal mammals",
            "Image": "https://images.unsplash.com/photo-1535591273668-578e31182c4f?w=400",
        },
        {
            "Animal": "Chinese Pangolin",
            "Region": "China",
            "Status": "Critically Endangered",
            "Latitude": 27.5,
            "Longitude": 112.5,
            "Description": (
                "A shy, nocturnal mammal covered in protective scales and"
                " threatened by illegal wildlife trade."
            ),
            "Keywords": "pangolin pangolins mammal mammals scales",
            "Image": "https://images.unsplash.com/photo-1550358864-518f202c02ba?w=400",
        },
        {
            "Animal": "Arctic Wolf",
            "Region": "North Pacific",
            "Status": "Least Concern",
            "Latitude": 71.0,
            "Longitude": -156.0,
            "Description": (
                "A white-furred subspecies of the gray wolf adapted to the"
                " Arctic tundra."
            ),
            "Keywords": "wolf wolves arctic wolf canine canines",
            "Image": "https://images.unsplash.com/photo-1564466809058-bf4114d55352?w=400",
        },
        {
            "Animal": "Mexican Gray Wolf",
            "Region": "United States",
            "Status": "Endangered",
            "Latitude": 33.5,
            "Longitude": -109.0,
            "Description": (
                "The rarest gray wolf subspecies in North America,"
                " reintroduced to the southwestern United States."
            ),
            "Keywords": "wolf wolves mexican gray wolf canine canines",
            "Image": "https://images.unsplash.com/photo-1564466809058-bf4114d55352?w=400",
        },
        {
            "Animal": "Himalayan Wolf",
            "Region": "Himalayas",
            "Status": "Vulnerable",
            "Latitude": 34.5,
            "Longitude": 78.5,
            "Description": (
                "An ancient lineage of wolf that lives at high elevations"
                " in the Himalayan Mountains."
            ),
            "Keywords": "wolf wolves himalayan wolf canine canines",
            "Image": "https://images.unsplash.com/photo-1564466809058-bf4114d55352?w=400",
        },
        {
            "Animal": "Eurasian Wolf",
            "Region": "Russia",
            "Status": "Least Concern",
            "Latitude": 58.0,
            "Longitude": 90.0,
            "Description": (
                "A widespread gray wolf subspecies found throughout Europe"
                " and northern Asia."
            ),
            "Keywords": "wolf wolves eurasian wolf gray wolf canine canines",
            "Image": "https://images.unsplash.com/photo-1564466809058-bf4114d55352?w=400",
        },
        {
            "Animal": "Alexander Archipelago Wolf",
            "Region": "United States",
            "Status": "Near Threatened",
            "Latitude": 56.5,
            "Longitude": -133.0,
            "Description": (
                "A coastal wolf that inhabits the forests and islands of"
                " southeastern Alaska."
            ),
            "Keywords": (
                "wolf wolves alexander archipelago wolf alaska canine"
                " canines"
            ),
            "Image": "https://images.unsplash.com/photo-1564466809058-bf4114d55352?w=400",
        },
    ]

    df = pd.DataFrame(animals)

    # Search Logic Helper
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

    # -----------------------------
    # Sidebar Navigation & Logout
    # -----------------------------
    st.sidebar.title("☰ Navigation")

    page = st.sidebar.radio(
        "Go to",
        [
            "🏠 Home",
            "🌎 Overview",
            "📚 Endangered Animal Library",
        ],
    )

    st.sidebar.markdown("---")
    st.sidebar.write(f"Logged in as: **{st.session_state.username}**")

    if st.sidebar.button("🚪 Log Out"):
        st.session_state.logged_in = False
        st.session_state.username = "Guest"
        st.session_state.payment_method = None
        st.rerun()

    # -----------------------------
    # PAGE 1: HOME PAGE
    # -----------------------------
    if page == "🏠 Home":
        st.title("🌿 Animal Advocators")
        st.subheader("Voice the Voiceless")

        st.success(f"Welcome, {st.session_state.username}!")

        st.write(
            """
        Animal Advocators is dedicated to protecting endangered wildlife around the world.

        Use the navigation menu on the left to explore endangered species, 
        learn about conservation, and support wildlife through donations.
        """
        )

        st.markdown("---")

        # Search bar
        search = st.text_input("🔎 Search for an endangered animal or region:")

        if search.strip():
            search_terms = normalize_search(search)

            def matches(row):
                searchable = (
                    f"{row['Animal']} {row['Region']} {row['Description']}"
                    f" {row['Keywords']}"
                ).lower()
                return any(term in searchable for term in search_terms)

            filtered_df = df[df.apply(matches, axis=1)]
        else:
            filtered_df = df

        if not filtered_df.empty and search.strip():
            st.dataframe(
                filtered_df[["Animal", "Region", "Status", "Description"]],
                use_container_width=True,
            )
        elif filtered_df.empty and search.strip():
            st.warning("No animals were found.")

        # Map Visualization
        st.header("🗺️ Endangered Animal Map")

        map_data = filtered_df if search.strip() else df

        if not map_data.empty:
            view_state = pdk.ViewState(
                latitude=float(map_data["Latitude"].mean()),
                longitude=float(map_data["Longitude"].mean()),
                zoom=1,
                pitch=0,
            )

            layer = pdk.Layer(
                "ScatterplotLayer",
                data=map_data,
                get_position="[Longitude, Latitude]",
                get_radius=250000,
                get_fill_color="[34, 139, 34, 180]",
                pickable=True,
            )

            tooltip = {
                "html": """
                <div style="font-family: sans-serif; max-width: 200px;">
                    <b style="font-size: 14px;">{Animal}</b><br/>
                    <img src="{Image}" style="width: 160px; height: 110px; object-fit: cover; border-radius: 6px; margin: 6px 0;"/><br/>
                    <b>Region:</b> {Region}<br/>
                    <b>Status:</b> {Status}<br/>
                    <span style="font-size: 11px; color: #ddd;">{Description}</span>
                </div>
                """
            }

            deck = pdk.Deck(
                layers=[layer],
                initial_view_state=view_state,
                tooltip=tooltip,
            )

            st.pydeck_chart(deck)

        # Donation Section
        st.markdown("---")
        st.header("💚 Donation")

        donation = st.slider(
            "Choose a donation amount ($)",
            min_value=5,
            max_value=500,
            value=25,
            step=5,
        )

        st.subheader("Choose a Payment Method")

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

        col5, col6, _ = st.columns(3)

        with col5:
            if st.button("🎁 Visa Gift Card", use_container_width=True):
                st.session_state.payment_method = "Visa Gift Card"
        with col6:
            if st.button("🎁 Mastercard Gift Card", use_container_width=True):
                st.session_state.payment_method = "Mastercard Gift Card"

        # Payment Form
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
                            f"🎉 Thank you for donating ${donation} using"
                            f" {st.session_state.payment_method}!"
                        )
                    else:
                        st.error("Please enter your gift card code.")
                else:
                    if card_number and card_name and expiry and cvv:
                        st.success(
                            f"🎉 Thank you for donating ${donation} using"
                            f" {st.session_state.payment_method}!"
                        )
                    else:
                        st.error("Please complete all payment information.")

    # -----------------------------
    # PAGE 2: OVERVIEW
    # -----------------------------
    elif page == "🌎 Overview":
        st.title("🌎 Overview")

        st.markdown(
            """
        ### Our Mission

        Animal Advocators raises awareness for endangered animals and supports conservation efforts.

        ### What You Can Do

        - 🔍 Search for endangered animals
        - 📚 Learn about endangered species
        - 🗺️ View animals on an interactive map
        - 💚 Donate to conservation projects

        Every donation helps protect wildlife and preserve habitats.
        """
        )

    # -----------------------------
    # PAGE 3: ENDANGERED ANIMAL LIBRARY
    # -----------------------------
    elif page == "📚 Endangered Animal Library":

        st.header("📚 Endangered Animal Library")

        st.write(
            "Browse all animals in our library below to read their descriptions"
            " and status."
        )

        st.dataframe(
            df[["Animal", "Region", "Status", "Description"]],
            use_container_width=True,
        )

    # -----------------------------
    # Footer
    # -----------------------------
    st.markdown("---")
    st.caption("Animal Advocators • Helping Wild Animals Worldwide 🌍")