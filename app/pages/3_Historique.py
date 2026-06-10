# ============================================
# PAGE 3 - Historique & Statistiques
# ============================================
import streamlit as st
import json
import os
import sys
from collections import Counter, defaultdict
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from styles import GLOBAL_CSS
from recommender import run_query

st.set_page_config(page_title="Historique · SmartWardrobe", page_icon="📊", layout="centered")
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

st.markdown("""
<div class="sw-page-header">
    <div class="sw-page-eyebrow">Mémoire & Intelligence</div>
    <h1 class="sw-page-title">Historique & Stats</h1>
    <p class="sw-page-sub">Tes tenues et ce que l'IA a appris sur toi</p>
</div>
""", unsafe_allow_html=True)

# ── Chargement ────────────────────────────────────────────────────────────────
FEEDBACK_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "feedback_local"
)

def load_feedbacks():
    feedbacks = []
    if not os.path.exists(FEEDBACK_DIR):
        return feedbacks
    for fname in sorted(os.listdir(FEEDBACK_DIR), reverse=True):
        if fname.endswith(".json"):
            with open(os.path.join(FEEDBACK_DIR, fname), encoding="utf-8") as f:
                feedbacks.append(json.load(f))
    return feedbacks

@st.cache_data(ttl=300)
def load_wardrobe():
    return run_query("""
        SELECT item_name, category, color, material,
               warmth_level, formality_level
        FROM public.stg_wardrobe
    """)

feedbacks = load_feedbacks()
wardrobe  = load_wardrobe()

# ── Etat vide ─────────────────────────────────────────────────────────────────
if not feedbacks:
    st.markdown("""
    <div style="background:white;border:1px solid rgba(13,27,42,0.08);
    border-radius:16px;padding:3rem;text-align:center;margin-top:2rem">
        <div style="font-size:3rem;margin-bottom:1rem">👔</div>
        <div style="font-family:'Syne',sans-serif;font-size:1.1rem;
        font-weight:700;color:#0D1B2A">Aucun historique pour l'instant</div>
        <div style="font-size:0.85rem;color:#8A8A8A;margin-top:0.4rem">
            Commence par valider ta première tenue sur la page Recommandation.
        </div>
    </div>
    """, unsafe_allow_html=True)

