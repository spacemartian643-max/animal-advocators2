import pandas as pd
import pydeck as pdk
import streamlit as st

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="Animal Advocators 🌿",
    page_icon="🦁",
    layout="wide" if st.session_state.get("logged_in") else "centered",
    initial_sidebar_state="expanded",
)

# -----------------------------
# Global CSS & Auto Scroll-to-Top JS
# -----------------------------
st.markdown(
    """
    <style>
    /* Apply Times New Roman across all Streamlit elements */
    html, body, [class*="css"], [class*="st-"], div, span, p, h1, h2, h3, h4, h5, h6, button, input, textarea, label {
        font-family: 'Times New Roman', Times, serif !important;
    }

    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

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

    <script>
        window.scrollTo(0, 0);
    </script>
    """,
    unsafe_allow_html=True,
)


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

if "view_profile" not in st.session_state:
    st.session_state.view_profile = False

if "total_donated" not in st.session_state:
    st.session_state.total_donated = 0.0

if "claimed_rewards" not in st.session_state:
    st.session_state.claimed_rewards = set()

if "donation_success_msg" not in st.session_state:
    st.session_state.donation_success_msg = None


# -----------------------------
# Log Out Confirmation Dialog
# -----------------------------
@st.dialog("Log Out Confirmation")
def logout_confirm_dialog():
    st.write(
        "Are you sure you want to log out? All changes and donations you made"
        " will remain saved."
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Close", use_container_width=True):
            st.rerun()

    with col2:
        if st.button("Yes", type="primary", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = "Guest"
            st.session_state.phone = ""
            st.session_state.description = (
                "Passionate about protecting wildlife!"
            )
            st.session_state.profile_pic = None
            st.session_state.view_profile = False
            st.rerun()


# =============================================================================
# 🔑 LOGIN / SIGN UP / GUEST VIEW
# =============================================================================
if not st.session_state.logged_in:

    st.title("Animal Advocators 🌿")
    st.subheader("Voice the Voiceless")

    st.write("Please log in, create an account, or continue as a guest.")

    login_tab, signup_tab = st.tabs(["🔑 Log In", "📝 Sign Up"])

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

    st.markdown("---")
    st.write("Don't want to make an account?")

    if st.button("Continue as Guest"):
        st.session_state.logged_in = True
        st.session_state.username = "Guest"
        st.rerun()

    show_bottom_banner()


# =============================================================================
# 🏠 MAIN APP VIEW
# =============================================================================
else:

    # -----------------------------
    # Shared Data Load (51 Animals)
    # -----------------------------
    animals = [
        {"Animal": "Amur Leopard", "Region": "Russia / China", "Status": "Critically Endangered", "Latitude": 43.2, "Longitude": 131.9, "Description": "One of the rarest big cats in the world.", "Keywords": "leopard leopards cat cats feline felines big cat"},
        {"Animal": "Javan Rhino", "Region": "Indonesia", "Status": "Critically Endangered", "Latitude": -6.75, "Longitude": 105.37, "Description": "Only a small population remains in Java.", "Keywords": "rhino rhinos rhinoceros rhinoceroses"},
        {"Animal": "Vaquita", "Region": "Gulf of California", "Status": "Critically Endangered", "Latitude": 31.0, "Longitude": -114.0, "Description": "The world's rarest marine mammal.", "Keywords": "vaquita porpoise porpoises marine mammal mammals"},
        {"Animal": "African Forest Elephant", "Region": "Central Africa", "Status": "Critically Endangered", "Latitude": 0.5, "Longitude": 21.0, "Description": "Threatened by habitat loss and poaching.", "Keywords": "elephant elephants"},
        {"Animal": "Red Wolf", "Region": "United States", "Status": "Critically Endangered", "Latitude": 35.5, "Longitude": -76.2, "Description": "One of the world's most endangered wolves.", "Keywords": "wolf wolves canine canines"},
        {"Animal": "Mountain Gorilla", "Region": "Rwanda / Uganda", "Status": "Endangered", "Latitude": -1.4, "Longitude": 29.6, "Description": "Lives in the forests of Central Africa.", "Keywords": "gorilla gorillas ape apes primate primates"},
        {"Animal": "Blue Whale", "Region": "Pacific Ocean", "Status": "Endangered", "Latitude": 36.6, "Longitude": -122.0, "Description": "The largest animal ever known.", "Keywords": "whale whales marine mammal mammals"},
        {"Animal": "Giant Panda", "Region": "China", "Status": "Vulnerable", "Latitude": 31.2, "Longitude": 103.5, "Description": "Famous for eating bamboo.", "Keywords": "panda pandas bear bears"},
        {"Animal": "Snow Leopard", "Region": "Himalayas", "Status": "Vulnerable", "Latitude": 34.0, "Longitude": 75.0, "Description": "Lives high in the mountains of Asia.", "Keywords": "leopard leopards snow leopard cat cats feline felines"},
        {"Animal": "Sea Otter", "Region": "North Pacific", "Status": "Endangered", "Latitude": 57.0, "Longitude": -152.0, "Description": "Helps keep kelp forests healthy.", "Keywords": "otter otters marine mammal mammals"},
        {"Animal": "Siberian Tiger", "Region": "Russia / China", "Status": "Endangered", "Latitude": 45.0, "Longitude": 134.0, "Description": "The largest wild cat, threatened by poaching.", "Keywords": "tiger tigers big cat feline"},
        {"Animal": "Chinese Giant Salamander", "Region": "China", "Status": "Critically Endangered", "Latitude": 31.0, "Longitude": 107.0, "Description": "The world's largest amphibian.", "Keywords": "salamander amphibian amphibians"},
        {"Animal": "Sumatran Orangutan", "Region": "Indonesia", "Status": "Critically Endangered", "Latitude": 3.3, "Longitude": 98.5, "Description": "Lives only on the island of Sumatra.", "Keywords": "orangutan ape primate"},
        {"Animal": "Sumatran Tiger", "Region": "Indonesia", "Status": "Critically Endangered", "Latitude": -1.5, "Longitude": 101.5, "Description": "The smallest surviving tiger subspecies.", "Keywords": "tiger big cat feline"},
        {"Animal": "Hawksbill Sea Turtle", "Region": "Pacific Ocean", "Status": "Critically Endangered", "Latitude": 10.0, "Longitude": -140.0, "Description": "A sea turtle known for its beautiful shell.", "Keywords": "turtle turtles sea turtle marine reptile"},
        {"Animal": "North Pacific Right Whale", "Region": "North Pacific", "Status": "Endangered", "Latitude": 55.0, "Longitude": -160.0, "Description": "One of the rarest whale species in the world.", "Keywords": "whale whales marine mammal"},
        {"Animal": "California Condor", "Region": "United States", "Status": "Critically Endangered", "Latitude": 36.5, "Longitude": -118.5, "Description": "North America's largest flying bird.", "Keywords": "condor bird birds vulture"},
        {"Animal": "Florida Panther", "Region": "United States", "Status": "Endangered", "Latitude": 26.2, "Longitude": -81.0, "Description": "A rare cougar found in southern Florida.", "Keywords": "panther cougar mountain lion cat feline"},
        {"Animal": "Bonobo", "Region": "Central Africa", "Status": "Endangered", "Latitude": -2.0, "Longitude": 23.0, "Description": "A great ape found only in Congo.", "Keywords": "bonobo ape primate chimpanzee"},
        {"Animal": "Okapi", "Region": "Central Africa", "Status": "Endangered", "Latitude": 2.5, "Longitude": 28.5, "Description": "A unique relative of the giraffe found in Congo.", "Keywords": "okapi giraffe mammal"},
        {"Animal": "Golden Monkey", "Region": "Rwanda / Uganda", "Status": "Endangered", "Latitude": -1.5, "Longitude": 29.6, "Description": "A colorful monkey living in Virunga Mountains.", "Keywords": "monkey monkeys primate"},
        {"Animal": "Black Rhinoceros", "Region": "Rwanda", "Status": "Critically Endangered", "Latitude": -1.9, "Longitude": 30.1, "Description": "A rhinoceros threatened by illegal poaching.", "Keywords": "rhino rhinoceros"},
        {"Animal": "Snowy Owl", "Region": "North Pacific", "Status": "Vulnerable", "Latitude": 60.0, "Longitude": -150.0, "Description": "A large white owl adapted to cold climates.", "Keywords": "owl bird birds"},
        {"Animal": "Pallas's Cat", "Region": "Himalayas", "Status": "Near Threatened", "Latitude": 35.5, "Longitude": 78.0, "Description": "A small wild cat with thick fur.", "Keywords": "cat feline wildcat"},
        {"Animal": "Red Panda", "Region": "Himalayas", "Status": "Endangered", "Latitude": 27.8, "Longitude": 88.2, "Description": "A tree-dwelling mammal known for reddish fur.", "Keywords": "red panda panda bear"},
        {"Animal": "Whale Shark", "Region": "Pacific Ocean", "Status": "Endangered", "Latitude": 15.0, "Longitude": -145.0, "Description": "The largest fish species in the world.", "Keywords": "shark sharks fish whale shark"},
        {"Animal": "Manta Ray", "Region": "Pacific Ocean", "Status": "Vulnerable", "Latitude": 12.0, "Longitude": -150.0, "Description": "A graceful giant ray threatened by fishing.", "Keywords": "ray manta ray fish"},
        {"Animal": "Guadalupe Fur Seal", "Region": "Gulf of California", "Status": "Endangered", "Latitude": 29.0, "Longitude": -113.0, "Description": "A marine mammal native to the eastern Pacific.", "Keywords": "seal seals marine mammal"},
        {"Animal": "Totoaba", "Region": "Gulf of California", "Status": "Critically Endangered", "Latitude": 30.8, "Longitude": -114.2, "Description": "A large fish threatened by illegal fishing.", "Keywords": "fish totoaba"},
        {"Animal": "Saiga Antelope", "Region": "Russia", "Status": "Critically Endangered", "Latitude": 49.5, "Longitude": 46.0, "Description": "A distinctive antelope known for its large nose.", "Keywords": "saiga antelope antelopes mammal mammals"},
        {"Animal": "Chinese Pangolin", "Region": "China", "Status": "Critically Endangered", "Latitude": 27.5, "Longitude": 112.5, "Description": "A shy mammal covered in protective scales.", "Keywords": "pangolin pangolins mammal mammals scales"},
        {"Animal": "Arctic Wolf", "Region": "North Pacific", "Status": "Least Concern", "Latitude": 71.0, "Longitude": -156.0, "Description": "A white-furred wolf adapted to Arctic tundra.", "Keywords": "wolf wolves arctic wolf canine canines"},
        {"Animal": "Mexican Gray Wolf", "Region": "United States", "Status": "Endangered", "Latitude": 33.5, "Longitude": -109.0, "Description": "The rarest gray wolf subspecies in North America.", "Keywords": "wolf wolves mexican gray wolf canine canines"},
        {"Animal": "Himalayan Wolf", "Region": "Himalayas", "Status": "Vulnerable", "Latitude": 34.5, "Longitude": 78.5, "Description": "An ancient wolf that lives at high elevations.", "Keywords": "wolf wolves himalayan wolf canine canines"},
        {"Animal": "Eurasian Wolf", "Region": "Russia", "Status": "Least Concern", "Latitude": 58.0, "Longitude": 90.0, "Description": "A widespread gray wolf subspecies.", "Keywords": "wolf wolves eurasian wolf gray wolf canine canines"},
        {"Animal": "Alexander Archipelago Wolf", "Region": "United States", "Status": "Near Threatened", "Latitude": 56.5, "Longitude": -133.0, "Description": "A coastal wolf inhabiting forests of Alaska.", "Keywords": "wolf wolves alexander archipelago wolf alaska canine canines"},
        {"Animal": "Kakapo", "Region": "New Zealand", "Status": "Critically Endangered", "Latitude": -45.0, "Longitude": 167.5, "Description": "A rare flightless parrot native to New Zealand.", "Keywords": "kakapo parrot bird flightless parrot new zealand"},
        {"Animal": "Galapagos Giant Tortoise", "Region": "Ecuador", "Status": "Vulnerable", "Latitude": -0.9, "Longitude": -90.9, "Description": "The largest living species of tortoise.", "Keywords": "tortoise giant tortoise reptile galapagos ecuador"},
        {"Animal": "Iberian Lynx", "Region": "Spain / Portugal", "Status": "Endangered", "Latitude": 37.5, "Longitude": -6.5, "Description": "A wild cat endemic to the Iberian Peninsula.", "Keywords": "lynx iberian lynx cat wildcat feline spain portugal"},
        {"Animal": "Cheetah", "Region": "Sub-Saharan Africa", "Status": "Vulnerable", "Latitude": -2.0, "Longitude": 34.5, "Description": "The fastest land animal on Earth.", "Keywords": "cheetah cat big cat feline africa fast mammal"},
        {"Animal": "Monarch Butterfly", "Region": "North America", "Status": "Endangered", "Latitude": 19.6, "Longitude": -100.3, "Description": "Famous for its long annual migration.", "Keywords": "monarch butterfly insect migration pollinator"},
        {"Animal": "African Wild Dog", "Region": "Sub-Saharan Africa", "Status": "Endangered", "Latitude": -18.0, "Longitude": 25.0, "Description": "Known for mottled fur and social pack behavior.", "Keywords": "wild dog african wild dog canine hunting dog mammal"},
        {"Animal": "Komodo Dragon", "Region": "Indonesia", "Status": "Endangered", "Latitude": -8.5, "Longitude": 119.5, "Description": "The largest living species of lizard.", "Keywords": "komodo dragon lizard reptile giant lizard indonesia"},
        {"Animal": "Axolotl", "Region": "Mexico", "Status": "Critically Endangered", "Latitude": 19.2, "Longitude": -99.1, "Description": "A unique walking salamander native to Lake Xochimilco.", "Keywords": "axolotl salamander amphibian Mexico xochimilco"},
        {"Animal": "Tasmanian Devil", "Region": "Australia", "Status": "Endangered", "Latitude": -42.0, "Longitude": 146.5, "Description": "The largest carnivorous marsupial.", "Keywords": "tasmanian devil marsupial australia tasmania mammal"},
        {"Animal": "Gharial", "Region": "India / Nepal", "Status": "Critically Endangered", "Latitude": 27.5, "Longitude": 81.2, "Description": "A fish-eating crocodilian with a long snout.", "Keywords": "gharial crocodile crocodilian reptile india nepal"},
        {"Animal": "Sloth Bear", "Region": "India / Sri Lanka", "Status": "Vulnerable", "Latitude": 20.5, "Longitude": 78.9, "Description": "A shaggy-coated bear adapted for feeding on insects.", "Keywords": "sloth bear bear mammal india sri lanka"},
        {"Animal": "Polar Bear", "Region": "North Pacific", "Status": "Vulnerable", "Latitude": 75.0, "Longitude": -100.0, "Description": "The world's largest land carnivore.", "Keywords": "polar bear bear arctic marine mammal ice"},
        {"Animal": "Tree Kangaroo", "Region": "Papua New Guinea", "Status": "Endangered", "Latitude": -6.0, "Longitude": 143.5, "Description": "A tree-dwelling marsupial adapted for climbing.", "Keywords": "tree kangaroo kangaroo marsupial papua new guinea"},
        {"Animal": "Amazon River Dolphin", "Region": "South America", "Status": "Endangered", "Latitude": -3.4, "Longitude": -62.2, "Description": "A pink freshwater dolphin native to Amazon basin.", "Keywords": "amazon river dolphin pink dolphin river dolphin freshwater marine mammal"},
        {"Animal": "Philippine Eagle", "Region": "Philippines", "Status": "Critically Endangered", "Latitude": 7.1, "Longitude": 125.6, "Description": "One of the world's largest forest eagles.", "Keywords": "philippine eagle eagle bird bird of prey raptor philippines"},
    ]

    df = pd.DataFrame(animals)

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
    # Sidebar Navigation
    # -----------------------------
    st.sidebar.title("☰ Navigation")

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
        logout_confirm_dialog()

    # -----------------------------
    # PAGE: PROFILE MANAGEMENT
    # -----------------------------
    if st.session_state.view_profile:
        st.title("👤 Profile & Account Settings")

        if st.button("<< Back to App"):
            st.session_state.view_profile = False
            st.rerun()

        st.markdown("---")

        col1, col2 = st.columns([1, 2])

        with col1:
            st.subheader("Profile Photo")
            st.image(pic_to_show, width=150)

            # Single Image Upload Field
            uploaded_file = st.file_uploader(
                "Upload photo", type=["jpg", "png", "jpeg"], key="single_pic_uploader"
            )
            if uploaded_file is not None:
                st.session_state.profile_pic = uploaded_file
                st.success("Photo updated successfully!")

        with col2:
            st.subheader("Account Details")
            new_username = st.text_input("Username", value=st.session_state.username)
            new_phone = st.text_input("Phone Number (Optional)", value=st.session_state.phone)
            new_description = st.text_area("Profile Description", value=st.session_state.description)

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

        st.title("Animal Advocators 🌿")
        st.subheader("Voice the Voiceless")

        st.success(f"Welcome, {st.session_state.username}!")

        st.write(
            """
        Animal Advocators is dedicated to protecting endangered wildlife around the world.
        Use the sidebar navigation to explore endangered species, learn about conservation, and support wildlife through donations.
        """
        )

        st.markdown("---")

        search = st.text_input("🔎 Search for an endangered animal or region:")

        if search.strip():
            search_terms = normalize_search(search)

            def matches(row):
                searchable = (
                    f"{row['Animal']} {row['Region']} {row['Description']} {row['Keywords']}"
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

        # DONATION CIRCLE & PRIZE CLAIM SYSTEM
        st.markdown("---")
        st.header("💚 Circular Donation Goal & Rewards Tracker")

        if st.session_state.donation_success_msg:
            st.balloons()
            st.success(st.session_state.donation_success_msg)
            st.session_state.donation_success_msg = None

        curr_donation = st.session_state.total_donated
        goal_val = 5000.0
        pct = min(100.0, (curr_donation / goal_val) * 100)
        stroke_dash = float(pct * 2.83)  # SVG Circumference math

        circle_col, reward_col = st.columns([1, 2])

        with circle_col:
            st.subheader("Circle Goal Tracker")
            # SVG Circular Progress Ring
            st.markdown(
                f"""
                <div style="display: flex; flex-direction: column; align-items: center; justify-content: center;">
                    <svg width="160" height="160" viewBox="0 0 100 100">
                        <circle cx="50" cy="50" r="45" fill="none" stroke="#e6e6e6" stroke-width="8" />
                        <circle cx="50" cy="50" r="45" fill="none" stroke="#11998e" stroke-width="8"
                                stroke-dasharray="{stroke_dash} 283" stroke-linecap="round" transform="rotate(-90 50 50)" />
                        <text x="50" y="52" font-size="14" font-weight="bold" text-anchor="middle" fill="#11998e">{pct:.0f}%</text>
                    </svg>
                    <p style="margin-top: 10px; font-weight: bold; font-size: 1.1rem;">Raised: ${curr_donation:,.2f} / $5,000</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with reward_col:
            st.subheader("🎁 Milestone Prize Unlocks")

            milestones = [
                ("keychain", 100.0, "🔑 Free Keychain"),
                ("tshirt", 500.0, "👕 Free T-Shirt"),
                ("discount", 1000.0, "🏷️ Merch Discount"),
                ("vip", 5000.0, "🌟 VIP Visit to Help"),
            ]

            for item_id, goal_amt, label in milestones:
                col_m1, col_m2 = st.columns([2, 1])

                with col_m1:
                    if curr_donation >= goal_amt:
                        st.markdown(f"**{label}** (${goal_amt:,.0f}): <span style='color:green;'>Unlocked!</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"**{label}** (${goal_amt:,.0f}): Needs ${goal_amt - curr_donation:,.2f} more", unsafe_allow_html=True)

                with col_m2:
                    if curr_donation >= goal_amt:
                        if item_id in st.session_state.claimed_rewards:
                            st.button("✅ Claimed", key=f"claimed_{item_id}", disabled=True)
                        else:
                            if st.button(f"🎁 Claim Prize", key=f"claim_{item_id}"):
                                st.session_state.claimed_rewards.add(item_id)
                                st.balloons()
                                st.success(f"You claimed your {label}!")
                                st.rerun()
                    else:
                        st.button("Locked 🔒", key=f"locked_{item_id}", disabled=True)

        st.markdown("---")
        st.subheader("💳 Make a Donation (Credit Card or Gift Card)")

        with st.form("donation_payment_form"):
            donation_amt = st.number_input(
                "Enter Donation Amount ($):", min_value=1.0, value=50.0, step=5.0
            )

            pay_method = st.radio(
                "Select Payment Method:",
                ["Credit Card 💳", "Gift Card 🎁"],
                horizontal=True
            )

            if pay_method == "Credit Card 💳":
                card_type = st.selectbox("Card Brand:", ["Visa", "Mastercard", "American Express", "Discover"])
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    card_name = st.text_input("Cardholder Name")
                    card_num = st.text_input("Card Number", type="password")
                with col_c2:
                    expiry = st.text_input("MM/YY")
                    cvv = st.text_input("CVV", type="password")
            else:
                gift_code = st.text_input("Enter 16-Digit Gift Card Code:", type="password")
                gift_pin = st.text_input("Gift Card PIN:", type="password")

            pay_submitted = st.form_submit_button("Complete Donation")

            if pay_submitted:
                if pay_method == "Credit Card 💳" and (not card_name or not card_num or not expiry or not cvv):
                    st.error("Please fill in all credit card details.")
                elif pay_method == "Gift Card 🎁" and (not gift_code or not gift_pin):
                    st.error("Please enter a valid Gift Card Code and PIN.")
                else:
                    st.session_state.total_donated += donation_amt
                    st.session_state.donation_success_msg = (
                        f"Thank you for donating ${donation_amt:,.2f} using {pay_method}! "
                        f"Your updated total is ${st.session_state.total_donated:,.2f}."
                    )
                    st.rerun()

        show_bottom_banner()

    # -----------------------------
    # PAGE 2: OVERVIEW
    # -----------------------------
    elif page == "🌎 Overview":
        st.title("🌎 Overview & Mission")
        st.write(
            """
        Welcome to the Overview of **Animal Advocators**. 

        Human expansion, poaching, and climate change threaten thousands of unique species across the globe. 
        Our goal is to spread awareness, display real-time geographic data on endangered species, and collect 
        critical donations to fund global conservation projects.
        """
        )

        st.markdown("---")
        st.subheader("📊 Wildlife Conservation Impact")
        col1, col2, col3 = st.columns(3)
        col1.metric("Species Tracked", len(df))
        col2.metric("Critical Regions", len(df["Region"].unique()))
        col3.metric("Funds Raised", f"${st.session_state.total_donated:,.2f}")

        show_bottom_banner()

    # -----------------------------
    # PAGE 3: ENDANGERED ANIMAL LIBRARY
    # -----------------------------
    elif page == "📚 Endangered Animal Library":
        st.title("📚 Endangered Animal Library")
        st.write("Explore all 51 species tracked in our system.")

        selected_status = st.multiselect(
            "Filter by Threat Status:",
            options=df["Status"].unique(),
            default=df["Status"].unique(),
        )

        filtered_library = df[df["Status"].isin(selected_status)]

        st.dataframe(
            filtered_library[["Animal", "Region", "Status", "Description"]],
            use_container_width=True,
        )

        show_bottom_banner()

    # -----------------------------
    # PAGE 4: OTHER WAYS TO HELP
    # -----------------------------
    elif page == "🤝 Other Ways To Help":
        st.title("🤝 Other Ways To Help")
        st.write("Donations aren't the only way to make a difference! Here is how you can help protect wild animals:")

        st.markdown(
            """
        * **📢 Spread Awareness**: Share wildlife protection campaigns on social media.
        * **🌳 Reduce Carbon Footprint**: Protect natural habitats by reducing waste and recycling.
        * **🙋 Volunteer**: Join local environmental cleanups and wildlife shelters.
        * **🚫 Say No to Illegal Wildlife Trade**: Avoid purchasing products made from endangered species.
        """
        )

        show_bottom_banner()

    # -----------------------------
    # PAGE 5: SETTINGS & FEEDBACK / BUG REPORTING
    # -----------------------------
    elif page == "⚙️ Settings":
        st.title("⚙️ Settings & Support")

        st.subheader("🔔 Preferences")
        st.checkbox("Enable email updates for goal rewards", value=True)
        st.checkbox("Show map animation effects", value=True)

        st.markdown("---")

        st.subheader("💬 Contact Us & Send Feedback")
        st.write("Report bugs, glitches, or send feedback directly to our team!")

        with st.form("feedback_and_bug_form"):
            feedback_type = st.selectbox(
                "Category:",
                ["🐛 Bug / Error Report", "💡 General Feedback", "❓ Question / Support"]
            )
            user_email = st.text_input("Your Email Address (Optional):")
            subject = st.text_input("Subject:")
            message = st.text_area("Describe the bug or feedback in detail:")

            submit_feedback = st.form_submit_button("Submit Message")

            if submit_feedback:
                if not message or not subject:
                    st.error("Please provide both a subject and a description.")
                else:
                    st.success("Thank you! Your report has been submitted to our team.")

        show_bottom_banner()