import streamlit as st
import pandas as pd
import pydeck as pdk

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="Animal Advocators",
    page_icon="🦁",
    layout="wide"
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

if "profile_pic" not in st.session_state:
    st.session_state.profile_pic = None

if "bio" not in st.session_state:
    st.session_state.bio = "Wildlife advocate passionate about protecting endangered species."

if "phone" not in st.session_state:
    st.session_state.phone = ""

if "editing_profile" not in st.session_state:
    st.session_state.editing_profile = False

# -----------------------------
# Full Animals Dataset
# -----------------------------
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

# -----------------------------
# SEARCH NORMALIZATION FUNCTION
# -----------------------------
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
# AUTHENTICATION SCREEN
# -----------------------------
if not st.session_state.logged_in:
    st.title("🌿 Animal Advocators")
    st.subheader("Voice the Voiceless")
    st.write("Please log in, create an account, or continue as a guest.")

    login_tab, signup_tab = st.tabs(["🔑 Log In", "📝 Sign Up"])

    # Log In Tab
    with login_tab:
        login_username = st.text_input("Username", key="login_user")
        login_password = st.text_input("Password", type="password", key="login_pass")

        if st.button("Log In"):
            if login_username and login_password:
                st.session_state.logged_in = True
                st.session_state.username = login_username
                st.rerun()
            else:
                st.error("Please enter both username and password.")

    # Sign Up Tab
    with signup_tab:
        username = st.text_input("Create Username")
        email = st.text_input("Email Address")
        phone = st.text_input("Phone Number (Optional)")
        password = st.text_input("Create Password", type="password")
        confirm = st.text_input("Confirm Password", type="password")

        if st.button("Create Account"):
            if username == "" or email == "" or password == "":
                st.error("Please complete all required fields.")
            elif password != confirm:
                st.error("Passwords do not match.")
            else:
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

