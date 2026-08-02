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
# Custom CSS: Moving Blue and Green Bottom Background Banner
# -----------------------------
st.markdown(
    """
    <style>
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Style for the bottom animated gradient banner */
    .bottom-background-banner {
        width: 100%;
        height: 120px;
        margin-top: 30px;
        border-radius: 12px;
        background: linear-gradient(-45deg, #0f2027, #203a43, #2c5364, #11998e, #1a5b4c);
        background-size: 400% 400%;
        animation: gradientShift 10s ease infinite;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }

    .bottom-background-banner p {
        color: white;
        font-weight: 500;
        font-size: 1rem;
        margin: 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# Helper function to display the bottom banner
def show_bottom_banner():
    st.markdown(
        """
        <div class="bottom-background-banner">
            <p>Animal Advocators • Helping Wild Animals Worldwide 🌍</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------
# Initialize Session State
# -----------------------------
if "users_db" not in st.session_state:
    st.session_state.users_db = {}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = "Guest"

if "phone" not in st.session_state:
    st.session_state.phone = ""

if "description" not in st.session_state:
    st.session_state.description = "Passionate about protecting wildlife!"

DEFAULT_AVATAR = "https://cdn-icons-png.flaticon.com/512/149/149071.png"

if "profile_pic" not in st.session_state:
    st.session_state.profile_pic = None

if "payment_method" not in st.session_state:
    st.session_state.payment_method = None

if "view_profile" not in st.session_state:
    st.session_state.view_profile = False

# Donation goal trackers
if "total_donated" not in st.session_state:
    st.session_state.total_donated = 0.0

if "claimed_rewards" not in st.session_state:
    st.session_state.claimed_rewards = set()


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
            user_entry = st.session_state.users_db.get(login_username)

            if user_entry and user_entry["password"] == login_password:
                st.session_state.logged_in = True
                st.session_state.username = login_username
                st.session_state.phone = user_entry.get("phone", "")
                st.session_state.description = user_entry.get(
                    "description", "Passionate about protecting wildlife!"
                )
                st.rerun()
            else:
                st.error("Invalid username or password.")

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
            elif username in st.session_state.users_db:
                st.error("Username already exists.")
            elif password != confirm:
                st.error("Passwords do not match.")
            else:
                st.session_state.users_db[username] = {
                    "password": password,
                    "email": email,
                    "phone": phone,
                    "description": "Passionate about protecting wildlife!",
                }
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.phone = phone
                st.rerun()

    # GUEST OPTION
    st.markdown("---")
    st.write("Don't want to make an account?")

    if st.button("Continue as Guest"):
        st.session_state.logged_in = True
        st.session_state.username = "Guest"
        st.rerun()

    show_bottom_banner()


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
        },
        {
            "Animal": "Javan Rhino",
            "Region": "Indonesia",
            "Status": "Critically Endangered",
            "Latitude": -6.75,
            "Longitude": 105.37,
            "Description": "Only a small population remains in Java.",
            "Keywords": "rhino rhinos rhinoceros rhinoceroses",
        },
        {
            "Animal": "Vaquita",
            "Region": "Gulf of California",
            "Status": "Critically Endangered",
            "Latitude": 31.0,
            "Longitude": -114.0,
            "Description": "The world's rarest marine mammal.",
            "Keywords": "vaquita porpoise porpoises marine mammal mammals",
        },
        {
            "Animal": "African Forest Elephant",
            "Region": "Central Africa",
            "Status": "Critically Endangered",
            "Latitude": 0.5,
            "Longitude": 21.0,
            "Description": "Threatened by habitat loss and poaching.",
            "Keywords": "elephant elephants",
        },
        {
            "Animal": "Red Wolf",
            "Region": "United States",
            "Status": "Critically Endangered",
            "Latitude": 35.5,
            "Longitude": -76.2,
            "Description": "One of the world's most endangered wolves.",
            "Keywords": "wolf wolves canine canines",
        },
        {
            "Animal": "Mountain Gorilla",
            "Region": "Rwanda / Uganda",
            "Status": "Endangered",
            "Latitude": -1.4,
            "Longitude": 29.6,
            "Description": "Lives in the forests of Central Africa.",
            "Keywords": "gorilla gorillas ape apes primate primates",
        },
        {
            "Animal": "Blue Whale",
            "Region": "Pacific Ocean",
            "Status": "Endangered",
            "Latitude": 36.6,
            "Longitude": -122.0,
            "Description": "The largest animal ever known.",
            "Keywords": "whale whales marine mammal mammals",
        },
        {
            "Animal": "Giant Panda",
            "Region": "China",
            "Status": "Vulnerable",
            "Latitude": 31.2,
            "Longitude": 103.5,
            "Description": "Famous for eating bamboo.",
            "Keywords": "panda pandas bear bears",
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
        },
        {
            "Animal": "Sea Otter",
            "Region": "North Pacific",
            "Status": "Endangered",
            "Latitude": 57.0,
            "Longitude": -152.0,
            "Description": "Helps keep kelp forests healthy.",
            "Keywords": "otter otters marine mammal mammals",
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
        },
        {
            "Animal": "Chinese Giant Salamander",
            "Region": "China",
            "Status": "Critically Endangered",
            "Latitude": 31.0,
            "Longitude": 107.0,
            "Description": "The world's largest amphibian.",
            "Keywords": "salamander amphibian amphibians",
        },
        {
            "Animal": "Sumatran Orangutan",
            "Region": "Indonesia",
            "Status": "Critically Endangered",
            "Latitude": 3.3,
            "Longitude": 98.5,
            "Description": "Lives only on the island of Sumatra.",
            "Keywords": "orangutan ape primate",
        },
        {
            "Animal": "Sumatran Tiger",
            "Region": "Indonesia",
            "Status": "Critically Endangered",
            "Latitude": -1.5,
            "Longitude": 101.5,
            "Description": "The smallest surviving tiger subspecies.",
            "Keywords": "tiger big cat feline",
        },
        {
            "Animal": "Hawksbill Sea Turtle",
            "Region": "Pacific Ocean",
            "Status": "Critically Endangered",
            "Latitude": 10.0,
            "Longitude": -140.0,
            "Description": "A sea turtle known for its beautiful shell.",
            "Keywords": "turtle turtles sea turtle marine reptile",
        },
        {
            "Animal": "North Pacific Right Whale",
            "Region": "North Pacific",
            "Status": "Endangered",
            "Latitude": 55.0,
            "Longitude": -160.0,
            "Description": "One of the rarest whale species in the world.",
            "Keywords": "whale whales marine mammal",
        },
        {
            "Animal": "California Condor",
            "Region": "United States",
            "Status": "Critically Endangered",
            "Latitude": 36.5,
            "Longitude": -118.5,
            "Description": "North America's largest flying bird.",
            "Keywords": "condor bird birds vulture",
        },
        {
            "Animal": "Florida Panther",
            "Region": "United States",
            "Status": "Endangered",
            "Latitude": 26.2,
            "Longitude": -81.0,
            "Description": "A rare cougar found in southern Florida.",
            "Keywords": "panther cougar mountain lion cat feline",
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
        },
        {
            "Animal": "Black Rhinoceros",
            "Region": "Rwanda",
            "Status": "Critically Endangered",
            "Latitude": -1.9,
            "Longitude": 30.1,
            "Description": "A rhinoceros threatened by illegal poaching.",
            "Keywords": "rhino rhinoceros",
        },
        {
            "Animal": "Snowy Owl",
            "Region": "North Pacific",
            "Status": "Vulnerable",
            "Latitude": 60.0,
            "Longitude": -150.0,
            "Description": "A large white owl adapted to cold climates.",
            "Keywords": "owl bird birds",
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
        },
        {
            "Animal": "Whale Shark",
            "Region": "Pacific Ocean",
            "Status": "Endangered",
            "Latitude": 15.0,
            "Longitude": -145.0,
            "Description": "The largest fish species in the world.",
            "Keywords": "shark sharks fish whale shark",
        },
        {
            "Animal": "Manta Ray",
            "Region": "Pacific Ocean",
            "Status": "Vulnerable",
            "Latitude": 12.0,
            "Longitude": -150.0,
            "Description": "A graceful giant ray threatened by fishing.",
            "Keywords": "ray manta ray fish",
        },
        {
            "Animal": "Guadalupe Fur Seal",
            "Region": "Gulf of California",
            "Status": "Endangered",
            "Latitude": 29.0,
            "Longitude": -113.0,
            "Description": "A marine mammal native to the eastern Pacific.",
            "Keywords": "seal seals marine mammal",
        },
        {
            "Animal": "Totoaba",
            "Region": "Gulf of California",
            "Status": "Critically Endangered",
            "Latitude": 30.8,
            "Longitude": -114.2,
            "Description": "A large fish threatened by illegal fishing.",
            "Keywords": "fish totoaba",
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
        },
        {
            "Animal": "Kakapo",
            "Region": "New Zealand",
            "Status": "Critically Endangered",
            "Latitude": -45.0,
            "Longitude": 167.5,
            "Description": "A rare, flightless, nocturnal parrot native to New Zealand.",
            "Keywords": "kakapo parrot bird flightless parrot new zealand",
        },
        {
            "Animal": "Galapagos Giant Tortoise",
            "Region": "Ecuador",
            "Status": "Vulnerable",
            "Latitude": -0.9,
            "Longitude": -90.9,
            "Description": "The largest living species of tortoise, inhabiting the Galapagos Islands.",
            "Keywords": "tortoise giant tortoise reptile galapagos ecuador",
        },
        {
            "Animal": "Iberian Lynx",
            "Region": "Spain / Portugal",
            "Status": "Endangered",
            "Latitude": 37.5,
            "Longitude": -6.5,
            "Description": "A wild cat endemic to the Iberian Peninsula in southwestern Europe.",
            "Keywords": "lynx iberian lynx cat wildcat feline spain portugal",
        },
        {
            "Animal": "Cheetah",
            "Region": "Sub-Saharan Africa",
            "Status": "Vulnerable",
            "Latitude": -2.0,
            "Longitude": 34.5,
            "Description": "The fastest land animal on Earth, threatened by habitat loss.",
            "Keywords": "cheetah cat big cat feline africa fast mammal",
        },
        {
            "Animal": "Monarch Butterfly",
            "Region": "North America",
            "Status": "Endangered",
            "Latitude": 19.6,
            "Longitude": -100.3,
            "Description": "Famous for its long annual migration across North America.",
            "Keywords": "monarch butterfly insect migration pollinator",
        },
        {
            "Animal": "African Wild Dog",
            "Region": "Sub-Saharan Africa",
            "Status": "Endangered",
            "Latitude": -18.0,
            "Longitude": 25.0,
            "Description": "Known for its mottled fur and highly social pack behaviors.",
            "Keywords": "wild dog african wild dog canine hunting dog mammal",
        },
        {
            "Animal": "Komodo Dragon",
            "Region": "Indonesia",
            "Status": "Endangered",
            "Latitude": -8.5,
            "Longitude": 119.5,
            "Description": "The largest living species of lizard, native to Indonesian islands.",
            "Keywords": "komodo dragon lizard reptile giant lizard indonesia",
        },
        {
            "Animal": "Axolotl",
            "Region": "Mexico",
            "Status": "Critically Endangered",
            "Latitude": 19.2,
            "Longitude": -99.1,
            "Description": "A unique walking salamander native to Lake Xochimilco.",
            "Keywords": "axolotl salamander amphibian Mexico xochimilco",
        },
        {
            "Animal": "Tasmanian Devil",
            "Region": "Australia",
            "Status": "Endangered",
            "Latitude": -42.0,
            "Longitude": 146.5,
            "Description": "The largest carnivorous marsupial, native to the island of Tasmania.",
            "Keywords": "tasmanian devil marsupial australia tasmania mammal",
        },
        {
            "Animal": "Gharial",
            "Region": "India / Nepal",
            "Status": "Critically Endangered",
            "Latitude": 27.5,
            "Longitude": 81.2,
            "Description": "A fish-eating crocodilian with a long, narrow snout.",
            "Keywords": "gharial crocodile crocodilian reptile india nepal",
        },
        {
            "Animal": "Sloth Bear",
            "Region": "India / Sri Lanka",
            "Status": "Vulnerable",
            "Latitude": 20.5,
            "Longitude": 78.9,
            "Description": "A shaggy-coated bear adapted for feeding on insects like termites.",
            "Keywords": "sloth bear bear mammal india sri lanka",
        },
        {
            "Animal": "Polar Bear",
            "Region": "North Pacific",
            "Status": "Vulnerable",
            "Latitude": 75.0,
            "Longitude": -100.0,
            "Description": "The world's largest land carnivore, threatened by melting sea ice.",
            "Keywords": "polar bear bear arctic marine mammal ice",
        },
        {
            "Animal": "Tree Kangaroo",
            "Region": "Papua New Guinea",
            "Status": "Endangered",
            "Latitude": -6.0,
            "Longitude": 143.5,
            "Description": "A tree-dwelling marsupial adapted for climbing in tropical rainforests.",
            "Keywords": "tree kangaroo kangaroo marsupial papua new guinea",
        },
        {
            "Animal": "Amazon River Dolphin",
            "Region": "South America",
            "Status": "Endangered",
            "Latitude": -3.4,
            "Longitude": -62.2,
            "Description": "A pink freshwater dolphin native to the rivers of the Amazon basin.",
            "Keywords": "amazon river dolphin pink dolphin river dolphin freshwater marine mammal",
        },
        {
            "Animal": "Philippine Eagle",
            "Region": "Philippines",
            "Status": "Critically Endangered",
            "Latitude": 7.1,
            "Longitude": 125.6,
            "Description": "One of the world's largest and most powerful forest eagles.",
            "Keywords": "philippine eagle eagle bird bird of prey raptor philippines",
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
    # Sidebar Navigation Header & Profile Pic
    # -----------------------------
    st.sidebar.title("☰ Navigation")

    # Display Profile Picture Icon at Top Left
    pic_to_show = (
        st.session_state.profile_pic
        if st.session_state.profile_pic is not None
        else DEFAULT_AVATAR
    )
    st.sidebar.image(pic_to_show, width=65)

    if st.sidebar.button("Edit Profile", use_container_width=True):
        st.session_state.view_profile = True
        st.rerun()

    st.sidebar.markdown("---")

    page = st.sidebar.radio(
        "Go to",
        [
            "🏠 Home",
            "🌎 Overview",
            "📚 Endangered Animal Library",
            "🤝 Other Ways To Help",
            "⚙️ Settings",
        ],
    )

    st.sidebar.markdown("---")

    if st.sidebar.button("🚪 Log Out", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = "Guest"
        st.session_state.phone = ""
        st.session_state.description = "Passionate about protecting wildlife!"
        st.session_state.profile_pic = None
        st.session_state.payment_method = None
        st.session_state.view_profile = False
        st.rerun()

    # -----------------------------
    # PAGE: PROFILE MANAGEMENT (Accessed via Profile Icon Button)
    # -----------------------------
    if st.session_state.view_profile:
        st.title("👤 Profile & Account Settings")

        if st.button("⬅️ Back to App"):
            st.session_state.view_profile = False
            st.rerun()

        st.markdown("---")

        col1, col2 = st.columns([1, 2])

        with col1:
            st.subheader("Profile Photo")
            st.image(pic_to_show, width=150)

            uploaded_file = st.file_uploader(
                "Change photo", type=["jpg", "png", "jpeg"]
            )
            if uploaded_file is not None:
                st.session_state.profile_pic = uploaded_file
                st.success("Photo updated!")

        with col2:
            st.subheader("Account Details")
            new_username = st.text_input(
                "Username", value=st.session_state.username
            )
            new_phone = st.text_input(
                "Phone Number (Optional)", value=st.session_state.phone
            )
            new_description = st.text_area(
                "Profile Description", value=st.session_state.description
            )

            if st.button("Save Profile Changes"):
                st.session_state.username = new_username
                st.session_state.phone = new_phone
                st.session_state.description = new_description
                st.success("Profile changes saved!")

        st.markdown("---")
        st.subheader("🔁 Account Options")
        if st.button("Switch Account"):
            st.session_state.logged_in = False
            st.session_state.view_profile = False
            st.rerun()

        show_bottom_banner()

    # -----------------------------
    # PAGE 1: HOME PAGE
    # -----------------------------
    elif page == "🏠 Home":
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

        # Donation Section
        st.markdown("---")
        st.header("💚 Donation Tracker & Rewards")

        # Goal Progress Circle / Bar & Tracker (Placed ON TOP of Donation Bar)
        max_goal = 10000.0
        current_total = st.session_state.total_donated
        progress_pct = min(1.0, current_total / max_goal)

        col_circle, col_stats = st.columns([1, 2])

        with col_circle:
            # Custom CSS SVG Animated Progress Circle
            circle_pct = progress_pct * 100
            dash_array = f"{circle_pct}, 100"
            st.markdown(
                f"""
                <div style="display:flex; flex-direction:column; align-items:center; justify-content:center;">
                    <svg viewBox="0 0 36 36" style="width:140px; height:140px;">
                        <path stroke="#e6e6e6" stroke-width="3.8" fill="none"
                            d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                        <path stroke="#11998e" stroke-width="3.8" stroke-dasharray="{dash_array}" stroke-linecap="round" fill="none"
                            d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                        <text x="18" y="20.35" font-size="7" font-weight="bold" text-anchor="middle" fill="#11998e">{int(circle_pct)}%</text>
                    </svg>
                    <p style="margin-top:8px; font-weight:600; color:#11998e;">Goal Progress</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_stats:
            st.subheader(f"Total Raised: **${current_total:,.2f}** / **${max_goal:,.2f}**")
            st.progress(progress_pct)

            # Define Rewards Thresholds
            rewards = [
                {"name": "🔑 Free Keychain", "goal": 100.0, "key": "keychain"},
                {"name": "👕 Free T-Shirt", "goal": 1000.0, "key": "tshirt"},
                {"name": "🏷️ Merch Discount", "goal": 5000.0, "key": "discount"},
                {"name": "✈️ Visit to Help Out", "goal": 10000.0, "key": "visit"},
            ]

            st.markdown("### 🏆 Reward Unlocks:")
            for r in rewards:
                is_unlocked = current_total >= r["goal"]
                is_claimed = r["key"] in st.session_state.claimed_rewards

                if is_claimed:
                    st.success(f"✅ **{r['name']}** (${r['goal']:,.0f}) - **Claimed!**")
                elif is_unlocked:
                    st.info(f"🎉 **{r['name']}** (${r['goal']:,.0f}) - **Unlocked!**")
                    if st.button(f"🎁 Claim {r['name']}", key=f"claim_{r['key']}"):
                        st.session_state.claimed_rewards.add(r["key"])
                        st.balloons()
                        st.toast(f"🎉 You claimed your {r['name']}!")
                        st.rerun()
                else:
                    st.write(f"🔒 **{r['name']}** (${r['goal']:,.0f}) - *(Donate ${r['goal'] - current_total:,.0f} more)*")

        st.markdown("---")

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
                card_number = st.text_input("Card Number", type="password")
                card_name = st.text_input("Name on Card")
                expiry = st.text_input("Expiration Date (MM/YY)")
                cvv = st.text_input("CVV", type="password")

            if st.button("Complete Donation"):
                if "Gift Card" in st.session_state.payment_method:
                    if gift_code:
                        st.session_state.total_donated += float(donation)
                        st.balloons()
                        st.success(
                            f"🎉 Thank you for donating ${donation} using"
                            f" {st.session_state.payment_method}!"
                        )
                        st.rerun()
                    else:
                        st.error("Please enter your gift card code.")
                else:
                    if card_number and card_name and expiry and cvv:
                        st.session_state.total_donated += float(donation)
                        st.balloons()
                        st.success(
                            f"🎉 Thank you for donating ${donation} using"
                            f" {st.session_state.payment_method}!"
                        )
                        st.rerun()
                    else:
                        st.error("Please complete all payment information.")

        show_bottom_banner()

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

        show_bottom_banner()

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

        show_bottom_banner()

    # -----------------------------
    # PAGE 4: OTHER WAYS TO HELP
    # -----------------------------
    elif page == "🤝 Other Ways To Help":
        st.title("🤝 Other Ways To Help")
        st.write(
            "Donations aren't the only way to make a big difference! Here are"
            " impactful ways you can help protect endangered animals without"
            " spending money:"
        )

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(
                """
            ### 📢 Spread Awareness
            * **Share on Social Media:** Educate friends and family by sharing facts about endangered species.
            * **Advocate:** Speak up for local wildlife protections and conservation initiatives.
            * **Support Sustainable Brands:** Purchase eco-friendly products that don't harm habitats.
            """
            )

            st.markdown(
                """
            ### 🙋‍♂️ Volunteer Your Time
            * **Local Animal Shelters:** Offer a helping hand at community wildlife rescues or shelters.
            * **Cleanup Events:** Participate in local beach, park, or river cleanups to protect habitats.
            """
            )

        with col2:
            st.markdown(
                """
            ### ♻️ Eco-Friendly Habits
            * **Reduce, Reuse, Recycle:** Minimize single-use plastics that end up in marine environments.
            * **Plant Native Species:** Grow local flora to build supportive habitats for local pollinators and birds.
            * **Reduce Carbon Footprint:** Save energy at home to help slow down global climate change.
            """
            )

            st.markdown(
                """
            ### 📬 Get Involved
            Have an idea or want to collaborate on a conservation project? Reach out to us at **support@animaladvocators.org**!
            """
            )

        show_bottom_banner()

    # -----------------------------
    # PAGE 5: SETTINGS
    # -----------------------------
    elif page == "⚙️ Settings":
        st.title("⚙️ Settings")

        settings_tab1, settings_tab2, settings_tab3 = st.tabs(
            ["📊 Activity", "💬 Feedback", "🐞 Help & Bug Report"]
        )

        # TAB 1: ACTIVITY
        with settings_tab1:
            st.subheader("📊 Your Activity Log")
            st.write(f"**Logged in as:** {st.session_state.username}")
            st.write("**Account Status:** Active")
            st.markdown("---")
            st.write("Recent Actions:")
            st.write("- Logged into Animal Advocators")
            st.write("- Explored Endangered Animal Library")

        # TAB 2: FEEDBACK
        with settings_tab2:
            st.subheader("💬 Send Us Feedback")
            st.write("We'd love to hear how we can improve Animal Advocators!")
            feedback_type = st.selectbox(
                "Feedback Topic",
                ["General Feedback", "Feature Request", "Content Suggestion", "Other"],
            )
            feedback_text = st.text_area("Your Feedback")

            if st.button("Submit Feedback"):
                if feedback_text.strip():
                    st.success("Thank you for your feedback! We appreciate your support.")
                else:
                    st.warning("Please enter your feedback before submitting.")

        # TAB 3: HELP & BUG REPORT
        with settings_tab3:
            st.subheader("🐞 Help & Report Bugs")
            st.write("Encountered an issue or glitch on the site? Let us know!")

            bug_title = st.text_input("Bug Summary")
            bug_description = st.text_area("Describe the issue in detail")

            if st.button("Submit Bug Report"):
                if bug_title.strip() and bug_description.strip():
                    st.success("Bug report submitted successfully! Our team will look into it.")
                else:
                    st.warning("Please fill in both the summary and description.")

        show_bottom_banner()