else:
    # ── Calculs ───────────────────────────────────────────────────────────────
    total         = len(feedbacks)
    accepted      = [f for f in feedbacks if f['signal'] == 1]
    refused       = [f for f in feedbacks if f['signal'] == -1]
    rate          = int((len(accepted) / total) * 100)
    top_item      = Counter([f['item_name'] for f in accepted]).most_common(1)[0][0] if accepted else "—"
    worst_item    = Counter([f['item_name'] for f in refused]).most_common(1)[0][0]  if refused  else "—"
    top_context   = Counter([f['context_type'] for f in feedbacks]).most_common(1)[0][0]
    temps         = [f['temp_avg'] for f in feedbacks]
    avg_temp      = round(sum(temps) / len(temps), 1) if temps else 0
    streak        = 0
    for f in reversed(feedbacks):
        if f['signal'] == 1:
            streak += 1
        else:
            break

    avg_formality = round(wardrobe['formality_level'].mean(), 1)
    top_color     = wardrobe['color'].mode()[0] if len(wardrobe) > 0 else "—"

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab1, tab2 = st.tabs(["📊 Statistiques", "📅 Historique"])

    # ════════════════════════════════════════════════════════════════════════════
    # TAB 1 — STATISTIQUES
    # ════════════════════════════════════════════════════════════════════════════
    with tab1:

        st.markdown("<br>", unsafe_allow_html=True)

        # KPIs principaux
        st.markdown(f"""
        <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:1rem;margin-bottom:1.5rem">
            <div class="stat-block" style="padding:1.5rem">
                <div class="stat-num stat-gold">{rate}%</div>
                <div class="stat-lbl">Taux d'acceptation</div>
                <div style="font-size:0.78rem;color:#8A8A8A;margin-top:0.5rem">
                    {len(accepted)} acceptées · {len(refused)} refusées
                </div>
            </div>
            <div class="stat-block" style="padding:1.5rem">
                <div class="stat-num">🔥 {streak}</div>
                <div class="stat-lbl">Streak actuel</div>
                <div style="font-size:0.78rem;color:#8A8A8A;margin-top:0.5rem">
                    tenues de suite
                </div>
            </div>
            <div class="stat-block">
                <div class="stat-num" style="font-size:1.3rem">{top_color}</div>
                <div class="stat-lbl">Couleur dominante</div>
            </div>
            <div class="stat-block">
                <div class="stat-num">{avg_formality}</div>
                <div class="stat-lbl">Formalité moyenne</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="sw-divider"></div>', unsafe_allow_html=True)

        # Insights
        st.markdown("""
        <p style="font-family:'Syne',sans-serif;font-size:1rem;
        font-weight:700;color:#0D1B2A;margin-bottom:1rem">
        Ce que l'IA a appris
        </p>
        """, unsafe_allow_html=True)

        insights = [
            {"emoji": "👔", "label": "Vêtement favori",   "value": top_item,    "sub": "le plus accepté"},
            {"emoji": "❌", "label": "Vêtement évité",    "value": worst_item,  "sub": "le plus refusé"},
            {"emoji": "📅", "label": "Contexte dominant", "value": top_context, "sub": f"{total} interactions"},
            {"emoji": "🌡️", "label": "Temp. moyenne",     "value": f"{avg_temp}°C", "sub": "lors de tes sessions"},
        ]

        insights_html = ""
        for ins in insights:
            insights_html += f"""
            <div style="display:flex;align-items:center;gap:1rem;
            background:white;border:1px solid rgba(13,27,42,0.08);
            border-radius:12px;padding:1rem 1.2rem;margin-bottom:0.6rem">
                <div style="font-size:1.6rem">{ins['emoji']}</div>
                <div style="flex:1">
                    <div style="font-size:0.75rem;color:#8A8A8A;text-transform:uppercase;
                    letter-spacing:0.08em">{ins['label']}</div>
                    <div style="font-family:'Syne',sans-serif;font-size:1rem;
                    font-weight:700;color:#0D1B2A;margin-top:0.15rem">{ins['value']}</div>
                </div>
                <div style="font-size:0.75rem;color:#8A8A8A">{ins['sub']}</div>
            </div>
            """
        st.markdown(insights_html, unsafe_allow_html=True)

        st.markdown('<div class="sw-divider"></div>', unsafe_allow_html=True)

        # Phrase Spotify Wrapped
        if rate >= 70:
            phrase = f"Tu sais ce que tu veux. {rate}% d'acceptation — ton style est clair et assumé."
            bg, border = "#f0fdf4", "#bbf7d0"
        elif rate >= 40:
            phrase = f"L'IA apprend encore. {rate}% — continue à swiper pour affiner."
            bg, border = "#fff7ed", "#fed7aa"
        else:
            phrase = f"Exigeant ! {rate}% — l'IA va devoir travailler dur pour te satisfaire."
            bg, border = "#fef2f2", "#fecaca"

        st.markdown(f"""
        <div style="background:{bg};border:1px solid {border};
        border-radius:16px;padding:1.5rem;text-align:center">
            <div style="font-family:'Syne',sans-serif;font-size:0.95rem;
            font-weight:600;color:#0D1B2A;line-height:1.5">"{phrase}"</div>
        </div>
        """, unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════════════
    # TAB 2 — HISTORIQUE
    # ════════════════════════════════════════════════════════════════════════════
    with tab2:

        st.markdown("<br>", unsafe_allow_html=True)

        # Stats rapides
        st.markdown(f"""
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin-bottom:1.5rem">
            <div class="stat-block">
                <div class="stat-num">{total}</div>
                <div class="stat-lbl">Total</div>
            </div>
            <div class="stat-block">
                <div class="stat-num stat-gold">{rate}%</div>
                <div class="stat-lbl">Acceptation</div>
            </div>
            <div class="stat-block">
                <div class="stat-num">{len(refused)}</div>
                <div class="stat-lbl">Refusées</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Filtre
        filtre = st.radio(
            "",
            ["Tous", "Acceptées", "Refusées"],
            horizontal=True,
            label_visibility="collapsed"
        )

        filtered = feedbacks
        if filtre == "Acceptées":
            filtered = [f for f in feedbacks if f['signal'] == 1]
        elif filtre == "Refusées":
            filtered = [f for f in feedbacks if f['signal'] == -1]

        st.markdown("<br>", unsafe_allow_html=True)

        # Timeline groupée par date
        grouped = defaultdict(list)
        for fb in filtered:
            grouped[fb['feedback_date']].append(fb)

        for date, items in grouped.items():
            st.markdown(f"""
            <div style="font-size:0.75rem;color:#8A8A8A;text-transform:uppercase;
            letter-spacing:0.12em;font-weight:500;margin-bottom:0.8rem;
            margin-top:1.2rem">{date}</div>
            """, unsafe_allow_html=True)

            timeline_html = ""
            for fb in items:
                is_ok       = fb['signal'] == 1
                dot_color   = "#22c55e" if is_ok else "#f97316"
                label       = "Accepté"  if is_ok else "Refusé"
                label_color = "#22c55e"  if is_ok else "#f97316"

                timeline_html += f"""
                <div style="display:flex;align-items:center;gap:1rem;
                background:white;border:1px solid rgba(13,27,42,0.08);
                border-radius:12px;padding:1rem 1.2rem;margin-bottom:0.6rem">
                    <div style="width:10px;height:10px;border-radius:50%;
                    background:{dot_color};flex-shrink:0"></div>
                    <div style="flex:1">
                        <div style="font-family:'Syne',sans-serif;font-size:0.92rem;
                        font-weight:700;color:#0D1B2A">{fb['item_name']}</div>
                        <div style="font-size:0.78rem;color:#8A8A8A;margin-top:0.15rem">
                            {fb.get('context_type','—')} · {fb.get('temp_avg','—')}°C
                        </div>
                    </div>
                    <div style="font-size:0.78rem;font-weight:600;color:{label_color}">
                        {label}
                    </div>
                </div>
                """
            st.markdown(timeline_html, unsafe_allow_html=True)

# ── Navigation ────────────────────────────────────────────────────────────────
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