# ============================================
# PAGE 1 - Recommandation du jour
# ============================================
import streamlit as st
import sys, os
import anthropic
from dotenv import load_dotenv
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(r"C:\Projects\smartwardrobe\.env")

from styles import GLOBAL_CSS
from recommender import get_top_recommendations, get_weather_context, get_calendar_context, run_query
from feedback import save_feedback

st.set_page_config(page_title="SmartWardrobe", page_icon="👔", layout="centered")
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ── Palette couleurs ──────────────────────────────────────────────────────────
COLOR_MAP = {
    "Noir":     "#1a1a1a",
    "Blanc":    "#F5F3EE",
    "Gris":     "#9E9E9E",
    "Marine":   "#1B2A4A",
    "Bleu":     "#4A90D9",
    "Beige":    "#D4C5A9",
    "Camel":    "#C19A6B",
    "Marron":   "#6B3F2A",
    "Kaki":     "#7D8C5A",
    "Bordeaux": "#722F37",
    "Rouge":    "#C0392B",
    "Vert":     "#2ECC71",
}

def get_color(color_name):
    return COLOR_MAP.get(color_name, "#9E9E9E")

# ── Recommendation date depuis Gold ──────────────────────────────────────────
def get_recommendation_date():
    try:
        result = run_query("""
            SELECT TOP 1 recommendation_date
            FROM dbo.gold_recommendation
            ORDER BY recommendation_date DESC
        """)
        if len(result) > 0:
            return str(result.iloc[0]['recommendation_date'])
        return None
    except:
        return None

# ── SVG Avatar ────────────────────────────────────────────────────────────────
def generate_avatar_svg(recs_data):
    haut_color  = "#E0D8CE"
    bas_color   = "#C8C0B4"
    shoes_color = "#8B7355"
    haut_name   = ""
    bas_name    = ""
    shoes_name  = ""

    for item in recs_data:
        cat   = item.get("category", "")
        color = get_color(item.get("color", ""))
        name  = item.get("item_name", "")
        if cat == "Haut" and not haut_name:
            haut_color = color
            haut_name  = name
        elif cat == "Bas" and not bas_name:
            bas_color = color
            bas_name  = name
        elif cat == "Chaussures" and not shoes_name:
            shoes_color = color
            shoes_name  = name

    skin = "#D4A574"
    hair = "#2C1810"

    legende = ""
    if haut_name:
        legende += f"""
        <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.7rem">
            <div style="width:14px;height:14px;border-radius:3px;background:{haut_color};
            border:1px solid rgba(0,0,0,0.1);flex-shrink:0"></div>
            <div>
                <div style="font-size:0.65rem;color:#8A8A8A;text-transform:uppercase;
                letter-spacing:0.08em">Haut</div>
                <div style="font-family:'Syne',sans-serif;font-size:0.8rem;
                font-weight:700;color:#0D1B2A">{haut_name[:25]}</div>
            </div>
        </div>"""
    if bas_name:
        legende += f"""
        <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.7rem">
            <div style="width:14px;height:14px;border-radius:3px;background:{bas_color};
            border:1px solid rgba(0,0,0,0.1);flex-shrink:0"></div>
            <div>
                <div style="font-size:0.65rem;color:#8A8A8A;text-transform:uppercase;
                letter-spacing:0.08em">Bas</div>
                <div style="font-family:'Syne',sans-serif;font-size:0.8rem;
                font-weight:700;color:#0D1B2A">{bas_name[:25]}</div>
            </div>
        </div>"""
    if shoes_name:
        legende += f"""
        <div style="display:flex;align-items:center;gap:0.6rem">
            <div style="width:14px;height:14px;border-radius:3px;background:{shoes_color};
            border:1px solid rgba(0,0,0,0.1);flex-shrink:0"></div>
            <div>
                <div style="font-size:0.65rem;color:#8A8A8A;text-transform:uppercase;
                letter-spacing:0.08em">Chaussures</div>
                <div style="font-family:'Syne',sans-serif;font-size:0.8rem;
                font-weight:700;color:#0D1B2A">{shoes_name[:25]}</div>
            </div>
        </div>"""

    svg = f"""
    <div style="background:white;border:1px solid rgba(13,27,42,0.08);
    border-radius:16px;padding:1.5rem;margin-bottom:1rem">
        <div style="font-size:0.72rem;color:#B8974A;text-transform:uppercase;
        letter-spacing:0.1em;margin-bottom:1rem">👔 Aperçu de la tenue</div>
        <div style="display:flex;justify-content:center;align-items:flex-start;gap:2rem">
            <svg width="140" height="300" viewBox="0 0 160 340" xmlns="http://www.w3.org/2000/svg">
                <ellipse cx="80" cy="35" rx="28" ry="32" fill="{skin}"/>
                <ellipse cx="80" cy="18" rx="28" ry="16" fill="{hair}"/>
                <rect x="52" y="18" width="56" height="12" fill="{hair}"/>
                <rect x="72" y="64" width="16" height="14" fill="{skin}" rx="3"/>
                <path d="M35 78 Q50 70 72 75 L72 78 Q80 76 88 78 L88 75 Q110 70 125 78 L130 160 Q80 170 30 160 Z" fill="{haut_color}"/>
                <path d="M72 75 L80 90 L88 75" fill="none" stroke="{skin}" stroke-width="2"/>
                <path d="M35 78 L15 130 Q12 140 18 142 L42 158 L50 110 Z" fill="{haut_color}"/>
                <path d="M125 78 L145 130 Q148 140 142 142 L118 158 L110 110 Z" fill="{haut_color}"/>
                <ellipse cx="16" cy="145" rx="8" ry="10" fill="{skin}"/>
                <ellipse cx="144" cy="145" rx="8" ry="10" fill="{skin}"/>
                <path d="M32 158 L30 260 L70 260 L80 210 L90 260 L130 260 L128 158 Z" fill="{bas_color}"/>
                <rect x="28" y="258" width="44" height="12" fill="{shoes_color}" rx="6"/>
                <rect x="88" y="258" width="44" height="12" fill="{shoes_color}" rx="6"/>
                <ellipse cx="80" cy="282" rx="45" ry="6" fill="rgba(0,0,0,0.06)"/>
            </svg>
            <div style="padding-top:2rem">{legende}</div>
        </div>
    </div>
    """
    return svg

