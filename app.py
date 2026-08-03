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

    <script>
        window.scrollTo(0, 0);
    </script>
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

if "view_profile" not in st.session_state:
    st.session_state.view_profile = False

# Donation goal trackers
if "total_donated" not in st.session_state:
    st.session_state.total_donated = 0.0

if "donation_success_msg" not in st.session_state:
    st.session_state.donation_success_msg = None


# -----------------------------
# Log Out Confirmation Dialog (Pop-up)
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
# 🏠 HOME / MAIN APP VIEW
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
            "Keywords": "leopard leopards snow leopard cat cats feline felines",
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
    # Sidebar Navigation Header
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

        if st.button("← Back to App"):
            st.session_state.view_profile = False
            st.rerun()

        st.markdown("---")

        col1, col2 = st.columns([1, 2])

        with col1:
            st.subheader("Profile Photo")
            st.image(pic_to_show, width=150)

            # Single Uploader Input
            uploaded_file = st.file_uploader(
                "Upload a new photo", type=["jpg", "png", "jpeg"], key="profile_photo_uploader"
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
        Use the navigation menu on the left to explore endangered species, learn about conservation, and support wildlife through donations.
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

        # DONATION SECTION WITH REWARDS & CREDIT CARD PAYMENT
        st.markdown("---")
        st.header("💚 Donation Goal Tracker & Free Rewards")

        if st.session_state.donation_success_msg:
            st.balloons()
            st.success(st.session_state.donation_success_msg)
            st.session_state.donation_success_msg = None

        current_total = st.session_state.total_donated
        goal_5000 = 5000.0
        progress_pct = min(1.0, current_total / goal_5000)

        # Rewards Milestone Display Table
        st.subheader("🎯 Reward Milestones")

        r1 = "✅ UNLOCKED!" if current_total >= 100 else f"${100 - current_total:,.2f} remaining"
        r2 = "✅ UNLOCKED!" if current_total >= 500 else f"${500 - current_total:,.2f} remaining"
        r3 = "✅ UNLOCKED!" if current_total >= 1000 else f"${1000 - current_total:,.2f} remaining"
        r4 = "✅ UNLOCKED!" if current_total >= 5000 else f"${5000 - current_total:,.2f} remaining"

        col_a, col_b, col_c, col_d = st.columns(4)
        col_a.metric("🔑 Free Keychain", "$100 Goal", r1)
        col_b.metric("👕 Free T-Shirt", "$500 Goal", r2)
        col_c.metric("🏷️ Merch Discount", "$1,000 Goal", r3)
        col_d.metric("🌟 VIP Visit to Help", "$5,000 Goal", r4)

        st.write(f"**Overall Goal Progress to Maximum VIP Reward ($5,000):**")
        st.progress(progress_pct)
        st.metric(label="Total Donated So Far", value=f"${current_total:,.2f}")

        # Payment Form
        st.subheader("💳 Make a Donation")
        with st.form("donation_payment_form"):
            donation_amt = st.number_input(
                "Enter Donation Amount ($):", min_value=1.0, value=50.0, step=5.0
            )

            card_type = st.selectbox(
                "Select Credit Card Type:",
                ["Visa 💳", "Mastercard 💳", "American Express 💳", "Discover 💳"]
            )

            col_card1, col_card2 = st.columns(2)
            with col_card1:
                card_name = st.text_input("Cardholder Name")
                card_num = st.text_input("Card Number", type="password", max_chars=16)
            with col_card2:
                expiry = st.text_input("Expiration Date (MM/YY)", max_chars=5)
                cvv = st.text_input("CVV / CVC", type="password", max_chars=4)

            pay_submitted = st.form_submit_button("Complete Payment & Donate")

            if pay_submitted:
                if not card_name or not card_num or not expiry or not cvv:
                    st.error("Please fill in all credit card payment details.")
                else:
                    st.session_state.total_donated += donation_amt
                    st.session_state.donation_success_msg = (
                        f"Thank you for donating ${donation_amt:,.2f} via {card_type}! "
                        f"Your current total donated is ${st.session_state.total_donated:,.2f}."
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
        st.write("Explore information on protected species tracked in our system.")

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
        st.write("Report bugs, glitches, or send feedback to help us improve the app!")

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
                    st.error("Please provide both a subject and a message description.")
                else:
                    st.success("Thank you! Your feedback/bug report has been successfully submitted to our team.")

        show_bottom_banner()