# -----------------------------
# MAIN APPLICATION SCREEN
# -----------------------------
else:
    # Sidebar Navigation
    st.sidebar.title("☰ Navigation")
    
    # Sidebar Profile Display
    if st.session_state.profile_pic:
        st.sidebar.image(st.session_state.profile_pic, width=80)
    else:
        st.sidebar.write("👤 *(No Photo)*")
        
    st.sidebar.write(f"**{st.session_state.username}**")

    page = st.sidebar.radio(
        "Go to",
        [
            "🏠 Home",
            "🌎 Overview",
            "📚 Endangered Animal Library",
            "🤝 What You Can Do To Help",
            "👤 Profile & Settings",
        ]
    )

    st.sidebar.markdown("---")

    if st.sidebar.button("🚪 Log Out"):
        st.session_state.logged_in = False
        st.session_state.username = "Guest"
        st.session_state.profile_pic = None
        st.session_state.phone = ""
        st.session_state.editing_profile = False
        st.rerun()

    # -----------------------------------
    # HOME PAGE (Search, Map & Donation)
    # -----------------------------------
    if page == "🏠 Home":
        st.title("🌿 Animal Advocators")
        st.subheader("Voice the Voiceless")
        st.success(f"Welcome, {st.session_state.username}!")

        st.write("""
        Animal Advocators is dedicated to protecting endangered wildlife around the world.
        Use the search bar below to find specific animals or regions, explore the map, or support wildlife through donations.
        """)

        # --- HOME SEARCH BAR ---
        home_search = st.text_input("🔎 Search for an endangered animal or region:")

        if home_search.strip():
            search_terms = normalize_search(home_search)

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

        # --- SEARCH RESULTS (DISPLAYED IF FILTERED) ---
        if home_search.strip():
            st.markdown(f"### 🎯 Results for '{home_search}'")
            if filtered_df.empty:
                st.warning("No animals were found matching your search.")
            else:
                for _, animal in filtered_df.iterrows():
                    st.info(f"**{animal['Animal']}** — *{animal['Region']}* ({animal['Status']})\n\n{animal['Description']}")

        # --- MAP SECTION ---
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

        # --- DONATION SECTION ---
        st.markdown("---")
        st.header("💚 Donation")

        donation = st.slider(
            "Choose a donation amount ($)",
            min_value=5,
            max_value=500,
            value=25,
            step=5
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

        col5, col6, col7 = st.columns(3)

        with col5:
            if st.button("🎁 Visa Gift Card", use_container_width=True):
                st.session_state.payment_method = "Visa Gift Card"

        with col6:
            if st.button("🎁 Mastercard Gift Card", use_container_width=True):
                st.session_state.payment_method = "Mastercard Gift Card"

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
                        st.success(f"🎉 Thank you for donating ${donation} using {st.session_state.payment_method}!")
                    else:
                        st.error("Please enter your gift card code.")
                else:
                    if card_number and card_name and expiry and cvv:
                        st.success(f"🎉 Thank you for donating ${donation} using {st.session_state.payment_method}!")
                    else:
                        st.error("Please complete all payment information.")

    # -----------------------------------
    # OVERVIEW PAGE
    # -----------------------------------
    elif page == "🌎 Overview":
        st.title("🌎 Overview")
        
        st.markdown("""
        ### 🎯 Our Mission
        **Animal Advocators** raises awareness for endangered animals and supports global conservation efforts.
        We provide tools for education, mapping, and direct financial contributions to preserve our planet's bio-diversity.

        ### 🌿 What We Do
        - **Educate:** Provide accurate data and conservation statuses for vulnerable species.
        - **Visualize:** Map habitats globally so users can see where conservation focus is needed most.
        - **Action:** Facilitate direct support to fund sanctuary protections, anti-poaching initiatives, and habitat restoration.
        """)

    # -----------------------------------
    # ENDANGERED ANIMAL LIBRARY PAGE
    # -----------------------------------
    elif page == "📚 Endangered Animal Library":
        st.title("📚 Endangered Animal Library")

        search = st.text_input("🔎 Search for an endangered animal or region:")

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

        if filtered_df.empty:
            st.warning("No animals were found.")
        else:
            st.dataframe(
                filtered_df[["Animal", "Region", "Status", "Description"]],
                use_container_width=True
            )

    # -----------------------------------
    # WHAT YOU CAN DO TO HELP PAGE
    # -----------------------------------
    elif page == "🤝 What You Can Do To Help":
        st.title("🤝 What You Can Do To Help")
        st.write("Every action counts when it comes to preserving wildlife. Here are meaningful ways you can help protect endangered species:")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("1. 📢 Spread Awareness")
            st.write("Share information about endangered animals with friends, family, and social media networks. Educating others is the first step toward conservation.")

            st.subheader("2. 🛍️ Make Sustainable Choices")
            st.write("Avoid products made from endangered species, reduce single-use plastics that harm marine life, and support eco-friendly wildlife tourism.")

            st.subheader("3. 💚 Donate & Support")
            st.write("Contributions directly fund habitat protection, anti-poaching ranger patrols, and wildlife rehabilitation centers across the globe.")

        with col2:
            st.subheader("4. 🌿 Protect Natural Habitats")
            st.write("Plant native plants, reduce waste, and support local wildlife conservation projects and nature preserves in your community.")

            st.subheader("5. 📜 Advocate for Policy Change")
            st.write("Support wildlife protection legislation and vote for policies that protect vulnerable natural ecosystems and combat climate change.")

            st.subheader("6. 📚 Stay Educated")
            st.write("Use our **Endangered Animal Library** to keep updated on species status and learn more about global environmental challenges.")

    # -----------------------------------
    # PROFILE & SETTINGS PAGE
    # -----------------------------------
    elif page == "👤 Profile & Settings":
        st.title("👤 User Profile & Settings")

        profile_col, edit_col = st.columns([1, 2])

        with profile_col:
            st.subheader("Profile Details")
            if st.session_state.profile_pic:
                st.image(st.session_state.profile_pic, width=150)
            else:
                st.info("📷 No Profile Picture Uploaded")

            st.write(f"**Username:** {st.session_state.username}")
            st.write(f"**Bio / Description:** {st.session_state.bio}")
            st.write(f"**Phone Number:** {st.session_state.phone if st.session_state.phone else 'Not provided'}")

            if st.button("✏️ Edit Profile"):
                st.session_state.editing_profile = not st.session_state.editing_profile

        with edit_col:
            if st.session_state.editing_profile:
                st.subheader("✏️ Edit Profile Information")

                # 1. Profile Picture Upload
                uploaded_photo = st.file_uploader("Upload Profile Picture", type=["png", "jpg", "jpeg"])

                # 2. Change Name (Restricted for Guest)
                if st.session_state.username == "Guest":
                    st.text_input("Username", value="Guest", disabled=True, help="Guests cannot change their username.")
                    new_name = "Guest"
                else:
                    new_name = st.text_input("Username", value=st.session_state.username)

                # 3. Description / Bio
                new_bio = st.text_area("Description / Bio", value=st.session_state.bio)

                # 4. Optional Phone Number
                new_phone = st.text_input("Phone Number (Optional)", value=st.session_state.phone)

                if st.button("💾 Save Profile Changes"):
                    if uploaded_photo is not None:
                        st.session_state.profile_pic = uploaded_photo
                    
                    if st.session_state.username != "Guest" and new_name.strip():
                        st.session_state.username = new_name.strip()
                    
                    st.session_state.bio = new_bio.strip()
                    st.session_state.phone = new_phone.strip()
                    st.session_state.editing_profile = False
                    st.success("✅ Profile updated successfully!")
                    st.rerun()

        st.markdown("---")
        st.header("⚙️ App Support & Feedback")

        tab_feedback, tab_bug = st.tabs(["💬 Send Feedback", "🐛 Report a Bug or Error"])

        # Feedback Tab
        with tab_feedback:
            st.subheader("Share Your Thoughts")
            st.write("How can we improve your experience with Animal Advocators?")
            
            rating = st.select_slider(
                "How would you rate your overall experience?",
                options=["⭐ Poor", "⭐⭐ Fair", "⭐⭐⭐ Good", "⭐⭐⭐⭐ Very Good", "⭐⭐⭐⭐⭐ Excellent"],
                value="⭐⭐⭐⭐⭐ Excellent"
            )
            feedback_text = st.text_area("Your Feedback or Suggestions:", placeholder="Type your feedback here...")

            if st.button("Submit Feedback"):
                if feedback_text.strip():
                    st.success("🎉 Thank you! Your feedback has been sent to our team.")
                else:
                    st.error("Please enter some text before submitting.")

        # Bug Report Tab
        with tab_bug:
            st.subheader("Report an Issue")
            st.write("Found a bug or incorrect information? Let us know below.")

            bug_category = st.selectbox(
                "Issue Category:",
                ["Map / Display Error", "Incorrect Animal Data", "Payment / Donation Issue", "Search Bar Issue", "Other"]
            )
            bug_title = st.text_input("Brief Summary of the Issue:", placeholder="e.g., Map dots not loading")
            bug_details = st.text_area("Detailed Description:", placeholder="Please describe what happened and how to reproduce it...")

            if st.button("Submit Bug Report"):
                if bug_title.strip() and bug_details.strip():
                    st.success("🚨 Bug report submitted! Thank you for helping us keep Animal Advocators running smoothly.")
                else:
                    st.error("Please complete both the summary and detailed description fields.")

    # -----------------------------------
    # Footer
    # -----------------------------------
    st.markdown("---")
    st.caption("Animal Advocators • Helping Wild Animals Worldwide 🌍")