# ============================================
# MAIN - Connexion ATS Studio
# ============================================
import streamlit as st
import os
import time
from dotenv import load_dotenv
from supabase import create_client


from pathlib import Path

# Au lieu de chemin absolu
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

st.set_page_config(
    page_title="ATS Studio",
    page_icon="👔",
    layout="centered"
)

# ── State ─────────────────────────────────────────────────────────────────────
if 'user_id' not in st.session_state:  st.session_state.user_id  = None
if 'username' not in st.session_state: st.session_state.username = None
if 'nom' not in st.session_state:      st.session_state.nom      = None
if 'ville' not in st.session_state:    st.session_state.ville    = None

# ── Déjà connecté → redirect ──────────────────────────────────────────────────
if st.session_state.user_id:
    st.switch_page("pages/1_Recommandation.py")

# ── CSS thème noir + crème ────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

.stApp {
    background: #16140F;
}

* { font-family: -apple-system, BlinkMacSystemFont, 'Inter', sans-serif; }

#MainMenu, header, footer { visibility: hidden; }

.block-container {
    padding-top: 3rem !important;
    max-width: 420px !important;
}

/* Inputs */
.stTextInput > div > div > input {
    background: #211E18 !important;
    border: 0.5px solid rgba(240,235,225,0.18) !important;
    border-radius: 12px !important;
    color: #F0EBE1 !important;
    -webkit-text-fill-color: #F0EBE1 !important;
    caret-color: #F0EBE1 !important;
    padding: 12px 14px !important;
    font-size: 14px !important;
}
.stTextInput > div > div > input::placeholder {
    color: rgba(240,235,225,0.35) !important;
    -webkit-text-fill-color: rgba(240,235,225,0.35) !important;
}
            
.stTextInput > label {
    color: rgba(240,235,225,0.55) !important;
    font-size: 11px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    font-weight: 500 !important;
}

/* Bouton */
.stButton > button, .stFormSubmitButton > button {
    background: #F0EBE1 !important;
    color: #16140F !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    padding: 13px !important;
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
    background: #FFFFFF !important;
    color: #16140F !important;
}

/* Alertes */
.stAlert {
    background: rgba(240,235,225,0.08) !important;
    border-radius: 12px !important;
    color: #F0EBE1 !important;
}
</style>
""", unsafe_allow_html=True)

# ── Logo + titre ──────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:2.5rem 0 0.5rem 0">
    <div style="display:flex;align-items:center;justify-content:center;gap:14px">
        <div style="width:72px;height:72px;border:1.5px solid #F0EBE1;
        border-radius:18px;display:inline-flex;align-items:center;
        justify-content:center">
            <span style="font-size:25px;font-weight:600;letter-spacing:0.04em;
            color:#F0EBE1">ATS</span>
        </div>
        <span style="font-size:30px;font-weight:400;color:#F0EBE1;
        letter-spacing:0.01em">studio</span>
    </div>
    <p style="font-size:13px;color:rgba(240,235,225,0.5);margin:1.4rem 0 0">
        Ton assistant vestimentaire
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)

# ── Formulaire ────────────────────────────────────────────────────────────────
with st.form("login_form"):
    username = st.text_input("Identifiant", placeholder="ton identifiant")
    password = st.text_input("Mot de passe", type="password", placeholder="••••••••")
    submit   = st.form_submit_button("Se connecter", use_container_width=True)

if submit:
    if not username or not password:
        st.error("Remplis tous les champs")
    else:
        result = supabase.table("utilisateurs") \
            .select("*") \
            .eq("username", username) \
            .eq("password", password) \
            .execute()

        if result.data:
            user = result.data[0]
            st.session_state.user_id  = user['id']
            st.session_state.username = user['username']
            st.session_state.nom      = user['nom']
            st.session_state.ville    = user['ville']

            wardrobe = supabase.table("vetements") \
                .select("id") \
                .eq("user_id", user['id']) \
                .execute()

            if len(wardrobe.data) == 0:
                st.success(f"Bienvenue {user['nom']} ! Construisons ta garde-robe.")
                time.sleep(1)
                st.switch_page("pages/4_Onboarding.py")
            else:
                st.success(f"Bon retour {user['nom']} !")
                time.sleep(1)
                st.switch_page("pages/1_Recommandation.py")
        else:
            st.error("Identifiants incorrects")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;margin-top:3rem">
    <p style="font-size:10px;color:rgba(240,235,225,0.3);
    letter-spacing:0.1em;margin:0">ATS STUDIO · 2026</p>
</div>
""", unsafe_allow_html=True)