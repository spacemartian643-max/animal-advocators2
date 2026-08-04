import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import pydeck as pdk
import requests
import sqlite3
import hashlib

# Default placeholder image (Standard user profile avatar)
DEFAULT_AVATAR = "https://upload.wikimedia.org/wikipedia/commons/7/7c/Profile_avatar_placeholder_large.png"

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="Animal Advocators",
    page_icon="🦁",
    layout="wide"
)

# -----------------------------
# Database Setup (SQLite) for User Accounts
# -----------------------------
DB_PATH = "animal_advocators_users.db"

def init_db():
    """Creates the users table if it doesn't already exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            email TEXT,
            phone TEXT,
            password_hash TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def hash_password(password: str) -> str:
    """Returns a SHA-256 hash of the given password (so raw passwords are never stored)."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def create_user(username: str, email: str, phone: str, password: str) -> bool:
    """
    Adds a new user to the database.
    Returns True if the account was created, False if the username already exists.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
    if cursor.fetchone() is not None:
        conn.close()
        return False

    cursor.execute(
        "INSERT INTO users (username, email, phone, password_hash) VALUES (?, ?, ?, ?)",
        (username, email, phone, hash_password(password))
    )
    conn.commit()
    conn.close()
    return True

def verify_user(username: str, password: str) -> bool:
    """Checks whether the given username/password combination matches a stored account."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return False
    return row[0] == hash_password(password)

# Make sure the database and users table exist before the app runs
init_db()

# -----------------------------
# Helper Function: Confetti Effect
# -----------------------------
def trigger_confetti():
    components.html(
        """
        <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
        <script>
            confetti({
                particleCount: 120,
                spread: 80,
                origin: { y: 0.6 }
            });
        </script>
        """,
        height=0
    )

# -----------------------------
# Helper Function: Animated Gradient Progress Bar
# -----------------------------
def gradient_progress_bar(progress_pct, height_px=22):
    pct = max(0.0, min(progress_pct, 1.0)) * 100
    st.markdown(
        f"""
        <style>
        @keyframes gradientMove {{
            0% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
            100% {{ background-position: 0% 50%; }}
        }}
        .gradient-progress-outer {{
            width: 100%;
            background-color: #e0e0e0;
            border-radius: 999px;
            padding: 3px;
            box-sizing: border-box;
            margin: 8px 0 16px 0;
        }}
        .gradient-progress-inner {{
            width: {pct}%;
            height: {height_px}px;
            border-radius: 999px;
            background: linear-gradient(90deg, #1e88e5, #43a047, #1e88e5, #43a047);
            background-size: 300% 300%;
            animation: gradientMove 4s ease infinite;
            transition: width 0.4s ease;
        }}
        </style>
        <div class="gradient-progress-outer">
            <div class="gradient-progress-inner"></div>
        </div>
        """,
        unsafe_allow_html=True
    )

# -----------------------------
# Helper Function: Correct, Animal-Specific Photo Lookup
# -----------------------------
FALLBACK_ANIMAL_PHOTO = "https://placehold.co/500x350?text=Photo+Unavailable"

@st.cache_data(ttl=60 * 60 * 24, show_spinner=False)
def get_animal_photo_url(animal_name: str) -> str:
    """
    Looks up the real photo for a SPECIFIC animal by querying Wikipedia's
    summary API using that exact animal's name, so the photo returned is
    always tied to the correct animal (never a random/generic image).
    """
    try:
        title = animal_name.strip().replace(" ", "_")
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
        headers = {"User-Agent": "AnimalAdvocatorsApp/1.0 (educational streamlit app)"}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            thumbnail = data.get("thumbnail", {}).get("source")
            original = data.get("originalimage", {}).get("source")
            if thumbnail:
                return thumbnail
            if original:
                return original
        return FALLBACK_ANIMAL_PHOTO
    except Exception:
        return FALLBACK_ANIMAL_PHOTO

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

if "page" not in st.session_state:
    st.session_state.page = "🏠 Home"

if "show_logout_dialog" not in st.session_state:
    st.session_state.show_logout_dialog = False

