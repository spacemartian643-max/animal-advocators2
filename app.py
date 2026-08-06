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

# --- Language Preference State ---
if "language" not in st.session_state:
    st.session_state.language = "English"

GOAL_TIERS = [
    {"goal": 100, "reward": "🔑 Free Keychain"},
    {"goal": 500, "reward": "👕 Free T-Shirt"},
    {"goal": 1000, "reward": "🏷️ Special Merch Discount"},
    {"goal": 5000, "reward": "🎟️ VIP Tour: Visit How We Help Animals!"},
]

# =========================================================================
# TRANSLATION LAYER (ADDED)
# -------------------------------------------------------------------------
# This dictionary + helper function let the app display UI text in the
# language the user picked on the Settings page. Nothing about the app's
# existing logic, state, keys, or data was changed — this only adds a
# lookup used to choose which string gets displayed.
# =========================================================================
TRANSLATIONS = {
    "English": {
        "nav_home": "🏠 Home",
        "nav_overview": "🌎 Overview",
        "nav_library": "📚 Endangered Animal Library",
        "nav_help": "🤝 What You Can Do To Help",
        "nav_shop": "🛍️ Merch Shop",
        "nav_settings": "⚙️ Settings",

        "sidebar_nav_header": "☰ Navigation",
        "edit_profile_btn": "✏️ Edit Profile",
        "logout_btn": "🚪 Log Out",
        "logout_modal_title": "⚠️ Logout Confirmation",
        "logout_modal_text": "Are you sure you want to log out? Everything you have done will not change.",
        "close_btn": "Close",
        "yes_btn": "Yes",

        "app_title": "🌿 Animal Advocators",
        "app_tagline": "Voice the Voiceless",
        "login_intro": "Please log in, create an account, or continue as a guest.",
        "tab_login": "🔑 Log In",
        "tab_signup": "📝 Sign Up",
        "username_label": "Username",
        "password_label": "Password",
        "login_btn": "Log In",
        "login_error": "Incorrect username or password. Please try again, or sign up if you don't have an account yet.",
        "login_missing_error": "Please enter both username and password.",
        "create_username_label": "Create Username",
        "email_label": "Email Address",
        "phone_optional_label": "Phone Number (Optional)",
        "create_password_label": "Create Password",
        "confirm_password_label": "Confirm Password",
        "create_account_btn": "Create Account",
        "signup_missing_error": "Please complete all required fields.",
        "passwords_mismatch_error": "Passwords do not match.",
        "username_taken_error": "That username is already taken. Please choose a different username, or log in instead.",
        "no_account_prompt": "Don't want to make an account?",
        "continue_guest_btn": "Continue as Guest",

        "welcome_message": "Welcome, {name}!",
        "home_intro": "Animal Advocators is dedicated to protecting endangered wildlife around the world. Use the search bar below to find specific animals or regions, explore the map, or support wildlife through donations.",
        "home_search_label": "🔎 Search for an endangered animal or region:",
        "results_for": "### 🎯 Results for '{query}'",
        "no_animals_found": "No animals were found matching your search.",
        "map_header": "🗺️ Endangered Animal Map",
        "map_caption": "💡 Click a green circle on the map to see that animal's photo and donate directly to help it.",
        "selected_animal_header": "### 🐾 Selected Animal",
        "region_label": "**Region:**",
        "status_label": "**Status:**",
        "donation_note": "💚 Your donation below will go toward helping the **{animal}**.",
        "clear_selection_btn": "✖️ Clear Selection & Donate Generally",

        "support_header": "💚 Support & Goal Progress",
        "next_goal_title": "🎯 Next Reward Goal: ${goal}",
        "reward_label_title": "Reward: {reward}",
        "total_donated_line": "Total Donated: <span style=\"color: #2e7d32;\">${total}</span> / ${goal}",
        "goal_completed": "🎉 **Goal Completed!** You unlocked: **{reward}**!",
        "claim_reward_btn": "🎁 Claim Reward & Unlock Next Goal",
        "reward_claimed": "Reward Claimed! Your goal has leveled up!",
        "ultimate_champion_title": "🏆 Ultimate Wildlife Champion!",
        "ultimate_champion_desc": "You have beaten all donation milestones ($5,000 max tier)! Thank you for your incredible impact on wildlife conservation.",
        "claimed_rewards_label": "**🏅 Claimed Rewards:** ",

        "make_donation_header": "### 💳 Make a Donation",
        "donating_to_animal_caption": "You're currently donating to help the **{animal}**. Click a different animal on the map, or use 'Clear Selection' above, to change this.",
        "donating_general_caption": "Donating to the general conservation fund. Click an animal on the map above to direct your donation to that specific animal.",
        "donation_slider_label": "Choose a donation amount ($)",
        "choose_payment_header": "Choose a Payment Method",
        "payment_header": "Payment - {method}",
        "gift_card_code_label": "Gift Card Code",
        "card_number_label": "Card Number",
        "name_on_card_label": "Name on Card",
        "expiry_label": "Expiration Date (MM/YY)",
        "cvv_label": "CVV",
        "complete_donation_btn": "Complete Donation",
        "missing_gift_code_error": "Please enter your gift card code.",
        "missing_payment_info_error": "Please complete all payment information.",
        "donation_thanks_animal": "🎉 Thank you for donating ${amount} to help the {animal}, using {method}!",
        "donation_thanks_general": "🎉 Thank you for donating ${amount} using {method}!",

        "overview_title": "🌎 Overview",
        "overview_mission_header": "### 🎯 Our Mission",
        "overview_mission_text": "**Animal Advocators** raises awareness for endangered animals and supports global conservation efforts. We provide tools for education, mapping, and direct financial contributions to preserve our planet's bio-diversity.",
        "overview_what_header": "### 🌿 What We Do",
        "overview_educate": "- **Educate:** Provide accurate data and conservation statuses for vulnerable species.",
        "overview_visualize": "- **Visualize:** Map habitats globally so users can see where conservation focus is needed most.",
        "overview_action": "- **Action:** Facilitate direct support to fund sanctuary protections, anti-poaching initiatives, and habitat restoration.",

        "library_title": "📚 Endangered Animal Library",
        "library_search_label": "🔎 Search for an endangered animal or region:",
        "library_no_results": "No animals were found.",

        "help_title": "🤝 What You Can Do To Help",
        "help_intro": "Every action counts when it comes to preserving wildlife. Here are meaningful ways you can help protect endangered species:",
        "help_1_title": "1. 📢 Spread Awareness",
        "help_1_desc": "Share information about endangered animals with friends, family, and social media networks. Educating others is the first step toward conservation.",
        "help_2_title": "2. 🛍️ Make Sustainable Choices",
        "help_2_desc": "Avoid products made from endangered species, reduce single-use plastics that harm marine life, and support eco-friendly wildlife tourism.",
        "help_3_title": "3. 💚 Donate & Support",
        "help_3_desc": "Contributions directly fund habitat protection, anti-poaching ranger patrols, and wildlife rehabilitation centers across the globe.",
        "help_4_title": "4. 🌿 Protect Natural Habitats",
        "help_4_desc": "Plant native plants, reduce waste, and support local wildlife conservation projects and nature preserves in your community.",
        "help_5_title": "5. 📜 Advocate for Policy Change",
        "help_5_desc": "Support wildlife protection legislation and vote for policies that protect vulnerable natural ecosystems and combat climate change.",
        "help_6_title": "6. 📚 Stay Educated",
        "help_6_desc": "Use our **Endangered Animal Library** to keep updated on species status and learn more about global environmental challenges.",

        "shop_title": "🛍️ Merch Shop",
        "shop_intro": "Every purchase helps fund conservation efforts. Shop our wildlife-inspired merchandise below!",
        "buy_now_btn": "🛒 Buy Now",
        "added_to_order": "🎉 Added **{product}** to your order!",
        "order_summary_header": "### 🧾 Order Summary",
        "order_total_label": "Current order total: **${total}**",
        "complete_purchase_btn": "Complete Purchase",
        "order_thanks": "🎉 Thank you for your order of ${total}, paid with {method}! Your merch will ship soon.",

        "profile_title": "👤 User Profile",
        "back_home_btn": "🏠 Back to Home",
        "switch_account_btn": "🔄 Switch Account",
        "toggle_edit_btn": "✏️ Toggle Edit Mode",
        "edit_profile_header": "✏️ Edit Profile Information",
        "upload_photo_label": "Upload Profile Picture",
        "guest_username_help": "Guest accounts cannot change their username.",
        "bio_label": "Description / Bio",
        "phone_label": "Phone Number (Optional)",
        "save_changes_btn": "💾 Save Changes",
        "profile_updated": "✅ Profile updated successfully!",
        "username_display": "Username: {name}",
        "bio_display": "**Bio / Description:**\n{bio}",
        "phone_display": "**Phone Number:** {phone}",
        "phone_not_provided": "Not provided",
        "total_impact_label": "**Total Impact Donated:** ${total}",

        "settings_title": "⚙️ Settings & Support",
        "settings_intro": "We value your feedback and bug reports to make Animal Advocators better!",
        "tab_feedback": "💬 Send Feedback",
        "tab_bug": "🐛 Report a Bug or Error",
        "tab_language": "🌐 Change Languages",

        "feedback_header": "Share Your Thoughts",
        "feedback_intro": "How can we improve your experience with Animal Advocators?",
        "rating_label": "How would you rate your overall experience?",
        "feedback_label": "Your Feedback or Suggestions:",
        "feedback_placeholder": "Type your feedback here...",
        "submit_feedback_btn": "Submit Feedback",
        "feedback_thanks": "🎉 Thank you! Your feedback has been sent to our team.",
        "feedback_error": "Please enter some text before submitting.",

        "bug_header": "Report an Issue",
        "bug_intro": "Found a bug or incorrect information? Let us know below.",
        "bug_category_label": "Issue Category:",
        "bug_title_label": "Brief Summary of the Issue:",
        "bug_title_placeholder": "e.g., Map dots not loading",
        "bug_details_label": "Detailed Description:",
        "bug_details_placeholder": "Please describe what happened and how to reproduce it...",
        "submit_bug_btn": "Submit Bug Report",
        "bug_thanks": "🚨 Bug report submitted! Thank you for helping us keep Animal Advocators running smoothly.",
        "bug_error": "Please complete both the summary and detailed description fields.",

        "language_header": "Change Language",
        "language_intro": "Select your preferred language for Animal Advocators.",
        "choose_language_label": "Choose a language:",
        "save_language_btn": "Save Language",
        "language_updated": "✅ Language updated to {language}!",

        "footer_text": "Animal Advocators • Helping Wild Animals Worldwide 🌍",
    },

    "Spanish": {
        "nav_home": "🏠 Inicio",
        "nav_overview": "🌎 Resumen",
        "nav_library": "📚 Biblioteca de Animales en Peligro",
        "nav_help": "🤝 Cómo Puedes Ayudar",
        "nav_shop": "🛍️ Tienda de Productos",
        "nav_settings": "⚙️ Configuración",

        "sidebar_nav_header": "☰ Navegación",
        "edit_profile_btn": "✏️ Editar Perfil",
        "logout_btn": "🚪 Cerrar Sesión",
        "logout_modal_title": "⚠️ Confirmar Cierre de Sesión",
        "logout_modal_text": "¿Seguro que deseas cerrar sesión? Todo lo que hayas hecho permanecerá sin cambios.",
        "close_btn": "Cerrar",
        "yes_btn": "Sí",

        "app_title": "🌿 Animal Advocators",
        "app_tagline": "La Voz de los Que No Tienen Voz",
        "login_intro": "Inicia sesión, crea una cuenta o continúa como invitado.",
        "tab_login": "🔑 Iniciar Sesión",
        "tab_signup": "📝 Registrarse",
        "username_label": "Nombre de Usuario",
        "password_label": "Contraseña",
        "login_btn": "Iniciar Sesión",
        "login_error": "Usuario o contraseña incorrectos. Inténtalo de nuevo, o regístrate si aún no tienes una cuenta.",
        "login_missing_error": "Por favor, introduce el usuario y la contraseña.",
        "create_username_label": "Crear Nombre de Usuario",
        "email_label": "Correo Electrónico",
        "phone_optional_label": "Número de Teléfono (Opcional)",
        "create_password_label": "Crear Contraseña",
        "confirm_password_label": "Confirmar Contraseña",
        "create_account_btn": "Crear Cuenta",
        "signup_missing_error": "Por favor, completa todos los campos requeridos.",
        "passwords_mismatch_error": "Las contraseñas no coinciden.",
        "username_taken_error": "Ese nombre de usuario ya está en uso. Elige otro nombre, o inicia sesión.",
        "no_account_prompt": "¿No quieres crear una cuenta?",
        "continue_guest_btn": "Continuar como Invitado",

        "welcome_message": "¡Bienvenido, {name}!",
        "home_intro": "Animal Advocators se dedica a proteger la vida silvestre en peligro de extinción alrededor del mundo. Usa la barra de búsqueda para encontrar animales o regiones específicas, explora el mapa o apoya a la fauna con donaciones.",
        "home_search_label": "🔎 Busca un animal en peligro o una región:",
        "results_for": "### 🎯 Resultados para '{query}'",
        "no_animals_found": "No se encontraron animales que coincidan con tu búsqueda.",
        "map_header": "🗺️ Mapa de Animales en Peligro",
        "map_caption": "💡 Haz clic en un círculo verde del mapa para ver la foto de ese animal y donar directamente para ayudarlo.",
        "selected_animal_header": "### 🐾 Animal Seleccionado",
        "region_label": "**Región:**",
        "status_label": "**Estado:**",
        "donation_note": "💚 Tu donación a continuación ayudará a **{animal}**.",
        "clear_selection_btn": "✖️ Quitar Selección y Donar en General",

        "support_header": "💚 Apoyo y Progreso de Metas",
        "next_goal_title": "🎯 Próxima Meta de Recompensa: ${goal}",
        "reward_label_title": "Recompensa: {reward}",
        "total_donated_line": "Total Donado: <span style=\"color: #2e7d32;\">${total}</span> / ${goal}",
        "goal_completed": "🎉 **¡Meta Completada!** Desbloqueaste: **{reward}**!",
        "claim_reward_btn": "🎁 Reclamar Recompensa y Desbloquear Siguiente Meta",
        "reward_claimed": "¡Recompensa reclamada! Tu meta ha subido de nivel.",
        "ultimate_champion_title": "🏆 ¡Campeón Definitivo de la Vida Silvestre!",
        "ultimate_champion_desc": "¡Has superado todas las metas de donación (nivel máximo de $5,000)! Gracias por tu increíble impacto en la conservación de la vida silvestre.",
        "claimed_rewards_label": "**🏅 Recompensas Reclamadas:** ",

        "make_donation_header": "### 💳 Hacer una Donación",
        "donating_to_animal_caption": "Actualmente estás donando para ayudar a **{animal}**. Haz clic en otro animal en el mapa, o usa 'Quitar Selección' arriba, para cambiar esto.",
        "donating_general_caption": "Donando al fondo general de conservación. Haz clic en un animal en el mapa de arriba para dirigir tu donación a ese animal específico.",
        "donation_slider_label": "Elige un monto de donación ($)",
        "choose_payment_header": "Elige un Método de Pago",
        "payment_header": "Pago - {method}",
        "gift_card_code_label": "Código de Tarjeta de Regalo",
        "card_number_label": "Número de Tarjeta",
        "name_on_card_label": "Nombre en la Tarjeta",
        "expiry_label": "Fecha de Vencimiento (MM/AA)",
        "cvv_label": "CVV",
        "complete_donation_btn": "Completar Donación",
        "missing_gift_code_error": "Por favor, introduce el código de tu tarjeta de regalo.",
        "missing_payment_info_error": "Por favor, completa toda la información de pago.",
        "donation_thanks_animal": "🎉 ¡Gracias por donar ${amount} para ayudar a {animal}, usando {method}!",
        "donation_thanks_general": "🎉 ¡Gracias por donar ${amount} usando {method}!",

        "overview_title": "🌎 Resumen",
        "overview_mission_header": "### 🎯 Nuestra Misión",
        "overview_mission_text": "**Animal Advocators** crea conciencia sobre los animales en peligro y apoya los esfuerzos de conservación globales. Ofrecemos herramientas para la educación, la cartografía y las contribuciones económicas directas para preservar la biodiversidad de nuestro planeta.",
        "overview_what_header": "### 🌿 Qué Hacemos",
        "overview_educate": "- **Educar:** Ofrecemos datos precisos y estados de conservación de especies vulnerables.",
        "overview_visualize": "- **Visualizar:** Mapeamos hábitats a nivel mundial para mostrar dónde se necesita más enfoque de conservación.",
        "overview_action": "- **Actuar:** Facilitamos apoyo directo para financiar protección de santuarios, iniciativas contra la caza furtiva y restauración de hábitats.",

        "library_title": "📚 Biblioteca de Animales en Peligro",
        "library_search_label": "🔎 Busca un animal en peligro o una región:",
        "library_no_results": "No se encontraron animales.",

        "help_title": "🤝 Cómo Puedes Ayudar",
        "help_intro": "Cada acción cuenta cuando se trata de preservar la vida silvestre. Aquí tienes formas significativas de ayudar a proteger especies en peligro:",
        "help_1_title": "1. 📢 Difunde Conciencia",
        "help_1_desc": "Comparte información sobre animales en peligro con amigos, familiares y redes sociales. Educar a otros es el primer paso hacia la conservación.",
        "help_2_title": "2. 🛍️ Elige Opciones Sostenibles",
        "help_2_desc": "Evita productos hechos de especies en peligro, reduce los plásticos de un solo uso que dañan la vida marina y apoya el turismo de fauna respetuoso con el medio ambiente.",
        "help_3_title": "3. 💚 Dona y Apoya",
        "help_3_desc": "Las contribuciones financian directamente la protección de hábitats, las patrullas contra la caza furtiva y los centros de rehabilitación de fauna en todo el mundo.",
        "help_4_title": "4. 🌿 Protege los Hábitats Naturales",
        "help_4_desc": "Planta especies nativas, reduce los residuos y apoya proyectos locales de conservación y reservas naturales en tu comunidad.",
        "help_5_title": "5. 📜 Aboga por Cambios de Política",
        "help_5_desc": "Apoya la legislación de protección de la vida silvestre y vota por políticas que protejan los ecosistemas naturales vulnerables y combatan el cambio climático.",
        "help_6_title": "6. 📚 Mantente Informado",
        "help_6_desc": "Usa nuestra **Biblioteca de Animales en Peligro** para mantenerte al día sobre el estado de las especies y aprender más sobre los desafíos ambientales globales.",

        "shop_title": "🛍️ Tienda de Productos",
        "shop_intro": "Cada compra ayuda a financiar los esfuerzos de conservación. ¡Compra nuestra mercancía inspirada en la vida silvestre!",
        "buy_now_btn": "🛒 Comprar Ahora",
        "added_to_order": "🎉 ¡Se añadió **{product}** a tu pedido!",
        "order_summary_header": "### 🧾 Resumen del Pedido",
        "order_total_label": "Total actual del pedido: **${total}**",
        "complete_purchase_btn": "Completar Compra",
        "order_thanks": "🎉 ¡Gracias por tu pedido de ${total}, pagado con {method}! Tu mercancía se enviará pronto.",

        "profile_title": "👤 Perfil de Usuario",
        "back_home_btn": "🏠 Volver al Inicio",
        "switch_account_btn": "🔄 Cambiar Cuenta",
        "toggle_edit_btn": "✏️ Alternar Modo de Edición",
        "edit_profile_header": "✏️ Editar Información del Perfil",
        "upload_photo_label": "Subir Foto de Perfil",
        "guest_username_help": "Las cuentas de invitado no pueden cambiar su nombre de usuario.",
        "bio_label": "Descripción / Biografía",
        "phone_label": "Número de Teléfono (Opcional)",
        "save_changes_btn": "💾 Guardar Cambios",
        "profile_updated": "✅ ¡Perfil actualizado con éxito!",
        "username_display": "Usuario: {name}",
        "bio_display": "**Biografía / Descripción:**\n{bio}",
        "phone_display": "**Número de Teléfono:** {phone}",
        "phone_not_provided": "No proporcionado",
        "total_impact_label": "**Impacto Total Donado:** ${total}",

        "settings_title": "⚙️ Configuración y Soporte",
        "settings_intro": "¡Valoramos tus comentarios e informes de errores para mejorar Animal Advocators!",
        "tab_feedback": "💬 Enviar Comentarios",
        "tab_bug": "🐛 Reportar un Error",
        "tab_language": "🌐 Cambiar Idioma",

        "feedback_header": "Comparte Tu Opinión",
        "feedback_intro": "¿Cómo podemos mejorar tu experiencia con Animal Advocators?",
        "rating_label": "¿Cómo calificarías tu experiencia general?",
        "feedback_label": "Tus Comentarios o Sugerencias:",
        "feedback_placeholder": "Escribe tus comentarios aquí...",
        "submit_feedback_btn": "Enviar Comentarios",
        "feedback_thanks": "🎉 ¡Gracias! Tus comentarios han sido enviados a nuestro equipo.",
        "feedback_error": "Por favor, escribe algo antes de enviar.",

        "bug_header": "Reportar un Problema",
        "bug_intro": "¿Encontraste un error o información incorrecta? Cuéntanoslo a continuación.",
        "bug_category_label": "Categoría del Problema:",
        "bug_title_label": "Resumen Breve del Problema:",
        "bug_title_placeholder": "ej., los puntos del mapa no cargan",
        "bug_details_label": "Descripción Detallada:",
        "bug_details_placeholder": "Describe qué sucedió y cómo reproducirlo...",
        "submit_bug_btn": "Enviar Reporte de Error",
        "bug_thanks": "🚨 ¡Reporte de error enviado! Gracias por ayudarnos a mantener Animal Advocators funcionando sin problemas.",
        "bug_error": "Por favor, completa el resumen y la descripción detallada.",

        "language_header": "Cambiar Idioma",
        "language_intro": "Selecciona tu idioma preferido para Animal Advocators.",
        "choose_language_label": "Elige un idioma:",
        "save_language_btn": "Guardar Idioma",
        "language_updated": "✅ ¡Idioma actualizado a {language}!",

        "footer_text": "Animal Advocators • Ayudando a los Animales Salvajes del Mundo 🌍",
    },

    "Russian": {
        "nav_home": "🏠 Главная",
        "nav_overview": "🌎 Обзор",
        "nav_library": "📚 Библиотека Исчезающих Видов",
        "nav_help": "🤝 Как Вы Можете Помочь",
        "nav_shop": "🛍️ Магазин Товаров",
        "nav_settings": "⚙️ Настройки",

        "sidebar_nav_header": "☰ Навигация",
        "edit_profile_btn": "✏️ Редактировать Профиль",
        "logout_btn": "🚪 Выйти",
        "logout_modal_title": "⚠️ Подтверждение Выхода",
        "logout_modal_text": "Вы уверены, что хотите выйти? Все сделанное вами останется без изменений.",
        "close_btn": "Закрыть",
        "yes_btn": "Да",

        "app_title": "🌿 Animal Advocators",
        "app_tagline": "Голос Безмолвных",
        "login_intro": "Пожалуйста, войдите, создайте учетную запись или продолжите как гость.",
        "tab_login": "🔑 Вход",
        "tab_signup": "📝 Регистрация",
        "username_label": "Имя Пользователя",
        "password_label": "Пароль",
        "login_btn": "Войти",
        "login_error": "Неверное имя пользователя или пароль. Попробуйте снова или зарегистрируйтесь, если у вас еще нет аккаунта.",
        "login_missing_error": "Пожалуйста, введите имя пользователя и пароль.",
        "create_username_label": "Придумайте Имя Пользователя",
        "email_label": "Электронная Почта",
        "phone_optional_label": "Номер Телефона (Необязательно)",
        "create_password_label": "Придумайте Пароль",
        "confirm_password_label": "Подтвердите Пароль",
        "create_account_btn": "Создать Аккаунт",
        "signup_missing_error": "Пожалуйста, заполните все обязательные поля.",
        "passwords_mismatch_error": "Пароли не совпадают.",
        "username_taken_error": "Это имя пользователя уже занято. Выберите другое имя или войдите в систему.",
        "no_account_prompt": "Не хотите создавать аккаунт?",
        "continue_guest_btn": "Продолжить как Гость",

        "welcome_message": "Добро пожаловать, {name}!",
        "home_intro": "Animal Advocators посвящен защите исчезающих диких животных по всему миру. Используйте строку поиска ниже, чтобы найти конкретных животных или регионы, изучите карту или поддержите дикую природу с помощью пожертвований.",
        "home_search_label": "🔎 Найдите исчезающее животное или регион:",
        "results_for": "### 🎯 Результаты для «{query}»",
        "no_animals_found": "По вашему запросу животные не найдены.",
        "map_header": "🗺️ Карта Исчезающих Видов",
        "map_caption": "💡 Нажмите на зеленый круг на карте, чтобы увидеть фото этого животного и пожертвовать напрямую в его поддержку.",
        "selected_animal_header": "### 🐾 Выбранное Животное",
        "region_label": "**Регион:**",
        "status_label": "**Статус:**",
        "donation_note": "💚 Ваше пожертвование ниже пойдет на помощь **{animal}**.",
        "clear_selection_btn": "✖️ Сбросить Выбор и Жертвовать в Общий Фонд",

        "support_header": "💚 Поддержка и Прогресс Цели",
        "next_goal_title": "🎯 Следующая Цель Награды: ${goal}",
        "reward_label_title": "Награда: {reward}",
        "total_donated_line": "Всего Пожертвовано: <span style=\"color: #2e7d32;\">${total}</span> / ${goal}",
        "goal_completed": "🎉 **Цель Достигнута!** Вы получили: **{reward}**!",
        "claim_reward_btn": "🎁 Получить Награду и Открыть Следующую Цель",
        "reward_claimed": "Награда получена! Ваша цель повышена!",
        "ultimate_champion_title": "🏆 Абсолютный Чемпион Дикой Природы!",
        "ultimate_champion_desc": "Вы достигли всех уровней пожертвований (максимальный уровень $5,000)! Спасибо за ваш невероятный вклад в охрану дикой природы.",
        "claimed_rewards_label": "**🏅 Полученные Награды:** ",

        "make_donation_header": "### 💳 Сделать Пожертвование",
        "donating_to_animal_caption": "Сейчас вы жертвуете в помощь **{animal}**. Нажмите на другое животное на карте или используйте «Сбросить Выбор» выше, чтобы изменить это.",
        "donating_general_caption": "Пожертвование в общий фонд охраны природы. Нажмите на животное на карте выше, чтобы направить пожертвование конкретно ему.",
        "donation_slider_label": "Выберите сумму пожертвования ($)",
        "choose_payment_header": "Выберите Способ Оплаты",
        "payment_header": "Оплата - {method}",
        "gift_card_code_label": "Код Подарочной Карты",
        "card_number_label": "Номер Карты",
        "name_on_card_label": "Имя на Карте",
        "expiry_label": "Срок Действия (ММ/ГГ)",
        "cvv_label": "CVV",
        "complete_donation_btn": "Завершить Пожертвование",
        "missing_gift_code_error": "Пожалуйста, введите код вашей подарочной карты.",
        "missing_payment_info_error": "Пожалуйста, заполните всю платежную информацию.",
        "donation_thanks_animal": "🎉 Спасибо за пожертвование ${amount} в помощь {animal}, с использованием {method}!",
        "donation_thanks_general": "🎉 Спасибо за пожертвование ${amount} с использованием {method}!",

        "overview_title": "🌎 Обзор",
        "overview_mission_header": "### 🎯 Наша Миссия",
        "overview_mission_text": "**Animal Advocators** повышает осведомленность об исчезающих животных и поддерживает глобальные усилия по охране природы. Мы предоставляем инструменты для образования, картографирования и прямых финансовых взносов для сохранения биоразнообразия нашей планеты.",
        "overview_what_header": "### 🌿 Что Мы Делаем",
        "overview_educate": "- **Просвещение:** Предоставляем точные данные и статусы охраны уязвимых видов.",
        "overview_visualize": "- **Визуализация:** Наносим на карту места обитания по всему миру, чтобы показать, где нужна помощь.",
        "overview_action": "- **Действие:** Обеспечиваем прямую поддержку для финансирования защиты заповедников, борьбы с браконьерством и восстановления мест обитания.",

        "library_title": "📚 Библиотека Исчезающих Видов",
        "library_search_label": "🔎 Найдите исчезающее животное или регион:",
        "library_no_results": "Животные не найдены.",

        "help_title": "🤝 Как Вы Можете Помочь",
        "help_intro": "Каждое действие имеет значение, когда речь идет о сохранении дикой природы. Вот значимые способы помочь защитить исчезающие виды:",
        "help_1_title": "1. 📢 Распространяйте Информацию",
        "help_1_desc": "Делитесь информацией об исчезающих животных с друзьями, семьей и в социальных сетях. Просвещение других — первый шаг к охране природы.",
        "help_2_title": "2. 🛍️ Делайте Экологичный Выбор",
        "help_2_desc": "Избегайте продуктов из исчезающих видов, сокращайте использование одноразового пластика, вредящего морской жизни, и поддерживайте экологичный туризм дикой природы.",
        "help_3_title": "3. 💚 Жертвуйте и Поддерживайте",
        "help_3_desc": "Пожертвования напрямую финансируют охрану мест обитания, патрули по борьбе с браконьерством и центры реабилитации диких животных по всему миру.",
        "help_4_title": "4. 🌿 Защищайте Природные Места Обитания",
        "help_4_desc": "Сажайте местные растения, сокращайте отходы и поддерживайте местные проекты по охране природы и заповедники в вашем сообществе.",
        "help_5_title": "5. 📜 Выступайте за Изменение Политики",
        "help_5_desc": "Поддерживайте законодательство по защите дикой природы и голосуйте за политику, защищающую уязвимые экосистемы и борющуюся с изменением климата.",
        "help_6_title": "6. 📚 Оставайтесь в Курсе",
        "help_6_desc": "Используйте нашу **Библиотеку Исчезающих Видов**, чтобы быть в курсе статуса видов и узнавать больше о глобальных экологических проблемах.",

        "shop_title": "🛍️ Магазин Товаров",
        "shop_intro": "Каждая покупка помогает финансировать усилия по охране природы. Купите нашу продукцию, вдохновленную дикой природой!",
        "buy_now_btn": "🛒 Купить Сейчас",
        "added_to_order": "🎉 **{product}** добавлен в ваш заказ!",
        "order_summary_header": "### 🧾 Сводка Заказа",
        "order_total_label": "Текущая сумма заказа: **${total}**",
        "complete_purchase_btn": "Завершить Покупку",
        "order_thanks": "🎉 Спасибо за ваш заказ на ${total}, оплаченный через {method}! Ваш товар скоро будет отправлен.",

        "profile_title": "👤 Профиль Пользователя",
        "back_home_btn": "🏠 На Главную",
        "switch_account_btn": "🔄 Сменить Аккаунт",
        "toggle_edit_btn": "✏️ Переключить Режим Редактирования",
        "edit_profile_header": "✏️ Редактировать Информацию Профиля",
        "upload_photo_label": "Загрузить Фото Профиля",
        "guest_username_help": "Гостевые аккаунты не могут изменить имя пользователя.",
        "bio_label": "Описание / Биография",
        "phone_label": "Номер Телефона (Необязательно)",
        "save_changes_btn": "💾 Сохранить Изменения",
        "profile_updated": "✅ Профиль успешно обновлен!",
        "username_display": "Имя пользователя: {name}",
        "bio_display": "**Биография / Описание:**\n{bio}",
        "phone_display": "**Номер Телефона:** {phone}",
        "phone_not_provided": "Не указан",
        "total_impact_label": "**Общий Вклад Пожертвований:** ${total}",

        "settings_title": "⚙️ Настройки и Поддержка",
        "settings_intro": "Мы ценим ваши отзывы и сообщения об ошибках, чтобы сделать Animal Advocators лучше!",
        "tab_feedback": "💬 Отправить Отзыв",
        "tab_bug": "🐛 Сообщить об Ошибке",
        "tab_language": "🌐 Сменить Язык",

        "feedback_header": "Поделитесь Своим Мнением",
        "feedback_intro": "Как мы можем улучшить ваш опыт использования Animal Advocators?",
        "rating_label": "Как бы вы оценили свой общий опыт?",
        "feedback_label": "Ваш Отзыв или Предложения:",
        "feedback_placeholder": "Введите свой отзыв здесь...",
        "submit_feedback_btn": "Отправить Отзыв",
        "feedback_thanks": "🎉 Спасибо! Ваш отзыв отправлен нашей команде.",
        "feedback_error": "Пожалуйста, введите текст перед отправкой.",

        "bug_header": "Сообщить о Проблеме",
        "bug_intro": "Нашли ошибку или неверную информацию? Сообщите нам об этом ниже.",
        "bug_category_label": "Категория Проблемы:",
        "bug_title_label": "Краткое Описание Проблемы:",
        "bug_title_placeholder": "например, точки на карте не загружаются",
        "bug_details_label": "Подробное Описание:",
        "bug_details_placeholder": "Опишите, что произошло и как это воспроизвести...",
        "submit_bug_btn": "Отправить Сообщение об Ошибке",
        "bug_thanks": "🚨 Сообщение об ошибке отправлено! Спасибо, что помогаете нам поддерживать Animal Advocators в рабочем состоянии.",
        "bug_error": "Пожалуйста, заполните и краткое, и подробное описание.",

        "language_header": "Сменить Язык",
        "language_intro": "Выберите предпочитаемый язык для Animal Advocators.",
        "choose_language_label": "Выберите язык:",
        "save_language_btn": "Сохранить Язык",
        "language_updated": "✅ Язык изменен на {language}!",

        "footer_text": "Animal Advocators • Помощь Диким Животным по Всему Миру 🌍",
    },

    "Italian": {
        "nav_home": "🏠 Home",
        "nav_overview": "🌎 Panoramica",
        "nav_library": "📚 Biblioteca degli Animali in Pericolo",
        "nav_help": "🤝 Come Puoi Aiutare",
        "nav_shop": "🛍️ Negozio di Merchandise",
        "nav_settings": "⚙️ Impostazioni",

        "sidebar_nav_header": "☰ Navigazione",
        "edit_profile_btn": "✏️ Modifica Profilo",
        "logout_btn": "🚪 Esci",
        "logout_modal_title": "⚠️ Conferma Disconnessione",
        "logout_modal_text": "Sei sicuro di voler uscire? Tutto ciò che hai fatto rimarrà invariato.",
        "close_btn": "Chiudi",
        "yes_btn": "Sì",

        "app_title": "🌿 Animal Advocators",
        "app_tagline": "La Voce di Chi Non Ha Voce",
        "login_intro": "Accedi, crea un account o continua come ospite.",
        "tab_login": "🔑 Accedi",
        "tab_signup": "📝 Registrati",
        "username_label": "Nome Utente",
        "password_label": "Password",
        "login_btn": "Accedi",
        "login_error": "Nome utente o password errati. Riprova, oppure registrati se non hai ancora un account.",
        "login_missing_error": "Inserisci sia il nome utente che la password.",
        "create_username_label": "Crea Nome Utente",
        "email_label": "Indirizzo Email",
        "phone_optional_label": "Numero di Telefono (Facoltativo)",
        "create_password_label": "Crea Password",
        "confirm_password_label": "Conferma Password",
        "create_account_btn": "Crea Account",
        "signup_missing_error": "Completa tutti i campi obbligatori.",
        "passwords_mismatch_error": "Le password non corrispondono.",
        "username_taken_error": "Questo nome utente è già in uso. Scegline un altro oppure accedi.",
        "no_account_prompt": "Non vuoi creare un account?",
        "continue_guest_btn": "Continua come Ospite",

        "welcome_message": "Benvenuto, {name}!",
        "home_intro": "Animal Advocators si dedica alla protezione della fauna selvatica in pericolo in tutto il mondo. Usa la barra di ricerca qui sotto per trovare animali o regioni specifiche, esplora la mappa o sostieni la fauna con donazioni.",
        "home_search_label": "🔎 Cerca un animale in pericolo o una regione:",
        "results_for": "### 🎯 Risultati per '{query}'",
        "no_animals_found": "Nessun animale trovato corrispondente alla tua ricerca.",
        "map_header": "🗺️ Mappa degli Animali in Pericolo",
        "map_caption": "💡 Clicca su un cerchio verde sulla mappa per vedere la foto di quell'animale e donare direttamente per aiutarlo.",
        "selected_animal_header": "### 🐾 Animale Selezionato",
        "region_label": "**Regione:**",
        "status_label": "**Stato:**",
        "donation_note": "💚 La tua donazione qui sotto aiuterà **{animal}**.",
        "clear_selection_btn": "✖️ Annulla Selezione e Dona in Generale",

        "support_header": "💚 Sostegno e Avanzamento Obiettivo",
        "next_goal_title": "🎯 Prossimo Obiettivo Premio: ${goal}",
        "reward_label_title": "Premio: {reward}",
        "total_donated_line": "Totale Donato: <span style=\"color: #2e7d32;\">${total}</span> / ${goal}",
        "goal_completed": "🎉 **Obiettivo Raggiunto!** Hai sbloccato: **{reward}**!",
        "claim_reward_btn": "🎁 Riscatta Premio e Sblocca Prossimo Obiettivo",
        "reward_claimed": "Premio riscattato! Il tuo obiettivo è salito di livello!",
        "ultimate_champion_title": "🏆 Campione Supremo della Fauna Selvatica!",
        "ultimate_champion_desc": "Hai superato tutti i traguardi di donazione (livello massimo $5.000)! Grazie per il tuo incredibile impatto sulla conservazione della fauna selvatica.",
        "claimed_rewards_label": "**🏅 Premi Riscattati:** ",

        "make_donation_header": "### 💳 Effettua una Donazione",
        "donating_to_animal_caption": "Stai attualmente donando per aiutare **{animal}**. Clicca su un altro animale sulla mappa, oppure usa 'Annulla Selezione' sopra, per cambiare.",
        "donating_general_caption": "Donazione al fondo generale di conservazione. Clicca su un animale sulla mappa sopra per indirizzare la tua donazione a quell'animale specifico.",
        "donation_slider_label": "Scegli un importo di donazione ($)",
        "choose_payment_header": "Scegli un Metodo di Pagamento",
        "payment_header": "Pagamento - {method}",
        "gift_card_code_label": "Codice Carta Regalo",
        "card_number_label": "Numero Carta",
        "name_on_card_label": "Nome sulla Carta",
        "expiry_label": "Data di Scadenza (MM/AA)",
        "cvv_label": "CVV",
        "complete_donation_btn": "Completa Donazione",
        "missing_gift_code_error": "Inserisci il codice della tua carta regalo.",
        "missing_payment_info_error": "Completa tutte le informazioni di pagamento.",
        "donation_thanks_animal": "🎉 Grazie per aver donato ${amount} per aiutare {animal}, usando {method}!",
        "donation_thanks_general": "🎉 Grazie per aver donato ${amount} usando {method}!",

        "overview_title": "🌎 Panoramica",
        "overview_mission_header": "### 🎯 La Nostra Missione",
        "overview_mission_text": "**Animal Advocators** sensibilizza sugli animali in pericolo e sostiene gli sforzi di conservazione globali. Offriamo strumenti per l'educazione, la mappatura e i contributi finanziari diretti per preservare la biodiversità del nostro pianeta.",
        "overview_what_header": "### 🌿 Cosa Facciamo",
        "overview_educate": "- **Educare:** Forniamo dati accurati e stati di conservazione per le specie vulnerabili.",
        "overview_visualize": "- **Visualizzare:** Mappiamo gli habitat a livello globale per mostrare dove è più necessario concentrare gli sforzi di conservazione.",
        "overview_action": "- **Agire:** Facilitiamo il sostegno diretto per finanziare la protezione dei santuari, le iniziative anti-bracconaggio e il ripristino degli habitat.",

        "library_title": "📚 Biblioteca degli Animali in Pericolo",
        "library_search_label": "🔎 Cerca un animale in pericolo o una regione:",
        "library_no_results": "Nessun animale trovato.",

        "help_title": "🤝 Come Puoi Aiutare",
        "help_intro": "Ogni azione conta quando si tratta di preservare la fauna selvatica. Ecco modi significativi per aiutare a proteggere le specie in pericolo:",
        "help_1_title": "1. 📢 Diffondi Consapevolezza",
        "help_1_desc": "Condividi informazioni sugli animali in pericolo con amici, familiari e reti sociali. Educare gli altri è il primo passo verso la conservazione.",
        "help_2_title": "2. 🛍️ Fai Scelte Sostenibili",
        "help_2_desc": "Evita prodotti derivati da specie in pericolo, riduci la plastica monouso che danneggia la vita marina e sostieni il turismo faunistico eco-sostenibile.",
        "help_3_title": "3. 💚 Dona e Sostieni",
        "help_3_desc": "I contributi finanziano direttamente la protezione degli habitat, le pattuglie anti-bracconaggio e i centri di riabilitazione della fauna selvatica in tutto il mondo.",
        "help_4_title": "4. 🌿 Proteggi gli Habitat Naturali",
        "help_4_desc": "Pianta specie autoctone, riduci gli sprechi e sostieni progetti locali di conservazione e riserve naturali nella tua comunità.",
        "help_5_title": "5. 📜 Sostieni il Cambiamento delle Politiche",
        "help_5_desc": "Sostieni la legislazione per la protezione della fauna selvatica e vota per politiche che proteggano gli ecosistemi naturali vulnerabili e combattano il cambiamento climatico.",
        "help_6_title": "6. 📚 Rimani Informato",
        "help_6_desc": "Usa la nostra **Biblioteca degli Animali in Pericolo** per rimanere aggiornato sullo stato delle specie e saperne di più sulle sfide ambientali globali.",

        "shop_title": "🛍️ Negozio di Merchandise",
        "shop_intro": "Ogni acquisto aiuta a finanziare gli sforzi di conservazione. Acquista la nostra merce ispirata alla fauna selvatica!",
        "buy_now_btn": "🛒 Acquista Ora",
        "added_to_order": "🎉 **{product}** aggiunto al tuo ordine!",
        "order_summary_header": "### 🧾 Riepilogo Ordine",
        "order_total_label": "Totale ordine attuale: **${total}**",
        "complete_purchase_btn": "Completa Acquisto",
        "order_thanks": "🎉 Grazie per il tuo ordine di ${total}, pagato con {method}! La tua merce sarà spedita a breve.",

        "profile_title": "👤 Profilo Utente",
        "back_home_btn": "🏠 Torna alla Home",
        "switch_account_btn": "🔄 Cambia Account",
        "toggle_edit_btn": "✏️ Attiva/Disattiva Modifica",
        "edit_profile_header": "✏️ Modifica Informazioni Profilo",
        "upload_photo_label": "Carica Foto Profilo",
        "guest_username_help": "Gli account ospite non possono cambiare il nome utente.",
        "bio_label": "Descrizione / Biografia",
        "phone_label": "Numero di Telefono (Facoltativo)",
        "save_changes_btn": "💾 Salva Modifiche",
        "profile_updated": "✅ Profilo aggiornato con successo!",
        "username_display": "Nome Utente: {name}",
        "bio_display": "**Biografia / Descrizione:**\n{bio}",
        "phone_display": "**Numero di Telefono:** {phone}",
        "phone_not_provided": "Non fornito",
        "total_impact_label": "**Impatto Totale Donato:** ${total}",

        "settings_title": "⚙️ Impostazioni e Assistenza",
        "settings_intro": "Apprezziamo i tuoi feedback e le segnalazioni di bug per migliorare Animal Advocators!",
        "tab_feedback": "💬 Invia Feedback",
        "tab_bug": "🐛 Segnala un Bug o Errore",
        "tab_language": "🌐 Cambia Lingua",

        "feedback_header": "Condividi la Tua Opinione",
        "feedback_intro": "Come possiamo migliorare la tua esperienza con Animal Advocators?",
        "rating_label": "Come valuteresti la tua esperienza complessiva?",
        "feedback_label": "Il Tuo Feedback o Suggerimenti:",
        "feedback_placeholder": "Scrivi qui il tuo feedback...",
        "submit_feedback_btn": "Invia Feedback",
        "feedback_thanks": "🎉 Grazie! Il tuo feedback è stato inviato al nostro team.",
        "feedback_error": "Inserisci del testo prima di inviare.",

        "bug_header": "Segnala un Problema",
        "bug_intro": "Hai trovato un bug o informazioni errate? Faccelo sapere qui sotto.",
        "bug_category_label": "Categoria del Problema:",
        "bug_title_label": "Breve Riassunto del Problema:",
        "bug_title_placeholder": "es., i punti sulla mappa non si caricano",
        "bug_details_label": "Descrizione Dettagliata:",
        "bug_details_placeholder": "Descrivi cosa è successo e come riprodurlo...",
        "submit_bug_btn": "Invia Segnalazione Bug",
        "bug_thanks": "🚨 Segnalazione bug inviata! Grazie per averci aiutato a mantenere Animal Advocators funzionante senza problemi.",
        "bug_error": "Completa sia il riassunto che la descrizione dettagliata.",

        "language_header": "Cambia Lingua",
        "language_intro": "Seleziona la lingua preferita per Animal Advocators.",
        "choose_language_label": "Scegli una lingua:",
        "save_language_btn": "Salva Lingua",
        "language_updated": "✅ Lingua aggiornata a {language}!",

        "footer_text": "Animal Advocators • Aiutiamo gli Animali Selvatici nel Mondo 🌍",
    },

    "Mandarin": {
        "nav_home": "🏠 首页",
        "nav_overview": "🌎 概览",
        "nav_library": "📚 濒危动物图书馆",
        "nav_help": "🤝 你能做些什么",
        "nav_shop": "🛍️ 周边商店",
        "nav_settings": "⚙️ 设置",

        "sidebar_nav_header": "☰ 导航",
        "edit_profile_btn": "✏️ 编辑资料",
        "logout_btn": "🚪 退出登录",
        "logout_modal_title": "⚠️ 退出确认",
        "logout_modal_text": "确定要退出登录吗？您所做的一切都不会改变。",
        "close_btn": "关闭",
        "yes_btn": "是",

        "app_title": "🌿 Animal Advocators",
        "app_tagline": "为无声者发声",
        "login_intro": "请登录、创建账户或以访客身份继续。",
        "tab_login": "🔑 登录",
        "tab_signup": "📝 注册",
        "username_label": "用户名",
        "password_label": "密码",
        "login_btn": "登录",
        "login_error": "用户名或密码错误。请重试，如果您还没有账户，请注册。",
        "login_missing_error": "请输入用户名和密码。",
        "create_username_label": "创建用户名",
        "email_label": "电子邮箱",
        "phone_optional_label": "电话号码（可选）",
        "create_password_label": "创建密码",
        "confirm_password_label": "确认密码",
        "create_account_btn": "创建账户",
        "signup_missing_error": "请填写所有必填字段。",
        "passwords_mismatch_error": "两次输入的密码不一致。",
        "username_taken_error": "该用户名已被使用。请选择其他用户名，或直接登录。",
        "no_account_prompt": "不想创建账户？",
        "continue_guest_btn": "以访客身份继续",

        "welcome_message": "欢迎，{name}！",
        "home_intro": "Animal Advocators 致力于保护世界各地濒临灭绝的野生动物。使用下方搜索栏查找特定动物或地区，探索地图，或通过捐款支持野生动物保护。",
        "home_search_label": "🔎 搜索濒危动物或地区：",
        "results_for": "### 🎯 “{query}” 的搜索结果",
        "no_animals_found": "未找到与您的搜索匹配的动物。",
        "map_header": "🗺️ 濒危动物地图",
        "map_caption": "💡 点击地图上的绿色圆点，即可查看该动物的照片并直接捐款帮助它。",
        "selected_animal_header": "### 🐾 已选动物",
        "region_label": "**地区：**",
        "status_label": "**状态：**",
        "donation_note": "💚 您下方的捐款将用于帮助 **{animal}**。",
        "clear_selection_btn": "✖️ 清除选择并进行常规捐款",

        "support_header": "💚 支持与目标进度",
        "next_goal_title": "🎯 下一个奖励目标：${goal}",
        "reward_label_title": "奖励：{reward}",
        "total_donated_line": "已捐款总额：<span style=\"color: #2e7d32;\">${total}</span> / ${goal}",
        "goal_completed": "🎉 **目标已达成！** 您解锁了：**{reward}**！",
        "claim_reward_btn": "🎁 领取奖励并解锁下一个目标",
        "reward_claimed": "奖励已领取！您的目标已升级！",
        "ultimate_champion_title": "🏆 终极野生动物守护者！",
        "ultimate_champion_desc": "您已经完成了所有捐款里程碑（最高档 $5,000）！感谢您为野生动物保护做出的巨大贡献。",
        "claimed_rewards_label": "**🏅 已领取的奖励：** ",

        "make_donation_header": "### 💳 进行捐款",
        "donating_to_animal_caption": "您目前正在为帮助 **{animal}** 捐款。点击地图上的其他动物，或使用上方的“清除选择”来更改。",
        "donating_general_caption": "正在向一般保护基金捐款。点击上方地图上的动物，可将您的捐款定向到该特定动物。",
        "donation_slider_label": "选择捐款金额（$）",
        "choose_payment_header": "选择支付方式",
        "payment_header": "支付方式 - {method}",
        "gift_card_code_label": "礼品卡代码",
        "card_number_label": "卡号",
        "name_on_card_label": "持卡人姓名",
        "expiry_label": "有效期（月/年）",
        "cvv_label": "安全码 (CVV)",
        "complete_donation_btn": "完成捐款",
        "missing_gift_code_error": "请输入您的礼品卡代码。",
        "missing_payment_info_error": "请填写所有付款信息。",
        "donation_thanks_animal": "🎉 感谢您使用 {method} 捐款 ${amount} 帮助 {animal}！",
        "donation_thanks_general": "🎉 感谢您使用 {method} 捐款 ${amount}！",

        "overview_title": "🌎 概览",
        "overview_mission_header": "### 🎯 我们的使命",
        "overview_mission_text": "**Animal Advocators** 致力于提高人们对濒危动物的认识，并支持全球保护工作。我们提供教育、地图绘制以及直接资金捐助等工具，以保护地球的生物多样性。",
        "overview_what_header": "### 🌿 我们做什么",
        "overview_educate": "- **教育：** 提供关于脆弱物种的准确数据和保护状态。",
        "overview_visualize": "- **可视化：** 在全球范围内绘制栖息地地图，让用户了解最需要保护关注的地方。",
        "overview_action": "- **行动：** 促成直接支持，以资助保护区保护、反偷猎行动和栖息地恢复。",

        "library_title": "📚 濒危动物图书馆",
        "library_search_label": "🔎 搜索濒危动物或地区：",
        "library_no_results": "未找到相关动物。",

        "help_title": "🤝 你能做些什么",
        "help_intro": "在保护野生动物方面，每一个行动都很重要。以下是您可以帮助保护濒危物种的有效方式：",
        "help_1_title": "1. 📢 传播意识",
        "help_1_desc": "与朋友、家人及社交网络分享关于濒危动物的信息。教育他人是保护工作的第一步。",
        "help_2_title": "2. 🛍️ 做出可持续的选择",
        "help_2_desc": "避免使用濒危物种制成的产品，减少危害海洋生物的一次性塑料，并支持环保型野生动物旅游。",
        "help_3_title": "3. 💚 捐款与支持",
        "help_3_desc": "捐款直接资助全球各地的栖息地保护、反偷猎巡逻队和野生动物康复中心。",
        "help_4_title": "4. 🌿 保护自然栖息地",
        "help_4_desc": "种植本地植物，减少浪费，并支持您所在社区的地方保护项目和自然保护区。",
        "help_5_title": "5. 📜 倡导政策变革",
        "help_5_desc": "支持野生动物保护立法，并为保护脆弱自然生态系统、应对气候变化的政策投票。",
        "help_6_title": "6. 📚 保持学习",
        "help_6_desc": "使用我们的**濒危动物图书馆**，了解物种状态的最新信息，并进一步了解全球环境挑战。",

        "shop_title": "🛍️ 周边商店",
        "shop_intro": "每一次购买都有助于资助保护工作。快来选购我们以野生动物为灵感的周边商品吧！",
        "buy_now_btn": "🛒 立即购买",
        "added_to_order": "🎉 已将 **{product}** 添加到您的订单！",
        "order_summary_header": "### 🧾 订单摘要",
        "order_total_label": "当前订单总额：**${total}**",
        "complete_purchase_btn": "完成购买",
        "order_thanks": "🎉 感谢您以 {method} 支付 ${total} 的订单！您的商品即将发货。",

        "profile_title": "👤 用户资料",
        "back_home_btn": "🏠 返回首页",
        "switch_account_btn": "🔄 切换账户",
        "toggle_edit_btn": "✏️ 切换编辑模式",
        "edit_profile_header": "✏️ 编辑个人资料信息",
        "upload_photo_label": "上传头像",
        "guest_username_help": "访客账户无法更改用户名。",
        "bio_label": "简介 / 个人介绍",
        "phone_label": "电话号码（可选）",
        "save_changes_btn": "💾 保存更改",
        "profile_updated": "✅ 资料更新成功！",
        "username_display": "用户名：{name}",
        "bio_display": "**个人简介：**\n{bio}",
        "phone_display": "**电话号码：** {phone}",
        "phone_not_provided": "未提供",
        "total_impact_label": "**已捐款总额：** ${total}",

        "settings_title": "⚙️ 设置与支持",
        "settings_intro": "我们重视您的反馈和错误报告，以让 Animal Advocators 变得更好！",
        "tab_feedback": "💬 发送反馈",
        "tab_bug": "🐛 报告错误",
        "tab_language": "🌐 更改语言",

        "feedback_header": "分享您的想法",
        "feedback_intro": "我们如何改善您在 Animal Advocators 上的体验？",
        "rating_label": "您对整体体验的评价如何？",
        "feedback_label": "您的反馈或建议：",
        "feedback_placeholder": "请在此输入您的反馈...",
        "submit_feedback_btn": "提交反馈",
        "feedback_thanks": "🎉 谢谢！您的反馈已发送给我们的团队。",
        "feedback_error": "请在提交前输入一些文字。",

        "bug_header": "报告问题",
        "bug_intro": "发现了错误或不正确的信息？请在下方告诉我们。",
        "bug_category_label": "问题类别：",
        "bug_title_label": "问题简要说明：",
        "bug_title_placeholder": "例如：地图上的圆点无法加载",
        "bug_details_label": "详细描述：",
        "bug_details_placeholder": "请描述发生了什么以及如何重现该问题...",
        "submit_bug_btn": "提交错误报告",
        "bug_thanks": "🚨 错误报告已提交！感谢您帮助我们保持 Animal Advocators 顺畅运行。",
        "bug_error": "请同时填写简要说明和详细描述。",

        "language_header": "更改语言",
        "language_intro": "选择您在 Animal Advocators 中使用的首选语言。",
        "choose_language_label": "选择语言：",
        "save_language_btn": "保存语言",
        "language_updated": "✅ 语言已更新为 {language}！",

        "footer_text": "Animal Advocators • 帮助全世界的野生动物 🌍",
    },

    "German": {
        "nav_home": "🏠 Startseite",
        "nav_overview": "🌎 Überblick",
        "nav_library": "📚 Bibliothek Bedrohter Tiere",
        "nav_help": "🤝 Wie Du Helfen Kannst",
        "nav_shop": "🛍️ Merch-Shop",
        "nav_settings": "⚙️ Einstellungen",

        "sidebar_nav_header": "☰ Navigation",
        "edit_profile_btn": "✏️ Profil Bearbeiten",
        "logout_btn": "🚪 Abmelden",
        "logout_modal_title": "⚠️ Abmeldung Bestätigen",
        "logout_modal_text": "Möchtest du dich wirklich abmelden? Alles, was du getan hast, bleibt unverändert.",
        "close_btn": "Schließen",
        "yes_btn": "Ja",

        "app_title": "🌿 Animal Advocators",
        "app_tagline": "Die Stimme der Stimmlosen",
        "login_intro": "Bitte melde dich an, erstelle ein Konto oder fahre als Gast fort.",
        "tab_login": "🔑 Anmelden",
        "tab_signup": "📝 Registrieren",
        "username_label": "Benutzername",
        "password_label": "Passwort",
        "login_btn": "Anmelden",
        "login_error": "Falscher Benutzername oder falsches Passwort. Bitte versuche es erneut oder registriere dich, falls du noch kein Konto hast.",
        "login_missing_error": "Bitte gib Benutzername und Passwort ein.",
        "create_username_label": "Benutzername Erstellen",
        "email_label": "E-Mail-Adresse",
        "phone_optional_label": "Telefonnummer (Optional)",
        "create_password_label": "Passwort Erstellen",
        "confirm_password_label": "Passwort Bestätigen",
        "create_account_btn": "Konto Erstellen",
        "signup_missing_error": "Bitte fülle alle Pflichtfelder aus.",
        "passwords_mismatch_error": "Die Passwörter stimmen nicht überein.",
        "username_taken_error": "Dieser Benutzername ist bereits vergeben. Bitte wähle einen anderen Namen oder melde dich an.",
        "no_account_prompt": "Möchtest du kein Konto erstellen?",
        "continue_guest_btn": "Als Gast Fortfahren",

        "welcome_message": "Willkommen, {name}!",
        "home_intro": "Animal Advocators widmet sich dem Schutz bedrohter Wildtiere auf der ganzen Welt. Nutze die Suchleiste unten, um bestimmte Tiere oder Regionen zu finden, erkunde die Karte oder unterstütze Wildtiere durch Spenden.",
        "home_search_label": "🔎 Suche nach einem bedrohten Tier oder einer Region:",
        "results_for": "### 🎯 Ergebnisse für '{query}'",
        "no_animals_found": "Es wurden keine Tiere gefunden, die deiner Suche entsprechen.",
        "map_header": "🗺️ Karte Bedrohter Tiere",
        "map_caption": "💡 Klicke auf einen grünen Kreis auf der Karte, um das Foto dieses Tieres zu sehen und direkt zu spenden, um ihm zu helfen.",
        "selected_animal_header": "### 🐾 Ausgewähltes Tier",
        "region_label": "**Region:**",
        "status_label": "**Status:**",
        "donation_note": "💚 Deine Spende unten hilft **{animal}**.",
        "clear_selection_btn": "✖️ Auswahl Löschen & Allgemein Spenden",

        "support_header": "💚 Unterstützung & Zielfortschritt",
        "next_goal_title": "🎯 Nächstes Belohnungsziel: ${goal}",
        "reward_label_title": "Belohnung: {reward}",
        "total_donated_line": "Gesamtspenden: <span style=\"color: #2e7d32;\">${total}</span> / ${goal}",
        "goal_completed": "🎉 **Ziel Erreicht!** Du hast freigeschaltet: **{reward}**!",
        "claim_reward_btn": "🎁 Belohnung Einlösen & Nächstes Ziel Freischalten",
        "reward_claimed": "Belohnung eingelöst! Dein Ziel wurde erhöht!",
        "ultimate_champion_title": "🏆 Ultimativer Wildtier-Champion!",
        "ultimate_champion_desc": "Du hast alle Spendenmeilensteine geschafft (Höchststufe $5.000)! Danke für deinen unglaublichen Einsatz für den Naturschutz.",
        "claimed_rewards_label": "**🏅 Eingelöste Belohnungen:** ",

        "make_donation_header": "### 💳 Eine Spende Tätigen",
        "donating_to_animal_caption": "Du spendest derzeit, um **{animal}** zu helfen. Klicke auf ein anderes Tier auf der Karte oder nutze 'Auswahl Löschen' oben, um dies zu ändern.",
        "donating_general_caption": "Spende an den allgemeinen Naturschutzfonds. Klicke auf ein Tier auf der Karte oben, um deine Spende gezielt an dieses Tier zu richten.",
        "donation_slider_label": "Wähle einen Spendenbetrag ($)",
        "choose_payment_header": "Wähle eine Zahlungsmethode",
        "payment_header": "Zahlung - {method}",
        "gift_card_code_label": "Geschenkkarten-Code",
        "card_number_label": "Kartennummer",
        "name_on_card_label": "Name auf der Karte",
        "expiry_label": "Ablaufdatum (MM/JJ)",
        "cvv_label": "CVV",
        "complete_donation_btn": "Spende Abschließen",
        "missing_gift_code_error": "Bitte gib deinen Geschenkkarten-Code ein.",
        "missing_payment_info_error": "Bitte vervollständige alle Zahlungsinformationen.",
        "donation_thanks_animal": "🎉 Danke, dass du ${amount} gespendet hast, um {animal} zu helfen, mit {method}!",
        "donation_thanks_general": "🎉 Danke, dass du ${amount} mit {method} gespendet hast!",

        "overview_title": "🌎 Überblick",
        "overview_mission_header": "### 🎯 Unsere Mission",
        "overview_mission_text": "**Animal Advocators** schärft das Bewusstsein für bedrohte Tiere und unterstützt globale Naturschutzbemühungen. Wir bieten Werkzeuge für Bildung, Kartierung und direkte finanzielle Beiträge, um die Artenvielfalt unseres Planeten zu bewahren.",
        "overview_what_header": "### 🌿 Was Wir Tun",
        "overview_educate": "- **Aufklären:** Bereitstellung genauer Daten und Erhaltungsstatus für gefährdete Arten.",
        "overview_visualize": "- **Visualisieren:** Weltweite Kartierung von Lebensräumen, damit Nutzer sehen, wo der Naturschutz am dringendsten gebraucht wird.",
        "overview_action": "- **Handeln:** Direkte Unterstützung zur Finanzierung von Schutzgebieten, Antiwilderer-Initiativen und Lebensraum-Wiederherstellung.",

        "library_title": "📚 Bibliothek Bedrohter Tiere",
        "library_search_label": "🔎 Suche nach einem bedrohten Tier oder einer Region:",
        "library_no_results": "Es wurden keine Tiere gefunden.",

        "help_title": "🤝 Wie Du Helfen Kannst",
        "help_intro": "Jede Handlung zählt, wenn es um den Schutz der Tierwelt geht. Hier sind sinnvolle Wege, wie du helfen kannst, bedrohte Arten zu schützen:",
        "help_1_title": "1. 📢 Bewusstsein Schaffen",
        "help_1_desc": "Teile Informationen über bedrohte Tiere mit Freunden, Familie und in sozialen Netzwerken. Andere aufzuklären ist der erste Schritt zum Naturschutz.",
        "help_2_title": "2. 🛍️ Nachhaltige Entscheidungen Treffen",
        "help_2_desc": "Vermeide Produkte aus bedrohten Arten, reduziere Einwegplastik, das dem Meeresleben schadet, und unterstütze umweltfreundlichen Wildtiertourismus.",
        "help_3_title": "3. 💚 Spenden & Unterstützen",
        "help_3_desc": "Beiträge finanzieren direkt den Schutz von Lebensräumen, Antiwilderer-Patrouillen und Wildtier-Rehabilitationszentren weltweit.",
        "help_4_title": "4. 🌿 Natürliche Lebensräume Schützen",
        "help_4_desc": "Pflanze einheimische Pflanzen, reduziere Abfall und unterstütze lokale Naturschutzprojekte und Naturschutzgebiete in deiner Gemeinde.",
        "help_5_title": "5. 📜 Für Politischen Wandel Eintreten",
        "help_5_desc": "Unterstütze Gesetze zum Schutz der Tierwelt und stimme für Politik, die gefährdete natürliche Ökosysteme schützt und den Klimawandel bekämpft.",
        "help_6_title": "6. 📚 Informiert Bleiben",
        "help_6_desc": "Nutze unsere **Bibliothek Bedrohter Tiere**, um über den Artenstatus auf dem Laufenden zu bleiben und mehr über globale Umweltprobleme zu erfahren.",

        "shop_title": "🛍️ Merch-Shop",
        "shop_intro": "Jeder Kauf hilft, Naturschutzbemühungen zu finanzieren. Kaufe unsere von der Tierwelt inspirierten Artikel!",
        "buy_now_btn": "🛒 Jetzt Kaufen",
        "added_to_order": "🎉 **{product}** wurde zu deiner Bestellung hinzugefügt!",
        "order_summary_header": "### 🧾 Bestellübersicht",
        "order_total_label": "Aktueller Bestellbetrag: **${total}**",
        "complete_purchase_btn": "Kauf Abschließen",
        "order_thanks": "🎉 Danke für deine Bestellung über ${total}, bezahlt mit {method}! Deine Ware wird bald versandt.",

        "profile_title": "👤 Benutzerprofil",
        "back_home_btn": "🏠 Zurück zur Startseite",
        "switch_account_btn": "🔄 Konto Wechseln",
        "toggle_edit_btn": "✏️ Bearbeitungsmodus Umschalten",
        "edit_profile_header": "✏️ Profilinformationen Bearbeiten",
        "upload_photo_label": "Profilbild Hochladen",
        "guest_username_help": "Gastkonten können ihren Benutzernamen nicht ändern.",
        "bio_label": "Beschreibung / Bio",
        "phone_label": "Telefonnummer (Optional)",
        "save_changes_btn": "💾 Änderungen Speichern",
        "profile_updated": "✅ Profil erfolgreich aktualisiert!",
        "username_display": "Benutzername: {name}",
        "bio_display": "**Bio / Beschreibung:**\n{bio}",
        "phone_display": "**Telefonnummer:** {phone}",
        "phone_not_provided": "Nicht angegeben",
        "total_impact_label": "**Gesamt Gespendet:** ${total}",

        "settings_title": "⚙️ Einstellungen & Support",
        "settings_intro": "Wir schätzen dein Feedback und deine Fehlerberichte, um Animal Advocators zu verbessern!",
        "tab_feedback": "💬 Feedback Senden",
        "tab_bug": "🐛 Fehler oder Problem Melden",
        "tab_language": "🌐 Sprache Ändern",

        "feedback_header": "Teile Deine Gedanken",
        "feedback_intro": "Wie können wir dein Erlebnis mit Animal Advocators verbessern?",
        "rating_label": "Wie würdest du dein Gesamterlebnis bewerten?",
        "feedback_label": "Dein Feedback oder Vorschläge:",
        "feedback_placeholder": "Gib hier dein Feedback ein...",
        "submit_feedback_btn": "Feedback Absenden",
        "feedback_thanks": "🎉 Danke! Dein Feedback wurde an unser Team gesendet.",
        "feedback_error": "Bitte gib vor dem Absenden einen Text ein.",

        "bug_header": "Ein Problem Melden",
        "bug_intro": "Einen Fehler oder falsche Informationen gefunden? Lass es uns unten wissen.",
        "bug_category_label": "Problemkategorie:",
        "bug_title_label": "Kurze Zusammenfassung des Problems:",
        "bug_title_placeholder": "z.B. Kartenpunkte werden nicht geladen",
        "bug_details_label": "Detaillierte Beschreibung:",
        "bug_details_placeholder": "Bitte beschreibe, was passiert ist und wie man es reproduzieren kann...",
        "submit_bug_btn": "Fehlerbericht Absenden",
        "bug_thanks": "🚨 Fehlerbericht gesendet! Danke, dass du uns hilfst, Animal Advocators reibungslos am Laufen zu halten.",
        "bug_error": "Bitte fülle sowohl die Zusammenfassung als auch die detaillierte Beschreibung aus.",

        "language_header": "Sprache Ändern",
        "language_intro": "Wähle deine bevorzugte Sprache für Animal Advocators.",
        "choose_language_label": "Wähle eine Sprache:",
        "save_language_btn": "Sprache Speichern",
        "language_updated": "✅ Sprache auf {language} aktualisiert!",

        "footer_text": "Animal Advocators • Wildtieren Weltweit Helfen 🌍",
    },
}

