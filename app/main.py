# ============================================
# MAIN - Connexion SmartWardrobe
# ============================================
import streamlit as st
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv(r"C:\Projects\smartwardrobe\.env")

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

st.set_page_config(
    page_title="SmartWardrobe",
    page_icon="👔",
    layout="centered"
)

# ── State ─────────────────────────────────────────────────────────────────────
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'nom' not in st.session_state:
    st.session_state.nom = None
if 'ville' not in st.session_state:
    st.session_state.ville = None

# ── Déjà connecté → redirect ──────────────────────────────────────────────────
if st.session_state.user_id:
    st.switch_page("pages/1_Recommandation.py")

# ── Page de connexion ─────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:3rem 0 2rem 0">
    <div style="font-family:'Syne',sans-serif;font-size:2.5rem;
    font-weight:800;color:#0D1B2A">SmartWardrobe</div>
    <div style="font-size:0.95rem;color:#8A8A8A;margin-top:0.5rem">
        Ton assistant vestimentaire personnel
    </div>
</div>
""", unsafe_allow_html=True)

with st.form("login_form"):
    username = st.text_input("Nom d'utilisateur")
    password = st.text_input("Mot de passe", type="password")
    submit   = st.form_submit_button("Se connecter", use_container_width=True, type="primary")

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
            st.success(f"Bienvenue {user['nom']} ! 👋")
            st.switch_page("pages/1_Recommandation.py")
        else:
            st.error("Identifiants incorrects")