# --- Donation & Reward Gamification State ---
if "total_donated" not in st.session_state:
    st.session_state.total_donated = 0

if "current_goal" not in st.session_state:
    st.session_state.current_goal = 100

if "claimed_rewards" not in st.session_state:
    st.session_state.claimed_rewards = []

# --- Map Click -> Per-Animal Donation State ---
GENERAL_FUND_LABEL = "🌍 General Conservation Fund"

if "donation_target" not in st.session_state:
    st.session_state.donation_target = GENERAL_FUND_LABEL

if "_clear_map_selection" not in st.session_state:
    st.session_state._clear_map_selection = False

GOAL_TIERS = [
    {"goal": 100, "reward": "🔑 Free Keychain"},
    {"goal": 500, "reward": "👕 Free T-Shirt"},
    {"goal": 1000, "reward": "🏷️ Special Merch Discount"},
    {"goal": 5000, "reward": "🎟️ VIP Tour: Visit How We Help Animals!"},
]

# -----------------------------
# Modal Dialog: Logout Confirmation
# -----------------------------
@st.dialog("⚠️ Logout Confirmation")
def logout_modal():
    st.write("Are you sure you want to log out? Everything you have done will not change.")
    col_close, col_yes = st.columns(2)
    
    with col_close:
        if st.button("Close", use_container_width=True):
            st.session_state.show_logout_dialog = False
            st.session_state.page = "🏠 Home"
            st.rerun()

    with col_yes:
        if st.button("Yes", use_container_width=True, type="primary"):
            st.session_state.logged_in = False
            st.session_state.username = "Guest"
            st.session_state.profile_pic = None
            st.session_state.phone = ""
            st.session_state.editing_profile = False
            st.session_state.page = "🏠 Home"
            st.session_state.show_logout_dialog = False
            st.rerun()

# Trigger dialog if requested
if st.session_state.show_logout_dialog:
    logout_modal()