def t(key, **kwargs):
    """
    Translation helper. Looks up `key` in the dictionary for the language
    the user picked on the Settings page (st.session_state.language),
    falling back to English if the language or key isn't found.
    Any kwargs are used to fill in {placeholders} in the string.
    """
    lang = st.session_state.get("language", "English")
    lang_dict = TRANSLATIONS.get(lang, TRANSLATIONS["English"])
    text = lang_dict.get(key, TRANSLATIONS["English"].get(key, key))
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text
# =========================================================================
# END TRANSLATION LAYER
# =========================================================================

# -----------------------------
# Modal Dialog: Logout Confirmation
# -----------------------------
@st.dialog("⚠️ Logout Confirmation")
def logout_modal():
    st.write(t("logout_modal_text"))
    col_close, col_yes = st.columns(2)
    
    with col_close:
        if st.button(t("close_btn"), use_container_width=True):
            st.session_state.show_logout_dialog = False
            st.session_state.page = "🏠 Home"
            st.rerun()

    with col_yes:
        if st.button(t("yes_btn"), use_container_width=True, type="primary"):
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
    st.title(t("app_title"))
    st.subheader(t("app_tagline"))
    st.write(t("login_intro"))

    login_tab, signup_tab = st.tabs([t("tab_login"), t("tab_signup")])

    # Log In Tab
    with login_tab:
        login_username = st.text_input(t("username_label"), key="login_user")
        login_password = st.text_input(t("password_label"), type="password", key="login_pass")

        if st.button(t("login_btn")):
            if login_username and login_password:
                if verify_user(login_username, login_password):
                    st.session_state.logged_in = True
                    st.session_state.username = login_username
                    st.rerun()
                else:
                    st.error(t("login_error"))
            else:
                st.error(t("login_missing_error"))

    # Sign Up Tab
    with signup_tab:
        username = st.text_input(t("create_username_label"))
        email = st.text_input(t("email_label"))
        phone = st.text_input(t("phone_optional_label"))
        password = st.text_input(t("create_password_label"), type="password")
        confirm = st.text_input(t("confirm_password_label"), type="password")

        if st.button(t("create_account_btn")):
            if username == "" or email == "" or password == "":
                st.error(t("signup_missing_error"))
            elif password != confirm:
                st.error(t("passwords_mismatch_error"))
            else:
                account_created = create_user(username, email, phone, password)
                if account_created:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.phone = phone
                    st.rerun()
                else:
                    st.error(t("username_taken_error"))

    st.markdown("---")
    st.write(t("no_account_prompt"))

    if st.button(t("continue_guest_btn")):
        st.session_state.logged_in = True
        st.session_state.username = "Guest"
        st.rerun()

