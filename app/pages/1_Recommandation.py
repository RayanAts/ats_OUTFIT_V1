# ============================================
# PAGE 1 - Recommandation du jour
# ============================================
import streamlit as st
import sys, os
from dotenv import load_dotenv
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(r"C:\Projects\smartwardrobe\.env")

from styles import GLOBAL_CSS
from recommender import get_top_recommendations, get_weather_context, get_calendar_context, get_tomorrow_context, run_query
from feedback import save_feedback
from auth import require_wardrobe
USER_ID = require_wardrobe()

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
def get_recommendation_date(user_id=1):
    try:
        result = run_query(f"""
            SELECT recommendation_date
            FROM public.gold_recommendation
            WHERE user_id = {user_id}
            ORDER BY recommendation_date DESC
            LIMIT 1
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

    for item in recs_data:
        cat   = item.get("category", "")
        color = get_color(item.get("color", ""))
        if cat == "Haut":
            haut_color = color
        elif cat == "Bas":
            bas_color = color
        elif cat == "Chaussures":
            shoes_color = color

    skin = "#D4A574"
    hair = "#2C1810"

    return f"""
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
            <div style="padding-top:2rem">LEGENDE_PLACEHOLDER</div>
        </div>
    </div>
    """

def generate_avatar_with_legend(recs_data):
    haut_color  = "#E0D8CE"
    bas_color   = "#C8C0B4"
    shoes_color = "#8B7355"
    haut_name   = ""
    bas_name    = ""
    shoes_name  = ""

    for item in recs_data:
        cat   = item.get("category", "")
        color = get_color(item.get("color", ""))
        name  = str(item.get("item_name") or "")
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

    return f"""
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

# ── Score Vibe ────────────────────────────────────────────────────────────────
def get_vibe_score(recs_data):
    NEUTRES = ["Blanc", "Beige", "Gris", "Camel"]
    FONCES  = ["Noir", "Marine", "Bordeaux", "Marron"]
    VIFS    = ["Bleu", "Vert", "Rouge", "Kaki"]

    couleurs = [item.get("color", "") for item in recs_data]

    nb_neutres = sum(1 for c in couleurs if c in NEUTRES)
    nb_fonces  = sum(1 for c in couleurs if c in FONCES)
    nb_vifs    = sum(1 for c in couleurs if c in VIFS)

    if nb_neutres == 3:
        return "✅", "Safe"
    elif nb_neutres == 2:
        return "👌", "Clean"
    elif nb_vifs >= 2 and nb_fonces >= 1:
        return "⚡", "Audacieux"
    elif nb_vifs == 3:
        return "⚠️", "Attention"
    else:
        return "🔥", "Stylé"

# ── State ─────────────────────────────────────────────────────────────────────
if 'feedback_sent' not in st.session_state:
    st.session_state.feedback_sent = False
if 'accepted' not in st.session_state:
    st.session_state.accepted = False
if 'alternative_count' not in st.session_state:
    st.session_state.alternative_count = 0

# ── Chargement ────────────────────────────────────────────────────────────────


with st.spinner("Analyse en cours..."):
    weather   = get_weather_context()
    calendar  = get_calendar_context(user_id=USER_ID)
    recs      = get_top_recommendations(offset=st.session_state.alternative_count, user_id=USER_ID)
    reco_date = get_recommendation_date(user_id=USER_ID)
    tomorrow  = get_tomorrow_context(user_id=USER_ID)

# ── Header ────────────────────────────────────────────────────────────────────
NOM = st.session_state.get('nom', '')

st.markdown(f"""
<div class="sw-page-header">
    <div class="sw-page-eyebrow">SmartWardrobe · 👤 {NOM}</div>
    <h1 class="sw-page-title">Ta tenue du jour</h1>
    <p class="sw-page-sub">Sélectionnée selon la météo et ton agenda</p>
</div>
""", unsafe_allow_html=True)

# ── Bannière date + pipeline ──────────────────────────────────────────────────
today_str     = datetime.today().strftime("%Y-%m-%d")
today_fr      = datetime.today().strftime("%d/%m/%Y")
reco_date_str = str(reco_date)[:10] if reco_date else None
pipeline_ok    = reco_date_str == today_str
pipeline_label = "✅ Pipeline à jour" if pipeline_ok else "⚠️ Pipeline pas encore tourné"
pipeline_color = "#22c55e" if pipeline_ok else "#f97316"

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

# ── Météo + Contexte ──────────────────────────────────────────────────────────
weather_emojis = {
    "Ciel dégagé": "☀️", "Nuageux": "🌤️", "Brouillard": "🌫️",
    "Pluie": "🌧️", "Neige": "❄️", "Averses": "🌦️", "Orage": "⛈️"
}
context_emojis = {
    "Formel": "💼", "Semi-formel": "🏢",
    "Élégant": "✨", "Casual": "😎", "Sport": "🏃"
}

temp_display = weather.get('temp_current', weather.get('temp_avg', '?'))
temp_max     = weather.get('temp_max', '')
temp_min     = weather.get('temp_min', '')

st.markdown('<div style="display:flex;gap:1rem;margin-bottom:1rem">', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div class="sw-card" style="text-align:center;height:100%;box-sizing:border-box">
        <div style="font-size:1.8rem">{weather_emojis.get(weather['weather_label'], '🌡️')}</div>
        <div class="sw-page-eyebrow" style="margin-top:0.5rem">Météo · Paris</div>
        <div style="font-family:'Syne',sans-serif;font-size:1.6rem;
        font-weight:800;color:#0D1B2A">{temp_display}°C</div>
        <div style="font-size:0.82rem;color:#8A8A8A;margin-top:0.2rem">
            {weather['weather_label']}
        </div>
        <div style="font-size:0.78rem;color:#B8974A;margin-top:0.3rem">
            ↑ {temp_max}°C · ↓ {temp_min}°C
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    mood_labels = {
        "bureau":         "Au taf",
        "réunion_client": "Réunion",
        "casual":         "Journée libre",
        "sport":          "On bouge",
        "soirée":         "Soirée"
    }
    mood_label = mood_labels.get(str(calendar['context_type']), calendar['context_label'])

    st.markdown(f"""
    <div class="sw-card" style="text-align:center;height:100%;box-sizing:border-box">
        <div style="font-size:1.8rem">{context_emojis.get(calendar['context_label'], '📅')}</div>
        <div class="sw-page-eyebrow" style="margin-top:0.5rem">Mood</div>
        <div style="font-family:'Syne',sans-serif;font-size:1.6rem;
        font-weight:800;color:#0D1B2A">{mood_label}</div>
        <div style="font-size:0.85rem;color:#8A8A8A;margin-top:0.2rem">
            Formalité {calendar['formality_required']}/5
        </div>
        <div style="font-size:0.78rem;color:#B8974A;margin-top:0.3rem">
            &nbsp;
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# BLOC RECOMMANDATION
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state.feedback_sent:

    # ── Avatar + Légende (tout en un seul bloc HTML) ──────────────────────────
    recs_data = [
        {"category": row["category"], "color": row["color"], "item_name": row["item_name"]}
        for _, row in recs.iterrows()
    ]
    # Debug temporaire
    if len(recs_data) == 0:
        st.warning("⚠️ Aucune recommandation trouvée pour cet utilisateur")
    else:
        st.markdown(generate_avatar_with_legend(recs_data), unsafe_allow_html=True)


    # ── Vibe score ────────────────────────────────────────────────────────────
    vibe_emoji, vibe_label = get_vibe_score(recs_data)
    st.markdown(f"""
    <div style="text-align:center;margin:-0.5rem 0 1rem 0">
        <span style="font-size:0.78rem;color:#8A8A8A;text-transform:uppercase;
        letter-spacing:0.1em">Vibe · </span>
        <span style="font-size:0.85rem;font-weight:700;color:#0D1B2A">
            {vibe_emoji} {vibe_label}
        </span>
    </div>
    """, unsafe_allow_html=True)

    # ── Liste scorée ──────────────────────────────────────────────────────────
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

    # ── Contexte lendemain ────────────────────────────────────────────────────
    if tomorrow is not None:
        context_to_label = {
            "bureau":         "Au bureau",
            "réunion_client": "Réunion importante",
            "casual":         "Journée détendue",
            "sport":          "Activité sportive",
            "soirée":         "Soirée"
        }
        context_to_conseil = {
            "bureau":         "Prépare une tenue propre et soignée",
            "réunion_client": "Prépare ta plus belle chemise",
            "casual":         "Demain tu peux t'habiller comme tu veux",
            "sport":          "Pense à préparer ta tenue de sport",
            "soirée":         "Prépare une tenue élégante"
        }
        context_type   = str(tomorrow['context_type'])
        label_demain   = context_to_label.get(context_type, "Demain")
        conseil_demain = context_to_conseil.get(context_type, "Prépare ta tenue à l'avance")
        tomorrow_emoji = context_emojis.get(str(tomorrow['context_label']), "📅")

        st.markdown(f"""
        <div style="background:white;border:1px solid rgba(13,27,42,0.08);
        border-radius:14px;padding:1rem 1.4rem;margin-top:0.8rem">
            <div style="font-size:0.72rem;color:#8A8A8A;text-transform:uppercase;
            letter-spacing:0.1em;margin-bottom:0.5rem">📅 Demain</div>
            <div style="display:flex;justify-content:space-between;align-items:center">
                <div style="font-family:'Syne',sans-serif;font-size:0.95rem;
                font-weight:700;color:#0D1B2A">
                    {tomorrow_emoji} {label_demain}
                </div>
                <div style="font-size:0.78rem;color:#B8974A;
                font-weight:500;text-align:right;max-width:200px">
                    {conseil_demain}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="sw-divider"></div>', unsafe_allow_html=True)

    # ── Question + boutons ────────────────────────────────────────────────────
    st.markdown("""
    <p style="font-family:'Syne',sans-serif;font-size:1rem;
    font-weight:600;color:#0D1B2A;margin-bottom:1rem">
    Cette tenue te convient ?
    </p>
    """, unsafe_allow_html=True)

    col_alt, col_yes, col_no = st.columns([1, 1, 1])

    with col_alt:
        if st.button("🔄 Autre tenue", use_container_width=True, type="secondary"):
            st.session_state.alternative_count += 1
            st.cache_data.clear()
            st.rerun()

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

# ══════════════════════════════════════════════════════════════════════════════
# BLOC POST-FEEDBACK
# ══════════════════════════════════════════════════════════════════════════════
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
        import random
        st.session_state.feedback_sent = False
        st.session_state.alternative_count = random.randint(1, 5)
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