# -----------------------------
# Full Animals Dataset
# -----------------------------
animals = [
    # --- Original Dataset ---
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
        "Description": "A distinctive antelope known for its large, flexible nose.",
        "Keywords": "saiga antelope antelopes mammal mammals"
    },
    {
        "Animal": "Chinese Pangolin",
        "Region": "China",
        "Status": "Critically Endangered",
        "Latitude": 27.5,
        "Longitude": 112.5,
        "Description": "A shy, nocturnal mammal covered in protective scales.",
        "Keywords": "pangolin pangolins mammal mammals scales"
    },
    {
        "Animal": "Arctic Wolf",
        "Region": "North Pacific",
        "Status": "Least Concern",
        "Latitude": 71.0,
        "Longitude": -156.0,
        "Description": "A white-furred subspecies of the gray wolf adapted to Arctic tundra.",
        "Keywords": "wolf wolves arctic wolf canine canines"
    },
    {
        "Animal": "Mexican Gray Wolf",
        "Region": "United States",
        "Status": "Endangered",
        "Latitude": 33.5,
        "Longitude": -109.0,
        "Description": "The rarest gray wolf subspecies in North America.",
        "Keywords": "wolf wolves mexican gray wolf canine canines"
    },
    {
        "Animal": "Himalayan Wolf",
        "Region": "Himalayas",
        "Status": "Vulnerable",
        "Latitude": 34.5,
        "Longitude": 78.5,
        "Description": "An ancient lineage of wolf that lives high in the Himalayas.",
        "Keywords": "wolf wolves himalayan wolf canine canines"
    },
    {
        "Animal": "Eurasian Wolf",
        "Region": "Russia",
        "Status": "Least Concern",
        "Latitude": 58.0,
        "Longitude": 90.0,
        "Description": "A widespread gray wolf subspecies across Europe and Asia.",
        "Keywords": "wolf wolves eurasian wolf gray wolf canine canines"
    },
    {
        "Animal": "Alexander Archipelago Wolf",
        "Region": "United States",
        "Status": "Near Threatened",
        "Latitude": 56.5,
        "Longitude": -133.0,
        "Description": "A coastal wolf that inhabits the islands of southeastern Alaska.",
        "Keywords": "wolf wolves alexander archipelago wolf alaska canine canines"
    },

    # --- 10 ANTARCTICA ANIMALS ---
    {
        "Animal": "Emperor Penguin",
        "Region": "Antarctica",
        "Status": "Near Threatened",
        "Latitude": -75.0,
        "Longitude": 0.0,
        "Description": "The tallest and heaviest of all living penguin species, breeding in extreme cold.",
        "Keywords": "penguin penguins emperor bird birds antarctica polar"
    },
    {
        "Animal": "Weddell Seal",
        "Region": "Antarctica",
        "Status": "Least Concern",
        "Latitude": -77.8,
        "Longitude": 166.6,
        "Description": "An ice-dwelling seal that lives further south than any other mammal.",
        "Keywords": "seal seals weddell marine mammal polar antarctica"
    },
    {
        "Animal": "Leopard Seal",
        "Region": "Antarctica",
        "Status": "Least Concern",
        "Latitude": -65.0,
        "Longitude": -64.0,
        "Description": "A formidable Antarctic predator known for its spotted coat and speed in water.",
        "Keywords": "seal seals leopard seal marine mammal predator antarctica"
    },
    {
        "Animal": "Antarctic Krill",
        "Region": "Antarctica",
        "Status": "Least Concern",
        "Latitude": -60.0,
        "Longitude": -45.0,
        "Description": "Tiny swimming crustaceans that form the foundation of the Antarctic food web.",
        "Keywords": "krill crustacean marine life food chain antarctica"
    },
    {
        "Animal": "Snow Petrel",
        "Region": "Antarctica",
        "Status": "Least Concern",
        "Latitude": -71.0,
        "Longitude": 10.0,
        "Description": "A pure white bird that nests exclusively on the Antarctic continent.",
        "Keywords": "petrel snow petrel bird birds antarctica polar"
    },
    {
        "Animal": "Hourglass Dolphin",
        "Region": "Antarctica",
        "Status": "Least Concern",
        "Latitude": -62.0,
        "Longitude": -60.0,
        "Description": "A striking black-and-white dolphin native to cold Antarctic waters.",
        "Keywords": "dolphin dolphins hourglass marine mammal antarctica"
    },
    {
        "Animal": "Chinstrap Penguin",
        "Region": "Antarctica",
        "Status": "Least Concern",
        "Latitude": -62.2,
        "Longitude": -58.9,
        "Description": "Named for the thin black band under its chin, nesting in large Antarctic colonies.",
        "Keywords": "penguin penguins chinstrap bird birds antarctica"
    },
    {
        "Animal": "Adélie Penguin",
        "Region": "Antarctica",
        "Status": "Least Concern",
        "Latitude": -66.5,
        "Longitude": 140.0,
        "Description": "A classic tuxedo-patterned penguin common along the Antarctic coast.",
        "Keywords": "penguin penguins adelie bird birds antarctica"
    },
    {
        "Animal": "Antarctic Petrel",
        "Region": "Antarctica",
        "Status": "Least Concern",
        "Latitude": -70.0,
        "Longitude": 2.0,
        "Description": "A brown-and-white seabird highly adapted to life in icy polar winds.",
        "Keywords": "petrel antarctic petrel bird birds seabird antarctica"
    },
    {
        "Animal": "Wandering Albatross",
        "Region": "Antarctica",
        "Status": "Vulnerable",
        "Latitude": -54.0,
        "Longitude": -38.0,
        "Description": "Boasts the largest wingspan of any living bird, soaring over Southern oceans.",
        "Keywords": "albatross wandering albatross bird birds wingspan antarctica"
    },

    # --- 15 OTHER GLOBAL ANIMALS ---
    {
        "Animal": "Tasmanian Devil",
        "Region": "Australia",
        "Status": "Endangered",
        "Latitude": -42.0,
        "Longitude": 146.5,
        "Description": "The world's largest carnivorous marsupial, native to Tasmania.",
        "Keywords": "tasmanian devil marsupial australia carnivore"
    },
    {
        "Animal": "Kakapo",
        "Region": "New Zealand",
        "Status": "Critically Endangered",
        "Latitude": -46.6,
        "Longitude": 167.5,
        "Description": "A rare, flightless, nocturnal parrot native to New Zealand.",
        "Keywords": "kakapo parrot bird flightless new zealand"
    },
    {
        "Animal": "Lemur Leaf Frog",
        "Region": "Central America",
        "Status": "Critically Endangered",
        "Latitude": 9.5,
        "Longitude": -83.8,
        "Description": "A small frog species capable of shifting its skin color from green to reddish-brown.",
        "Keywords": "frog amphibian leaf frog central america"
    },
    {
        "Animal": "Galapagos Giant Tortoise",
        "Region": "Galapagos Islands",
        "Status": "Vulnerable",
        "Latitude": -0.8,
        "Longitude": -91.1,
        "Description": "Massive tortoises known for long lifespans exceeding 100 years.",
        "Keywords": "tortoise giant tortoise reptile galapagos"
    },
    {
        "Animal": "Iberian Lynx",
        "Region": "Spain / Portugal",
        "Status": "Vulnerable",
        "Latitude": 38.0,
        "Longitude": -4.0,
        "Description": "A wild cat species native to the Iberian Peninsula in southwestern Europe.",
        "Keywords": "lynx cat feline iberian lynx europe"
    },
    {
        "Animal": "Sunda Pangolin",
        "Region": "Southeast Asia",
        "Status": "Critically Endangered",
        "Latitude": 2.5,
        "Longitude": 102.5,
        "Description": "A scaly nocturnal mammal heavily targeted by wildlife trafficking.",
        "Keywords": "pangolin sunda pangolin mammal scales southeast asia"
    },
    {
        "Animal": "Komodo Dragon",
        "Region": "Indonesia",
        "Status": "Endangered",
        "Latitude": -8.6,
        "Longitude": 119.5,
        "Description": "The largest living lizard species on Earth, native to Indonesian islands.",
        "Keywords": "komodo dragon lizard reptile giant lizard indonesia"
    },
    {
        "Animal": "African Wild Dog",
        "Region": "Sub-Saharan Africa",
        "Status": "Endangered",
        "Latitude": -18.0,
        "Longitude": 25.0,
        "Description": "A highly social canine known for its unique patchy fur pattern and endurance hunting.",
        "Keywords": "wild dog canine painted dog africa"
    },
    {
        "Animal": "Flatback Sea Turtle",
        "Region": "Australia",
        "Status": "Data Deficient",
        "Latitude": -12.5,
        "Longitude": 130.8,
        "Description": "A sea turtle endemic to the continental shelf of northern Australia.",
        "Keywords": "turtle sea turtle flatback reptile australia"
    },
    {
        "Animal": "Ganges River Dolphin",
        "Region": "India / Nepal",
        "Status": "Endangered",
        "Latitude": 25.3,
        "Longitude": 83.0,
        "Description": "A freshwater dolphin species living in the muddy rivers of South Asia.",
        "Keywords": "dolphin river dolphin freshwater dolphin ganges india"
    },
    {
        "Animal": "Fossa",
        "Region": "Madagascar",
        "Status": "Vulnerable",
        "Latitude": -19.0,
        "Longitude": 47.0,
        "Description": "A slender cat-like carnivorous mammal unique to Madagascar.",
        "Keywords": "fossa carnivore predator madagascar"
    },
    {
        "Animal": "Platypus",
        "Region": "Australia",
        "Status": "Near Threatened",
        "Latitude": -35.3,
        "Longitude": 149.1,
        "Description": "An egg-laying semi-aquatic mammal native to eastern Australia.",
        "Keywords": "platypus monotreme duckbill mammal australia"
    },
    {
        "Animal": "Polar Bear",
        "Region": "Arctic Ocean",
        "Status": "Vulnerable",
        "Latitude": 75.0,
        "Longitude": -40.0,
        "Description": "A hypercarnivorous bear whose native range lies largely within the Arctic Circle.",
        "Keywords": "polar bear bear arctic polar mammal"
    },
    {
        "Animal": "Chinchilla",
        "Region": "Chile",
        "Status": "Endangered",
        "Latitude": -31.5,
        "Longitude": -71.2,
        "Description": "Small rodents famous for having the densest fur of all land mammals.",
        "Keywords": "chinchilla rodent fur chile south america"
    },
    {
        "Animal": "Pygmy Hippopotamus",
        "Region": "West Africa",
        "Status": "Endangered",
        "Latitude": 6.3,
        "Longitude": -10.8,
        "Description": "A small reclusive hippopotamus native to the forests and swamps of West Africa.",
        "Keywords": "hippo pygmy hippo mammal west africa"
    }
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
                if verify_user(login_username, login_password):
                    st.session_state.logged_in = True
                    st.session_state.username = login_username
                    st.rerun()
                else:
                    st.error("Incorrect username or password. Please try again, or sign up if you don't have an account yet.")
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
                account_created = create_user(username, email, phone, password)
                if account_created:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.phone = phone
                    st.rerun()
                else:
                    st.error("That username is already taken. Please choose a different username, or log in instead.")

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
    # Sidebar Navigation Header
    st.sidebar.title("☰ Navigation")
    
    # Profile photo & Edit Profile button placed next to each other
    sb_col1, sb_col2 = st.sidebar.columns([1, 1.3])

    with sb_col1:
        display_image = st.session_state.profile_pic if st.session_state.profile_pic else DEFAULT_AVATAR
        st.image(display_image, width=70)

    with sb_col2:
        st.write(f"**{st.session_state.username}**")
        if st.button("✏️ Edit Profile", key="sb_edit_profile"):
            st.session_state.page = "👤 Profile"
            st.session_state.editing_profile = True
            st.rerun()

    st.sidebar.markdown("---")

    # Logout button opens Pop-up Modal
    if st.sidebar.button("🚪 Log Out"):
        st.session_state.show_logout_dialog = True
        st.rerun()

    # -----------------------------
    # Horizontal Top Navigation
    # -----------------------------
    categories = [
        "🏠 Home",
        "🌎 Overview",
        "📚 Endangered Animal Library",
        "🤝 What You Can Do To Help",
        "🛍️ Merch Shop",
        "⚙️ Settings",
    ]

    current_index = categories.index(st.session_state.page) if st.session_state.page in categories else 0

    def set_nav_page():
        st.session_state.page = st.session_state.nav_radio

    selected_category = st.radio(
        "Go to",
        categories,
        index=current_index,
        key="nav_radio",
        on_change=set_nav_page,
        horizontal=True,
        label_visibility="collapsed",
    )

    st.markdown("---")

    page = st.session_state.page

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
        st.caption("💡 Click a green circle on the map to see that animal's photo and donate directly to help it.")

        if not filtered_df.empty:
            view_state = pdk.ViewState(
                latitude=float(filtered_df["Latitude"].mean()),
                longitude=float(filtered_df["Longitude"].mean()),
                zoom=1,
                pitch=0,
            )

            layer = pdk.Layer(
                "ScatterplotLayer",
                id="animal-layer",
                data=filtered_df,
                get_position='[Longitude, Latitude]',
                get_radius=250000,
                get_fill_color='[34, 139, 34, 180]',
                pickable=True,
                auto_highlight=True,
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

            # If the user asked to clear their map selection, reset the
            # chart's selection state before it's instantiated below.
            if st.session_state._clear_map_selection:
                if "animal_map" in st.session_state:
                    del st.session_state["animal_map"]
                st.session_state._clear_map_selection = False
                st.session_state.donation_target = GENERAL_FUND_LABEL

            map_event = st.pydeck_chart(
                deck,
                on_select="rerun",
                selection_mode="single-object",
                key="animal_map",
            )

            # --- Handle a clicked animal ---
            selected_animal_row = None
            if map_event and map_event.selection:
                selected_objects = map_event.selection.get("objects", {}).get("animal-layer", [])
                if selected_objects:
                    clicked_name = selected_objects[0].get("Animal")
                    match = df[df["Animal"] == clicked_name]
                    if not match.empty:
                        selected_animal_row = match.iloc[0]
                        st.session_state.donation_target = clicked_name

            # --- Selected Animal Card (correct photo tied to that exact animal) ---
            if selected_animal_row is not None:
                st.markdown("### 🐾 Selected Animal")
                card_col1, card_col2 = st.columns([1, 2])

                with card_col1:
                    photo_url = get_animal_photo_url(selected_animal_row["Animal"])
                    st.image(photo_url, use_container_width=True, caption=selected_animal_row["Animal"])

                with card_col2:
                    st.subheader(selected_animal_row["Animal"])
                    st.write(f"**Region:** {selected_animal_row['Region']}")
                    st.write(f"**Status:** {selected_animal_row['Status']}")
                    st.write(selected_animal_row["Description"])
                    st.info(f"💚 Your donation below will go toward helping the **{selected_animal_row['Animal']}**.")

                    if st.button("✖️ Clear Selection & Donate Generally"):
                        st.session_state._clear_map_selection = True
                        st.rerun()

        # --- DONATION & GOAL PROGRESS SECTION ---
        st.markdown("---")
        st.header("💚 Support & Goal Progress")

        # Active reward goal tier lookup
        current_tier = next((t for t in GOAL_TIERS if t["goal"] == st.session_state.current_goal), None)
        
        if current_tier:
            reward_title = current_tier["reward"]
            target_goal = current_tier["goal"]
            progress_pct = min(st.session_state.total_donated / target_goal, 1.0)

            # Circular Progress Ring & Milestone Display
            st.markdown(f"""
            <div style="background-color: #f0f7f4; border: 2px solid #2e7d32; border-radius: 12px; padding: 20px; text-align: center; margin-bottom: 25px;">
                <h3 style="color: #2e7d32; margin-bottom: 5px;">🎯 Next Reward Goal: ${target_goal}</h3>
                <h4 style="color: #1b5e20; margin-top: 0px;">Reward: {reward_title}</h4>
                <div style="font-size: 20px; font-weight: bold; margin: 15px 0; color: #333;">
                    Total Donated: <span style="color: #2e7d32;">${st.session_state.total_donated}</span> / ${target_goal}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Animated blue-green gradient progress bar tracking goal
            gradient_progress_bar(progress_pct)

            # Goal met & Claim Reward button action
            if st.session_state.total_donated >= target_goal:
                st.balloons()
                trigger_confetti()
                st.success(f"🎉 **Goal Completed!** You unlocked: **{reward_title}**!")
                
                if st.button("🎁 Claim Reward & Unlock Next Goal"):
                    st.session_state.claimed_rewards.append(reward_title)
                    
                    # Scale goal to next tier
                    if target_goal == 100:
                        st.session_state.current_goal = 500
                    elif target_goal == 500:
                        st.session_state.current_goal = 1000
                    elif target_goal == 1000:
                        st.session_state.current_goal = 5000
                    
                    trigger_confetti()
                    st.success("Reward Claimed! Your goal has leveled up!")
                    st.rerun()
        else:
            # All milestones achieved state
            st.balloons()
            trigger_confetti()
            st.markdown("""
            <div style="background-color: #fff8e1; border: 2px solid #ffa000; border-radius: 12px; padding: 20px; text-align: center; margin-bottom: 25px;">
                <h3 style="color: #f57f17;">🏆 Ultimate Wildlife Champion!</h3>
                <p style="font-size: 16px;">You have beaten all donation milestones ($5,000 max tier)! Thank you for your incredible impact on wildlife conservation.</p>
            </div>
            """, unsafe_allow_html=True)
            gradient_progress_bar(1.0)

        # Claimed Rewards Summary Box
        if st.session_state.claimed_rewards:
            st.markdown("**🏅 Claimed Rewards:** " + ", ".join(st.session_state.claimed_rewards))

        st.markdown("### 💳 Make a Donation")

        if st.session_state.donation_target != GENERAL_FUND_LABEL:
            st.caption(f"You're currently donating to help the **{st.session_state.donation_target}**. Click a different animal on the map, or use 'Clear Selection' above, to change this.")
        else:
            st.caption("Donating to the general conservation fund. Click an animal on the map above to direct your donation to that specific animal.")

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
                if "Gift Card" in st.session_state.payment_method and not gift_code:
                    st.error("Please enter your gift card code.")
                elif "Gift Card" not in st.session_state.payment_method and not (card_number and card_name and expiry and cvv):
                    st.error("Please complete all payment information.")
                else:
                    st.session_state.total_donated += donation
                    trigger_confetti()
                    if st.session_state.donation_target != GENERAL_FUND_LABEL:
                        st.success(f"🎉 Thank you for donating ${donation} to help the {st.session_state.donation_target}, using {st.session_state.payment_method}!")
                    else:
                        st.success(f"🎉 Thank you for donating ${donation} using {st.session_state.payment_method}!")
                    st.rerun()

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
    # MERCH SHOP PAGE
    # -----------------------------------
    elif page == "🛍️ Merch Shop":
        st.title("🛍️ Merch Shop")
        st.write("Every purchase helps fund conservation efforts. Shop our wildlife-inspired merchandise below!")

        if "merch_cart_total" not in st.session_state:
            st.session_state.merch_cart_total = 0

        products = [
            {
                "name": "🐾 Wildlife Advocators T-Shirt",
                "price": 25,
                "image": "https://placehold.co/300x300?text=T-Shirt",
                "description": "Soft cotton tee featuring our signature paw logo.",
            },
            {
                "name": "🧥 Conservation Hoodie",
                "price": 45,
                "image": "https://placehold.co/300x300?text=Hoodie",
                "description": "Cozy fleece hoodie, perfect for a chilly day out in nature.",
            },
            {
                "name": "🔑 Endangered Species Keychain",
                "price": 10,
                "image": "https://placehold.co/300x300?text=Keychain",
                "description": "A mini enamel keychain featuring your favorite endangered animal.",
            },
            {
                "name": "👜 Canvas Tote Bag",
                "price": 18,
                "image": "https://placehold.co/300x300?text=Tote+Bag",
                "description": "Reusable canvas tote printed with our 'Voice the Voiceless' design.",
            },
            {
                "name": "☕ Wildlife Mug",
                "price": 15,
                "image": "https://placehold.co/300x300?text=Mug",
                "description": "Ceramic mug featuring illustrations of endangered species.",
            },
            {
                "name": "🧢 Snapback Cap",
                "price": 22,
                "image": "https://placehold.co/300x300?text=Cap",
                "description": "Adjustable snapback cap with embroidered logo.",
            },
        ]

        shop_col1, shop_col2, shop_col3 = st.columns(3)
        shop_columns = [shop_col1, shop_col2, shop_col3]

        for idx, product in enumerate(products):
            with shop_columns[idx % 3]:
                st.image(product["image"], use_container_width=True)
                st.subheader(product["name"])
                st.write(product["description"])
                st.markdown(f"**${product['price']}**")
                if st.button(f"🛒 Buy Now", key=f"buy_{idx}"):
                    st.session_state.merch_cart_total += product["price"]
                    trigger_confetti()
                    st.success(f"🎉 Added **{product['name']}** to your order!")
                st.markdown("---")

        if st.session_state.merch_cart_total > 0:
            st.markdown("### 🧾 Order Summary")
            st.info(f"Current order total: **${st.session_state.merch_cart_total}**")

            st.subheader("Choose a Payment Method")

            mcol1, mcol2, mcol3, mcol4 = st.columns(4)

            with mcol1:
                if st.button("💳 Visa", use_container_width=True, key="merch_visa"):
                    st.session_state.payment_method = "Visa"

            with mcol2:
                if st.button("💳 Mastercard", use_container_width=True, key="merch_mc"):
                    st.session_state.payment_method = "Mastercard"

            with mcol3:
                if st.button("💳 American Express", use_container_width=True, key="merch_amex"):
                    st.session_state.payment_method = "American Express"

            with mcol4:
                if st.button("💳 Chase", use_container_width=True, key="merch_chase"):
                    st.session_state.payment_method = "Chase Credit Card"

            mcol5, mcol6 = st.columns(2)

            with mcol5:
                if st.button("🎁 Visa Gift Card", use_container_width=True, key="merch_visa_gift"):
                    st.session_state.payment_method = "Visa Gift Card"

            with mcol6:
                if st.button("🎁 Mastercard Gift Card", use_container_width=True, key="merch_mc_gift"):
                    st.session_state.payment_method = "Mastercard Gift Card"

            if st.session_state.payment_method:
                st.markdown("---")
                st.subheader(f"Payment - {st.session_state.payment_method}")

                if "Gift Card" in st.session_state.payment_method:
                    merch_gift_code = st.text_input("Gift Card Code", key="merch_gift_code")
                else:
                    merch_card_number = st.text_input("Card Number", key="merch_card_number")
                    merch_card_name = st.text_input("Name on Card", key="merch_card_name")
                    merch_expiry = st.text_input("Expiration Date (MM/YY)", key="merch_expiry")
                    merch_cvv = st.text_input("CVV", type="password", key="merch_cvv")

                if st.button("Complete Purchase", key="merch_complete_purchase"):
                    if "Gift Card" in st.session_state.payment_method and not merch_gift_code:
                        st.error("Please enter your gift card code.")
                    elif "Gift Card" not in st.session_state.payment_method and not (merch_card_number and merch_card_name and merch_expiry and merch_cvv):
                        st.error("Please complete all payment information.")
                    else:
                        st.balloons()
                        trigger_confetti()
                        st.success(f"🎉 Thank you for your order of ${st.session_state.merch_cart_total}, paid with {st.session_state.payment_method}! Your merch will ship soon.")
                        st.session_state.merch_cart_total = 0
                        st.rerun()

    # -----------------------------------
    # PROFILE PAGE (EDIT / VIEW)
    # -----------------------------------
    elif page == "👤 Profile":
        st.title("👤 User Profile")

        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 3])
        with col_btn1:
            if st.button("🏠 Back to Home"):
                st.session_state.page = "🏠 Home"
                st.session_state.editing_profile = False
                st.rerun()

        with col_btn2:
            if st.button("🔄 Switch Account"):
                st.session_state.show_logout_dialog = True
                st.rerun()

        with col_btn3:
            if st.button("✏️ Toggle Edit Mode"):
                st.session_state.editing_profile = not st.session_state.editing_profile

        # Expanded Edit Profile Inputs
        if st.session_state.editing_profile:
            st.markdown("---")
            st.subheader("✏️ Edit Profile Information")

            # Upload Image File
            uploaded_photo = st.file_uploader("Upload Profile Picture", type=["png", "jpg", "jpeg"])

            # Name Edit (Disabled for Guest)
            if st.session_state.username == "Guest":
                st.text_input("Username", value="Guest", disabled=True, help="Guest accounts cannot change their username.")
                new_name = "Guest"
            else:
                new_name = st.text_input("Username", value=st.session_state.username)

            # Description / Bio
            new_bio = st.text_area("Description / Bio", value=st.session_state.bio)

            # Phone Number
            new_phone = st.text_input("Phone Number (Optional)", value=st.session_state.phone)

            col_save1, col_save2 = st.columns([1, 4])
            with col_save1:
                if st.button("💾 Save Changes"):
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

        # User Profile Display (Clear, medium-large photo size)
        col_img, col_info = st.columns([1, 1.8])

        with col_img:
            main_profile_img = st.session_state.profile_pic if st.session_state.profile_pic else DEFAULT_AVATAR
            st.image(main_profile_img, width=320)

        with col_info:
            st.subheader(f"Username: {st.session_state.username}")
            st.write(f"**Bio / Description:**\n{st.session_state.bio}")
            st.write(f"**Phone Number:** {st.session_state.phone if st.session_state.phone else 'Not provided'}")
            st.write(f"**Total Impact Donated:** ${st.session_state.total_donated}")

    # -----------------------------------
    # SETTINGS PAGE (Feedback & Bug Report)
    # -----------------------------------
    elif page == "⚙️ Settings":
        st.title("⚙️ Settings & Support")
        st.write("We value your feedback and bug reports to make Animal Advocators better!")

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