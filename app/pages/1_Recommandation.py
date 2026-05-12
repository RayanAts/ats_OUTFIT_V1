# ============================================
# PAGE 1 - Recommandation du jour
# ============================================
import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from styles import GLOBAL_CSS
from recommender import get_top_recommendations, get_weather_context, get_calendar_context
from feedback import save_feedback

st.set_page_config(page_title="SmartWardrobe", page_icon="👔", layout="centered")
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ── NAV CSS ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.nav-bar {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: white;
    border-top: 1px solid rgba(13,27,42,0.08);
    display: flex;
    justify-content: space-around;
    align-items: center;
    padding: 0.8rem 0;
    z-index: 999;
    box-shadow: 0 -4px 20px rgba(13,27,42,0.06);
}
.nav-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.2rem;
}
.nav-icon { font-size: 1.4rem; line-height: 1; }
.nav-label {
    font-size: 0.62rem;
    color: #8A8A8A;
    font-family: 'DM Sans', sans-serif;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
.nav-active {
    color: #0D1B2A !important;
    font-weight: 700;
}
.nav-dot {
    width: 4px; height: 4px;
    border-radius: 50%;
    background: #B8974A;
}
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="sw-page-header">
    <div class="sw-page-eyebrow">SmartWardrobe</div>
    <h1 class="sw-page-title">Ta tenue du jour</h1>
    <p class="sw-page-sub">Sélectionnée selon la météo et ton agenda</p>
</div>
""", unsafe_allow_html=True)

# ── Chargement ────────────────────────────────────────────────────────────────
with st.spinner("Analyse en cours..."):
    weather  = get_weather_context()
    calendar = get_calendar_context()
    recs     = get_top_recommendations()

# ── Contexte ──────────────────────────────────────────────────────────────────
weather_emojis = {
    "Ciel dégagé": "☀️", "Nuageux": "🌤️", "Brouillard": "🌫️",
    "Pluie": "🌧️", "Neige": "❄️", "Averses": "🌦️", "Orage": "⛈️"
}
context_emojis = {
    "Formel": "💼", "Semi-formel": "🏢",
    "Élégant": "✨", "Casual": "😎", "Sport": "🏃"
}

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div class="sw-card" style="text-align:center">
        <div style="font-size:1.8rem">{weather_emojis.get(weather['weather_label'], '🌡️')}</div>
        <div class="sw-page-eyebrow" style="margin-top:0.5rem">Météo</div>
        <div style="font-family:'Syne',sans-serif;font-size:1.6rem;
        font-weight:800;color:#0D1B2A">{weather['temp_avg']}°C</div>
        <div style="font-size:0.85rem;color:#8A8A8A;margin-top:0.2rem">
            {weather['weather_label']}
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="sw-card" style="text-align:center">
        <div style="font-size:1.8rem">{context_emojis.get(calendar['context_label'], '📅')}</div>
        <div class="sw-page-eyebrow" style="margin-top:0.5rem">Contexte</div>
        <div style="font-family:'Syne',sans-serif;font-size:1.6rem;
        font-weight:800;color:#0D1B2A">{calendar['context_label']}</div>
        <div style="font-size:0.85rem;color:#8A8A8A;margin-top:0.2rem">
            Formalité {calendar['formality_required']}/5
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="sw-divider"></div>', unsafe_allow_html=True)

# ── State ─────────────────────────────────────────────────────────────────────
if 'feedback_sent' not in st.session_state:
    st.session_state.feedback_sent = False

# ── Recommandations ───────────────────────────────────────────────────────────
if not st.session_state.feedback_sent:

    cat_emojis = {
        "Haut": "👕", "Bas": "👖",
        "Chaussures": "👟", "Accessoire": "🧣"
    }

    for _, row in recs.iterrows():
        score_pct = int(float(row['score_final']) * 100)
        emoji     = cat_emojis.get(row['category'], "👔")

        st.markdown(f"""
        <div class="outfit-row">
            <div class="outfit-rank-num">0{int(row['rank_today'])}</div>
            <div class="outfit-details">
                <div class="outfit-title">{emoji} {row['item_name']}</div>
                <div class="outfit-sub">
                    {row['category']} · {row['color']} · {row['material']}
                </div>
                <div class="sw-score-track">
                    <div class="sw-score-fill" style="width:{score_pct}%"></div>
                </div>
            </div>
            <div class="outfit-badge">{score_pct}%</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="sw-divider"></div>', unsafe_allow_html=True)
    st.markdown("""
    <p style="font-family:'Syne',sans-serif;font-size:1rem;
    font-weight:600;color:#0D1B2A;margin-bottom:1rem">
    Cette tenue te convient ?
    </p>
    """, unsafe_allow_html=True)

    col_yes, col_no = st.columns(2)

    with col_yes:
        if st.button("✓  J'accepte", use_container_width=True, type="primary"):
            for _, row in recs.iterrows():
                save_feedback(
                    item_id=int(row['rank_today']),
                    item_name=row['item_name'],
                    signal=1,
                    context_type=calendar['context_type'],
                    temp_avg=float(weather['temp_avg']),
                    weathercode=0
                )
            st.session_state.feedback_sent = True
            st.session_state.accepted = True
            st.rerun()

    with col_no:
        if st.button("✕  Je refuse", use_container_width=True, type="secondary"):
            for _, row in recs.iterrows():
                save_feedback(
                    item_id=int(row['rank_today']),
                    item_name=row['item_name'],
                    signal=-1,
                    context_type=calendar['context_type'],
                    temp_avg=float(weather['temp_avg']),
                    weathercode=0
                )
            st.session_state.feedback_sent = True
            st.session_state.accepted = False
            st.rerun()

else:
    if st.session_state.accepted:
        st.markdown("""
        <div class="sw-success">
            <div class="sw-result-emoji">✓</div>
            <div class="sw-result-title">Tenue validée</div>
            <div class="sw-result-sub">
                L'IA retient ton choix et s'améliore cette nuit.
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="sw-refused">
            <div class="sw-result-emoji">↺</div>
            <div class="sw-result-title">Noté</div>
            <div class="sw-result-sub">L'IA proposera autre chose demain.</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="sw-divider"></div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    best_score = int(float(recs['score_final'].max()) * 100)

    with col1:
        st.markdown(f"""
        <div class="stat-block">
            <div class="stat-num">{len(recs)}</div>
            <div class="stat-lbl">Scorés</div>
        </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="stat-block">
            <div class="stat-num stat-gold">{best_score}%</div>
            <div class="stat-lbl">Meilleur score</div>
        </div>""", unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="stat-block">
            <div class="stat-num">{calendar['formality_required']}</div>
            <div class="stat-lbl">Formalité /5</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("↺  Nouvelle recommandation", use_container_width=True, type="primary"):
        st.session_state.feedback_sent = False
        st.rerun()

# ── Espace pour la navbar fixe ────────────────────────────────────────────────
st.markdown("<br><br><br>", unsafe_allow_html=True)

# ── Navigation buttons ────────────────────────────────────────────────────────
st.markdown('<div class="sw-divider"></div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🏠\nAccueil", use_container_width=True, type="secondary"):
        st.switch_page("pages/1_Recommandation.py")

with col2:
    if st.button("👔\nGarde-robe", use_container_width=True, type="secondary"):
        st.switch_page("pages/2_Garde_robe.py")

with col3:
    if st.button("📊\nStats", use_container_width=True, type="secondary"):
        st.switch_page("pages/3_Historique.py")

with col4:
    if st.button("➕\nAjouter", use_container_width=True, type="secondary"):
        st.switch_page("pages/5_Ajouter.py")