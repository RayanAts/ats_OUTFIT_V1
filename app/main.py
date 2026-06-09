# ============================================
# MAIN - Page de connexion SmartWardrobe
# ============================================
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

st.set_page_config(
    page_title="SmartWardrobe",
    page_icon="👔",
    layout="centered"
)

# ── Chargement config ─────────────────────────────────────────────────────────
with open("config.yaml") as f:
    config = yaml.load(f, Loader=SafeLoader)

# ── Authentification ──────────────────────────────────────────────────────────
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# ── Page de connexion ─────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:3rem 0 2rem 0">
    <div style="font-family:'Syne',sans-serif;font-size:2rem;
    font-weight:800;color:#0D1B2A">SmartWardrobe</div>
    <div style="font-size:0.9rem;color:#8A8A8A;margin-top:0.5rem">
        Ton assistant vestimentaire personnel
    </div>
</div>
""", unsafe_allow_html=True)

authenticator.login(
    location="main",
    fields={
        "Form name": "Connexion",
        "Username": "Nom d'utilisateur",
        "Password": "Mot de passe",
        "Login": "Se connecter"
    }
)

name                = st.session_state.get("name")
authentication_status = st.session_state.get("authentication_status")
username            = st.session_state.get("username")

if authentication_status:
    # Stocker l'utilisateur dans la session
    st.session_state['username'] = username
    st.session_state['name']     = name

    st.success(f"Bienvenue {name} ! 👋")
    st.switch_page("pages/1_Recommandation.py")

elif authentication_status is False:
    st.error("Identifiants incorrects")

elif authentication_status is None:
    st.info("Connecte-toi pour accéder à SmartWardrobe")