# -----------------------------
# MAIN APPLICATION SCREEN
# -----------------------------
else:
    # Sidebar Navigation Header
    st.sidebar.title(t("sidebar_nav_header"))
    
    # Profile photo & Edit Profile button placed next to each other
    sb_col1, sb_col2 = st.sidebar.columns([1, 1.3])

    with sb_col1:
        display_image = st.session_state.profile_pic if st.session_state.profile_pic else DEFAULT_AVATAR
        st.image(display_image, width=70)

    with sb_col2:
        st.write(f"**{st.session_state.username}**")
        if st.button(t("edit_profile_btn"), key="sb_edit_profile"):
            st.session_state.page = "👤 Profile"
            st.session_state.editing_profile = True
            st.rerun()

    st.sidebar.markdown("---")

    # Logout button opens Pop-up Modal
    if st.sidebar.button(t("logout_btn")):
        st.session_state.show_logout_dialog = True
        st.rerun()

    # -----------------------------
    # Horizontal Top Navigation
    # -----------------------------
    # NOTE: these values are used internally as page identifiers (compared
    # against st.session_state.page below), so they stay in English. Only
    # the labels shown to the user (via format_func) are translated.
    categories = [
        "🏠 Home",
        "🌎 Overview",
        "📚 Endangered Animal Library",
        "🤝 What You Can Do To Help",
        "🛍️ Merch Shop",
        "⚙️ Settings",
    ]

    NAV_LABEL_KEYS = {
        "🏠 Home": "nav_home",
        "🌎 Overview": "nav_overview",
        "📚 Endangered Animal Library": "nav_library",
        "🤝 What You Can Do To Help": "nav_help",
        "🛍️ Merch Shop": "nav_shop",
        "⚙️ Settings": "nav_settings",
    }

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
        format_func=lambda val: t(NAV_LABEL_KEYS.get(val, val)),
    )

    st.markdown("---")

    page = st.session_state.page

    # -----------------------------------
    # HOME PAGE (Search, Map & Donation)
    # -----------------------------------
    if page == "🏠 Home":
        st.title(t("app_title"))
        st.subheader(t("app_tagline"))
        st.success(t("welcome_message", name=st.session_state.username))

        st.write(t("home_intro"))

        # --- HOME SEARCH BAR ---
        home_search = st.text_input(t("home_search_label"))

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
            st.markdown(t("results_for", query=home_search))
            if filtered_df.empty:
                st.warning(t("no_animals_found"))
            else:
                for _, animal in filtered_df.iterrows():
                    st.info(f"**{animal['Animal']}** — *{animal['Region']}* ({animal['Status']})\n\n{animal['Description']}")

        # --- MAP SECTION ---
        st.header(t("map_header"))
        st.caption(t("map_caption"))

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
                st.markdown(t("selected_animal_header"))
                card_col1, card_col2 = st.columns([1, 2])

                with card_col1:
                    photo_url = get_animal_photo_url(selected_animal_row["Animal"])
                    st.image(photo_url, use_container_width=True, caption=selected_animal_row["Animal"])

                with card_col2:
                    st.subheader(selected_animal_row["Animal"])
                    st.write(f"{t('region_label')} {selected_animal_row['Region']}")
                    st.write(f"{t('status_label')} {selected_animal_row['Status']}")
                    st.write(selected_animal_row["Description"])
                    st.info(t("donation_note", animal=selected_animal_row["Animal"]))

                    if st.button(t("clear_selection_btn")):
                        st.session_state._clear_map_selection = True
                        st.rerun()

        # --- DONATION & GOAL PROGRESS SECTION ---
        st.markdown("---")
        st.header(t("support_header"))

        # Active reward goal tier lookup
        current_tier = next((t2 for t2 in GOAL_TIERS if t2["goal"] == st.session_state.current_goal), None)
        
        if current_tier:
            reward_title = current_tier["reward"]
            target_goal = current_tier["goal"]
            progress_pct = min(st.session_state.total_donated / target_goal, 1.0)

            # Circular Progress Ring & Milestone Display
            st.markdown(f"""
            <div style="background-color: #f0f7f4; border: 2px solid #2e7d32; border-radius: 12px; padding: 20px; text-align: center; margin-bottom: 25px;">
                <h3 style="color: #2e7d32; margin-bottom: 5px;">{t("next_goal_title", goal=target_goal)}</h3>
                <h4 style="color: #1b5e20; margin-top: 0px;">{t("reward_label_title", reward=reward_title)}</h4>
                <div style="font-size: 20px; font-weight: bold; margin: 15px 0; color: #333;">
                    {t("total_donated_line", total=st.session_state.total_donated, goal=target_goal)}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Animated blue-green gradient progress bar tracking goal
            gradient_progress_bar(progress_pct)

            # Goal met & Claim Reward button action
            if st.session_state.total_donated >= target_goal:
                st.balloons()
                trigger_confetti()
                st.success(t("goal_completed", reward=reward_title))
                
                if st.button(t("claim_reward_btn")):
                    st.session_state.claimed_rewards.append(reward_title)
                    
                    # Scale goal to next tier
                    if target_goal == 100:
                        st.session_state.current_goal = 500
                    elif target_goal == 500:
                        st.session_state.current_goal = 1000
                    elif target_goal == 1000:
                        st.session_state.current_goal = 5000
                    
                    trigger_confetti()
                    st.success(t("reward_claimed"))
                    st.rerun()
        else:
            # All milestones achieved state
            st.balloons()
            trigger_confetti()
            st.markdown(f"""
            <div style="background-color: #fff8e1; border: 2px solid #ffa000; border-radius: 12px; padding: 20px; text-align: center; margin-bottom: 25px;">
                <h3 style="color: #f57f17;">{t("ultimate_champion_title")}</h3>
                <p style="font-size: 16px;">{t("ultimate_champion_desc")}</p>
            </div>
            """, unsafe_allow_html=True)
            gradient_progress_bar(1.0)

        # Claimed Rewards Summary Box
        if st.session_state.claimed_rewards:
            st.markdown(t("claimed_rewards_label") + ", ".join(st.session_state.claimed_rewards))

        st.markdown(t("make_donation_header"))

        if st.session_state.donation_target != GENERAL_FUND_LABEL:
            st.caption(t("donating_to_animal_caption", animal=st.session_state.donation_target))
        else:
            st.caption(t("donating_general_caption"))

        donation = st.slider(
            t("donation_slider_label"),
            min_value=5,
            max_value=500,
            value=25,
            step=5
        )

        st.subheader(t("choose_payment_header"))

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
            st.subheader(t("payment_header", method=st.session_state.payment_method))

            if "Gift Card" in st.session_state.payment_method:
                gift_code = st.text_input(t("gift_card_code_label"))
            else:
                card_number = st.text_input(t("card_number_label"))
                card_name = st.text_input(t("name_on_card_label"))
                expiry = st.text_input(t("expiry_label"))
                cvv = st.text_input(t("cvv_label"), type="password")

            if st.button(t("complete_donation_btn")):
                if "Gift Card" in st.session_state.payment_method and not gift_code:
                    st.error(t("missing_gift_code_error"))
                elif "Gift Card" not in st.session_state.payment_method and not (card_number and card_name and expiry and cvv):
                    st.error(t("missing_payment_info_error"))
                else:
                    st.session_state.total_donated += donation
                    trigger_confetti()
                    if st.session_state.donation_target != GENERAL_FUND_LABEL:
                        st.success(t("donation_thanks_animal", amount=donation, animal=st.session_state.donation_target, method=st.session_state.payment_method))
                    else:
                        st.success(t("donation_thanks_general", amount=donation, method=st.session_state.payment_method))
                    st.rerun()

    # -----------------------------------
    # OVERVIEW PAGE
    # -----------------------------------
    elif page == "🌎 Overview":
        st.title(t("overview_title"))
        
        st.markdown(f"""
        {t("overview_mission_header")}
        {t("overview_mission_text")}

        {t("overview_what_header")}
        {t("overview_educate")}
        {t("overview_visualize")}
        {t("overview_action")}
        """)

    # -----------------------------------
    # ENDANGERED ANIMAL LIBRARY PAGE
    # -----------------------------------
    elif page == "📚 Endangered Animal Library":
        st.title(t("library_title"))

        search = st.text_input(t("library_search_label"))

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
            st.warning(t("library_no_results"))
        else:
            st.dataframe(
                filtered_df[["Animal", "Region", "Status", "Description"]],
                use_container_width=True
            )

    # -----------------------------------
    # WHAT YOU CAN DO TO HELP PAGE
    # -----------------------------------
    elif page == "🤝 What You Can Do To Help":
        st.title(t("help_title"))
        st.write(t("help_intro"))

        col1, col2 = st.columns(2)

        with col1:
            st.subheader(t("help_1_title"))
            st.write(t("help_1_desc"))

            st.subheader(t("help_2_title"))
            st.write(t("help_2_desc"))

            st.subheader(t("help_3_title"))
            st.write(t("help_3_desc"))

        with col2:
            st.subheader(t("help_4_title"))
            st.write(t("help_4_desc"))

            st.subheader(t("help_5_title"))
            st.write(t("help_5_desc"))

            st.subheader(t("help_6_title"))
            st.write(t("help_6_desc"))

    # -----------------------------------
    # MERCH SHOP PAGE
    # -----------------------------------
    elif page == "🛍️ Merch Shop":
        st.title(t("shop_title"))
        st.write(t("shop_intro"))

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
                "price": 35,
                "image": "https://placehold.co/300x300?text=Hoodie",
                "description": "Cozy fleece hoodie, perfect for a chilly day out in nature.",
            },
            {
                "name": "🔑 Endangered Species Keychain",
                "price": 10,
                "image": "https://placehold.co/300x300?text=Keychain",
                "description": "A mini enamel keychain featuring your favorite endangered animal.",
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
                if st.button(t("buy_now_btn"), key=f"buy_{idx}"):
                    st.session_state.merch_cart_total += product["price"]
                    trigger_confetti()
                    st.success(t("added_to_order", product=product["name"]))
                st.markdown("---")

        if st.session_state.merch_cart_total > 0:
            st.markdown(t("order_summary_header"))
            st.info(t("order_total_label", total=st.session_state.merch_cart_total))

            st.subheader(t("choose_payment_header"))

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
                st.subheader(t("payment_header", method=st.session_state.payment_method))

                if "Gift Card" in st.session_state.payment_method:
                    merch_gift_code = st.text_input(t("gift_card_code_label"), key="merch_gift_code")
                else:
                    merch_card_number = st.text_input(t("card_number_label"), key="merch_card_number")
                    merch_card_name = st.text_input(t("name_on_card_label"), key="merch_card_name")
                    merch_expiry = st.text_input(t("expiry_label"), key="merch_expiry")
                    merch_cvv = st.text_input(t("cvv_label"), type="password", key="merch_cvv")

                if st.button(t("complete_purchase_btn"), key="merch_complete_purchase"):
                    if "Gift Card" in st.session_state.payment_method and not merch_gift_code:
                        st.error(t("missing_gift_code_error"))
                    elif "Gift Card" not in st.session_state.payment_method and not (merch_card_number and merch_card_name and merch_expiry and merch_cvv):
                        st.error(t("missing_payment_info_error"))
                    else:
                        st.balloons()
                        trigger_confetti()
                        st.success(t("order_thanks", total=st.session_state.merch_cart_total, method=st.session_state.payment_method))
                        st.session_state.merch_cart_total = 0
                        st.rerun()

    # -----------------------------------
    # PROFILE PAGE (EDIT / VIEW)
    # -----------------------------------
    elif page == "👤 Profile":
        st.title(t("profile_title"))

        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 3])
        with col_btn1:
            if st.button(t("back_home_btn")):
                st.session_state.page = "🏠 Home"
                st.session_state.editing_profile = False
                st.rerun()

        with col_btn2:
            if st.button(t("switch_account_btn")):
                st.session_state.show_logout_dialog = True
                st.rerun()

        with col_btn3:
            if st.button(t("toggle_edit_btn")):
                st.session_state.editing_profile = not st.session_state.editing_profile

        # Expanded Edit Profile Inputs
        if st.session_state.editing_profile:
            st.markdown("---")
            st.subheader(t("edit_profile_header"))

            # Upload Image File
            uploaded_photo = st.file_uploader(t("upload_photo_label"), type=["png", "jpg", "jpeg"])

            # Name Edit (Disabled for Guest)
            if st.session_state.username == "Guest":
                st.text_input(t("username_label"), value="Guest", disabled=True, help=t("guest_username_help"))
                new_name = "Guest"
            else:
                new_name = st.text_input(t("username_label"), value=st.session_state.username)

            # Description / Bio
            new_bio = st.text_area(t("bio_label"), value=st.session_state.bio)

            # Phone Number
            new_phone = st.text_input(t("phone_label"), value=st.session_state.phone)

            col_save1, col_save2 = st.columns([1, 4])
            with col_save1:
                if st.button(t("save_changes_btn")):
                    if uploaded_photo is not None:
                        st.session_state.profile_pic = uploaded_photo

                    if st.session_state.username != "Guest" and new_name.strip():
                        st.session_state.username = new_name.strip()

                    st.session_state.bio = new_bio.strip()
                    st.session_state.phone = new_phone.strip()
                    st.session_state.editing_profile = False
                    st.success(t("profile_updated"))
                    st.rerun()

        st.markdown("---")

        # User Profile Display (Clear, medium-large photo size)
        col_img, col_info = st.columns([1, 1.8])

        with col_img:
            main_profile_img = st.session_state.profile_pic if st.session_state.profile_pic else DEFAULT_AVATAR
            st.image(main_profile_img, width=320)

        with col_info:
            st.subheader(t("username_display", name=st.session_state.username))
            st.write(t("bio_display", bio=st.session_state.bio))
            st.write(t("phone_display", phone=st.session_state.phone if st.session_state.phone else t("phone_not_provided")))
            st.write(t("total_impact_label", total=st.session_state.total_donated))

    # -----------------------------------
    # SETTINGS PAGE (Feedback & Bug Report)
    # -----------------------------------
    elif page == "⚙️ Settings":
        st.title(t("settings_title"))
        st.write(t("settings_intro"))

        tab_feedback, tab_bug, tab_language = st.tabs([t("tab_feedback"), t("tab_bug"), t("tab_language")])

        # Feedback Tab
        with tab_feedback:
            st.subheader(t("feedback_header"))
            st.write(t("feedback_intro"))
            
            rating = st.select_slider(
                t("rating_label"),
                options=["⭐ Poor", "⭐⭐ Fair", "⭐⭐⭐ Good", "⭐⭐⭐⭐ Very Good", "⭐⭐⭐⭐⭐ Excellent"],
                value="⭐⭐⭐⭐⭐ Excellent"
            )
            feedback_text = st.text_area(t("feedback_label"), placeholder=t("feedback_placeholder"))

            if st.button(t("submit_feedback_btn")):
                if feedback_text.strip():
                    st.success(t("feedback_thanks"))
                else:
                    st.error(t("feedback_error"))

        # Bug Report Tab
        with tab_bug:
            st.subheader(t("bug_header"))
            st.write(t("bug_intro"))

            bug_category = st.selectbox(
                t("bug_category_label"),
                ["Map / Display Error", "Incorrect Animal Data", "Payment / Donation Issue", "Search Bar Issue", "Other"]
            )
            bug_title = st.text_input(t("bug_title_label"), placeholder=t("bug_title_placeholder"))
            bug_details = st.text_area(t("bug_details_label"), placeholder=t("bug_details_placeholder"))

            if st.button(t("submit_bug_btn")):
                if bug_title.strip() and bug_details.strip():
                    st.success(t("bug_thanks"))
                else:
                    st.error(t("bug_error"))

        # Change Languages Tab
        with tab_language:
            st.subheader(t("language_header"))
            st.write(t("language_intro"))

            language_options = ["English", "Spanish", "Russian", "Italian", "Mandarin", "German"]

            selected_language = st.selectbox(
                t("choose_language_label"),
                language_options,
                index=language_options.index(st.session_state.language)
            )

            if st.button(t("save_language_btn")):
                st.session_state.language = selected_language
                st.success(t("language_updated", language=selected_language))
                st.rerun()

    # -----------------------------------
    # Footer
    # -----------------------------------
    st.markdown("---")
    st.caption(t("footer_text"))