# ── Claude Haiku ──────────────────────────────────────────────────────────────
def get_claude_advice(recs, weather, calendar):
    try:
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

        tenue = "\n".join([
            f"- {row['item_name']} ({row['category']}, couleur {row['color']}, "
            f"chaleur {row['warmth_level']}/5, formalité {row['formality_level']}/5)"
            for _, row in recs.iterrows()
        ])

        temp = weather.get('temp_current', weather.get('temp_avg', '?'))

        prompt = f"""Tu es un assistant vestimentaire personnel élégant et concis.

Contexte du jour :
- Météo : {temp}°C actuellement à Paris, {weather['weather_label']}
- Agenda : {calendar['context_label']}, formalité requise {calendar['formality_required']}/5

La tenue sélectionnée aujourd'hui est exactement :
{tenue}

En 2 phrases maximum, explique pourquoi CETTE tenue précise est adaptée à la météo et au contexte.
Ne propose rien d'autre. Sois direct et élégant.
Ne commence pas par "Je" ou "Bonjour"."""

        message = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=150,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text

    except Exception as e:
        return None

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
    weather   = get_weather_context()
    calendar  = get_calendar_context()
    recs      = get_top_recommendations()
    reco_date = get_recommendation_date()

# ── Bannière date + pipeline status ──────────────────────────────────────────
today_str    = datetime.today().strftime("%Y-%m-%d")
today_fr     = datetime.today().strftime("%d/%m/%Y")
reco_date_str = str(reco_date)[:10] if reco_date else None

pipeline_ok     = reco_date_str == today_str
pipeline_label  = "✅ Pipeline à jour" if pipeline_ok else "⚠️ Pipeline pas encore tourné"
pipeline_color  = "#22c55e" if pipeline_ok else "#f97316"

st.markdown(f"""
<div style="background:white;border:1px solid rgba(13,27,42,0.08);
border-radius:14px;padding:0.9rem 1.4rem;margin-bottom:1rem;
display:flex;justify-content:space-between;align-items:center">
    <div>
        <div style="font-family:'Syne',sans-serif;font-size:1rem;
        font-weight:700;color:#0D1B2A">📍 Paris · {today_fr}</div>
        <div style="font-size:0.78rem;color:#8A8A8A;margin-top:0.15rem">
            Recommandation du {reco_date_str if reco_date_str else "—"}
        </div>
    </div>
    <div style="font-size:0.75rem;font-weight:600;color:{pipeline_color}">
        {pipeline_label}
    </div>
</div>
""", unsafe_allow_html=True)

# ── Contexte météo + agenda ───────────────────────────────────────────────────
weather_emojis = {
    "Ciel dégagé": "☀️", "Nuageux": "🌤️", "Brouillard": "🌫️",
    "Pluie": "🌧️", "Neige": "❄️", "Averses": "🌦️", "Orage": "⛈️"
}
context_emojis = {
    "Formel": "💼", "Semi-formel": "🏢",
    "Élégant": "✨", "Casual": "😎", "Sport": "🏃"
}

# Température actuelle
temp_display = weather.get('temp_current', weather.get('temp_avg', '?'))

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div class="sw-card" style="text-align:center">
        <div style="font-size:1.8rem">{weather_emojis.get(weather['weather_label'], '🌡️')}</div>
        <div class="sw-page-eyebrow" style="margin-top:0.5rem">Météo · Paris</div>
        <div style="font-family:'Syne',sans-serif;font-size:1.6rem;
        font-weight:800;color:#0D1B2A">{temp_display}°C</div>
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

    # Avatar SVG
    recs_data = [
        {"category": row["category"], "color": row["color"], "item_name": row["item_name"]}
        for _, row in recs.iterrows()
    ]
    st.markdown(generate_avatar_svg(recs_data), unsafe_allow_html=True)

    # Liste scorée
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
                <div class="outfit-sub">{row['category']} · {row['color']} · {row['material']}</div>
                <div class="sw-score-track">
                    <div class="sw-score-fill" style="width:{score_pct}%"></div>
                </div>
            </div>
            <div class="outfit-badge">{score_pct}%</div>
        </div>
        """, unsafe_allow_html=True)

    # Conseil Claude
    with st.spinner("✨ Claude analyse ta tenue..."):
        conseil = get_claude_advice(recs, weather, calendar)

    if conseil:
        st.markdown(f"""
        <div style="background:white;border:1px solid rgba(184,151,74,0.2);
        border-radius:14px;padding:1.2rem 1.4rem;margin:1rem 0">
            <div style="font-size:0.72rem;color:#B8974A;text-transform:uppercase;
            letter-spacing:0.1em;margin-bottom:0.5rem">✨ Conseil du jour</div>
            <div style="font-size:0.9rem;color:#0D1B2A;line-height:1.6;font-style:italic">
                "{conseil}"
            </div>
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
                    temp_avg=float(temp_display),
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
                    temp_avg=float(temp_display),
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
            <div class="sw-result-sub">L'IA retient ton choix et s'améliore cette nuit.</div>
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

# ── Navigation ────────────────────────────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)
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