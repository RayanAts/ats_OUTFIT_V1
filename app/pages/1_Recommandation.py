# ============================================
# PAGE 1 - Recommandation du jour — Apple Style
# ============================================
import streamlit as st
import sys, os, random
from dotenv import load_dotenv
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pathlib import Path

# Au lieu de chemin absolu
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

from styles import GLOBAL_CSS
from recommender import get_top_recommendations, get_weather_context, get_calendar_context, get_tomorrow_context
from feedback import save_feedback
from auth import require_wardrobe
from connector import get_supabase
supabase = get_supabase()

USER_ID = require_wardrobe()

st.set_page_config(page_title="SmartWardrobe", page_icon="👔", layout="centered")

# ── CSS Apple Style ───────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
* { box-sizing: border-box; }
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, 'Inter', sans-serif;
}
.stButton > button {
    border-radius: 14px !important;
    font-weight: 500 !important;
    padding: 12px !important;
    font-size: 14px !important;
}
.stButton > button[kind="primary"] {
    background: #1C1C1E !important;
    color: white !important;
    border: none !important;
}
.stButton > button[kind="secondary"] {
    background: #E5E5EA !important;
    color: #1C1C1E !important;
    border: none !important;
}
</style>
""", unsafe_allow_html=True)

# ── Palette couleurs ──────────────────────────────────────────────────────────
COLOR_MAP = {
    "Noir": "#1a1a1a", "Blanc": "#F5F3EE", "Gris": "#9E9E9E",
    "Marine": "#1B2A4A", "Bleu": "#4A90D9", "Beige": "#D4C5A9",
    "Camel": "#C19A6B", "Marron": "#6B3F2A", "Kaki": "#7D8C5A",
    "Bordeaux": "#722F37", "Rouge": "#C0392B", "Vert": "#2ECC71",
    "Orange": "#E8732A", "Violet": "#6B4E9B", "Rose": "#E8A0B4",
    "Jaune": "#F5C842", "Bleu ciel": "#87CEEB", "Crème": "#F5F0E8",
    "Taupe": "#8B7D6B",
}

def get_color(color_name):
    base = color_name.split(" / ")[0] if " / " in color_name else color_name
    return COLOR_MAP.get(base, "#9E9E9E")

def get_recommendation_date(user_id=1):
    try:
        result = supabase.table("gold_recommendation") \
            .select("recommendation_date") \
            .eq("user_id", user_id) \
            .order("recommendation_date", desc=True) \
            .limit(1) \
            .execute()
        
        return str(result.data[0]['recommendation_date']) if result.data else None
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None
    



# ── Avatar Apple-style ────────────────────────────────────────────────────────
def generate_avatar_apple(recs_data, vibe_emoji="", vibe_label=""):
    haut_color = "#E0D8CE"
    bas_color  = "#C8C0B4"
    shoe_color = "#8B7355"
    haut_name  = bas_name = shoes_name = ""

    for item in recs_data:
        cat   = item.get("category", "")
        color = get_color(item.get("color", ""))
        name  = str(item.get("item_name") or "")
        if cat == "Haut" and not haut_name:
            haut_color = color; haut_name = name
        elif cat == "Bas" and not bas_name:
            bas_color = color; bas_name = name
        elif cat == "Chaussures" and not shoes_name:
            shoe_color = color; shoes_name = name

    skin = "#D4A574"
    hair = "#2C1810"

    legende = ""
    for label, color, name in [("Haut", haut_color, haut_name),
                                 ("Bas", bas_color, bas_name),
                                 ("Chaussures", shoe_color, shoes_name)]:
        if name:
            legende += (
                '<div style="display:flex;align-items:center;gap:8px;margin-bottom:10px">'
                f'<div style="width:12px;height:12px;border-radius:4px;background:{color};'
                'border:0.5px solid rgba(0,0,0,0.12);flex-shrink:0"></div>'
                '<div>'
                f'<div style="font-size:10px;color:#8E8E93;text-transform:uppercase;letter-spacing:0.06em;line-height:1">{label}</div>'
                f'<div style="font-size:13px;font-weight:500;color:#1C1C1E;margin-top:1px">{name[:22]}</div>'
                '</div></div>'
            )

    svg = (
        '<svg width="90" height="165" viewBox="0 0 90 180" xmlns="http://www.w3.org/2000/svg">'
        '<ellipse cx="45" cy="172" rx="26" ry="5" fill="rgba(0,0,0,0.07)"/>'
        f'<ellipse cx="45" cy="28" rx="18" ry="20" fill="{skin}"/>'
        f'<ellipse cx="45" cy="13" rx="18" ry="10" fill="{hair}"/>'
        f'<rect x="27" y="13" width="36" height="8" fill="{hair}"/>'
        f'<rect x="40" y="46" width="10" height="10" rx="2" fill="{skin}"/>'
        f'<path d="M18 58 Q30 50 40 54 L40 56 Q45 54 50 56 L50 54 Q60 50 72 58 L76 128 Q45 136 14 128 Z" fill="{haut_color}"/>'
        '<path d="M40 54 L45 66 L50 54" fill="none" stroke="rgba(0,0,0,0.1)" stroke-width="1.5"/>'
        f'<path d="M18 58 L6 104 Q4 112 10 114 L24 122 L32 78 Z" fill="{haut_color}"/>'
        f'<path d="M72 58 L84 104 Q86 112 80 114 L66 122 L58 78 Z" fill="{haut_color}"/>'
        f'<ellipse cx="8" cy="117" rx="6" ry="8" fill="{skin}"/>'
        f'<ellipse cx="82" cy="117" rx="6" ry="8" fill="{skin}"/>'
        f'<path d="M16 126 L14 164 L38 164 L45 144 L52 164 L76 164 L74 126 Z" fill="{bas_color}"/>'
        '<line x1="45" y1="128" x2="45" y2="144" stroke="rgba(0,0,0,0.12)" stroke-width="1" stroke-dasharray="2,2"/>'
        f'<rect x="12" y="160" width="27" height="10" rx="5" fill="{shoe_color}"/>'
        f'<rect x="51" y="160" width="27" height="10" rx="5" fill="{shoe_color}"/>'
        '<rect x="14" y="161" width="10" height="3" rx="2" fill="rgba(255,255,255,0.25)"/>'
        '<rect x="53" y="161" width="10" height="3" rx="2" fill="rgba(255,255,255,0.25)"/>'
        '</svg>'
    )

    return (
        '<div style="background:white;border-radius:20px;padding:16px;'
        'border:0.5px solid rgba(0,0,0,0.06);margin-bottom:12px">'
        '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px">'
        '<span style="font-size:13px;font-weight:500;color:#1C1C1E">👔 Tenue du jour</span>'
        f'<span style="font-size:11px;background:#F2F2F7;color:#3A3A3C;padding:3px 10px;border-radius:20px;font-weight:500">{vibe_emoji} {vibe_label}</span>'
        '</div>'
        '<div style="display:flex;align-items:flex-start;gap:16px">'
        f'{svg}'
        f'<div style="flex:1;padding-top:4px">{legende}</div>'
        '</div>'
        '</div>'
    )

# ── Score Vibe ────────────────────────────────────────────────────────────────
def get_vibe_score(recs_data):
    NEUTRES = ["Blanc", "Beige", "Gris", "Camel", "Crème", "Taupe"]
    VIFS    = ["Bleu", "Vert", "Rouge", "Kaki", "Orange", "Violet", "Rose", "Jaune"]

    couleurs = [item.get("color", "").split(" / ")[0] for item in recs_data]
    nb_neutres = sum(1 for c in couleurs if c in NEUTRES)
    nb_vifs    = sum(1 for c in couleurs if c in VIFS)

    if nb_neutres == 3:   return "✅", "Safe"
    elif nb_neutres == 2: return "👌", "Clean"
    elif nb_vifs >= 3:    return "⚠️", "Attention"
    elif nb_vifs >= 2:    return "⚡", "Audacieux"
    else:                 return "🔥", "Stylé"

# ── Emojis contextuels ────────────────────────────────────────────────────────
WEATHER_EMOJIS = {
    "Ciel dégagé": "☀️", "Nuageux": "⛅", "Brouillard": "🌫️",
    "Pluie": "🌧️", "Neige": "❄️", "Averses": "🌦️", "Orage": "⛈️"
}
MOOD_EMOJIS = {
    "bureau": "💼", "réunion_client": "🤝",
    "casual": "😎", "sport": "🏃", "soirée": "✨"
}
MOOD_LABELS = {
    "bureau": "Au taf", "réunion_client": "Réunion",
    "casual": "Journée libre", "sport": "On bouge", "soirée": "Soirée"
}
DEMAIN_CONSEILS = {
    "bureau": "Prépare une tenue soignée 👔",
    "réunion_client": "Sors ta plus belle chemise 🤝",
    "casual": "Habille-toi comme tu veux 😎",
    "sport": "Prépare ta tenue de sport 🏃",
    "soirée": "Prépare une tenue élégante ✨"
}

# ── State ─────────────────────────────────────────────────────────────────────
if 'feedback_sent'      not in st.session_state: st.session_state.feedback_sent      = False
if 'accepted'           not in st.session_state: st.session_state.accepted           = False
if 'alternative_count'  not in st.session_state: st.session_state.alternative_count  = 0

# ── Chargement ────────────────────────────────────────────────────────────────
with st.spinner(""):
    weather   = get_weather_context()
    calendar  = get_calendar_context(user_id=USER_ID)
    recs      = get_top_recommendations(offset=st.session_state.alternative_count, user_id=USER_ID)
    reco_date = get_recommendation_date(user_id=USER_ID)
    tomorrow  = get_tomorrow_context(user_id=USER_ID)

NOM          = st.session_state.get('nom', '')
initiale     = NOM[0].upper() if NOM else '?'
temp_display = weather.get('temp_current', weather.get('temp_avg', '?'))
temp_max     = weather.get('temp_max', '')
temp_min     = weather.get('temp_min', '')
today_str    = datetime.today().strftime("%Y-%m-%d")
reco_date_str = str(reco_date)[:10] if reco_date else None
pipeline_ok  = reco_date_str == today_str

weather_emoji = WEATHER_EMOJIS.get(weather.get('weather_label', ''), '🌡️')
mood_type     = str(calendar.get('context_type', ''))
mood_emoji    = MOOD_EMOJIS.get(mood_type, '📅')
mood_label    = MOOD_LABELS.get(mood_type, str(calendar.get('context_label', '')))
formality_req = int(calendar.get("formality_required", 3))

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(
    '<div style="display:flex;justify-content:space-between;align-items:center;padding:12px 4px 16px">'
    '<div>'
    '<p style="font-size:13px;color:#8E8E93;margin:0">SmartWardrobe</p>'
    f'<p style="font-size:22px;font-weight:600;color:#1C1C1E;margin:2px 0 0;line-height:1.2">Bonjour {NOM} 👋</p>'
    '</div>'
    f'<div style="width:38px;height:38px;border-radius:50%;background:#E5E5EA;display:flex;align-items:center;justify-content:center;font-size:15px;font-weight:600;color:#1C1C1E">{initiale}</div>'
    '</div>',
    unsafe_allow_html=True
)

# ── Pipeline status ───────────────────────────────────────────────────────────
if not pipeline_ok:
    st.markdown(
        '<div style="background:#FFF3EE;border-radius:12px;padding:8px 14px;margin-bottom:12px;display:flex;align-items:center;gap:8px">'
        '<span>⚠️</span>'
        '<span style="font-size:12px;color:#C05000;font-weight:500">Pipeline pas encore tourné aujourd\'hui</span>'
        '</div>',
        unsafe_allow_html=True
    )

# ── Cards météo + mood ────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown(
        '<div style="background:linear-gradient(145deg,#E8F4FD,#C8E6FA);border-radius:20px;padding:16px;height:100%">'
        f'<div style="font-size:24px;margin-bottom:6px">{weather_emoji}</div>'
        '<div style="font-size:10px;font-weight:600;letter-spacing:0.06em;text-transform:uppercase;color:#1A6FA8;margin-bottom:4px">MÉTÉO · PARIS</div>'
        f'<div style="font-size:26px;font-weight:600;color:#0A3D5C;line-height:1.1">{temp_display}°C</div>'
        f'<div style="font-size:11px;color:#1A6FA8;margin-top:3px">{weather.get("weather_label","")}</div>'
        f'<div style="font-size:10px;color:#2E80B5;margin-top:4px">↑{temp_max}° · ↓{temp_min}°</div>'
        '</div>',
        unsafe_allow_html=True
    )

with col2:
    dots = ''.join([
        f'<div style="width:8px;height:8px;border-radius:50%;background:{"#6B3FA0" if i < formality_req else "rgba(107,63,160,0.2)"}"></div>'
        for i in range(5)
    ])
    st.markdown(
        '<div style="background:linear-gradient(145deg,#F0EBF8,#E0D2F2);border-radius:20px;padding:16px;height:100%">'
        f'<div style="font-size:24px;margin-bottom:6px">{mood_emoji}</div>'
        '<div style="font-size:10px;font-weight:600;letter-spacing:0.06em;text-transform:uppercase;color:#6B3FA0;margin-bottom:4px">MOOD</div>'
        f'<div style="font-size:22px;font-weight:600;color:#3D1D6B;line-height:1.1">{mood_label}</div>'
        '<div style="font-size:11px;color:#6B3FA0;margin-top:3px">Formalité</div>'
        f'<div style="display:flex;gap:3px;margin-top:5px">{dots}</div>'
        '</div>',
        unsafe_allow_html=True
    )

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# BLOC RECOMMANDATION
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state.feedback_sent:

    recs_data = [
        {"category": row["category"], "color": row["color"], "item_name": row["item_name"]}
        for _, row in recs.iterrows()
    ]

    if len(recs_data) == 0:
        st.warning("⚠️ Aucune recommandation trouvée")
    else:
        vibe_emoji, vibe_label = get_vibe_score(recs_data)
        st.markdown(generate_avatar_apple(recs_data, vibe_emoji, vibe_label), unsafe_allow_html=True)

        # Score IA par vêtement
        cat_emojis = {"Haut": "👕", "Bas": "👖", "Chaussures": "👟"}
        rows_html = ""
        for _, row in recs.iterrows():
            score_pct = int(float(row['score_final']) * 100)
            emoji     = cat_emojis.get(row['category'], "👔")
            rows_html += (
                '<div style="display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:0.5px solid rgba(0,0,0,0.05)">'
                '<div style="flex:1">'
                f'<p style="font-size:13px;font-weight:500;color:#1C1C1E;margin:0">{emoji} {row["item_name"]}</p>'
                f'<p style="font-size:11px;color:#8E8E93;margin:1px 0 0">{row["category"]} · {row["color"]}</p>'
                '<div style="height:3px;background:#E5E5EA;border-radius:2px;margin-top:5px;overflow:hidden">'
                f'<div style="height:3px;width:{score_pct}%;background:#1C1C1E;border-radius:2px"></div>'
                '</div></div>'
                f'<div style="margin-left:12px;font-size:13px;font-weight:600;color:#1C1C1E">{score_pct}%</div>'
                '</div>'
            )

        st.markdown(
            '<div style="background:white;border-radius:20px;padding:14px 16px;border:0.5px solid rgba(0,0,0,0.06);margin-bottom:12px">'
            f'{rows_html}'
            '</div>',
            unsafe_allow_html=True
        )

        # Demain
        if tomorrow is not None:
            ctx_type     = str(tomorrow.get('context_type', ''))
            demain_emoji = MOOD_EMOJIS.get(ctx_type, '📅')
            demain_label = MOOD_LABELS.get(ctx_type, 'Demain')
            demain_conseil = DEMAIN_CONSEILS.get(ctx_type, "Prépare ta tenue à l'avance")
            st.markdown(
                '<div style="background:white;border-radius:16px;padding:12px 14px;border:0.5px solid rgba(0,0,0,0.06);margin-bottom:12px;display:flex;justify-content:space-between;align-items:center">'
                '<div style="display:flex;align-items:center;gap:10px">'
                '<span style="font-size:20px">📅</span>'
                '<div>'
                '<p style="font-size:10px;color:#8E8E93;margin:0">Demain</p>'
                f'<p style="font-size:14px;font-weight:500;color:#1C1C1E;margin:0">{demain_emoji} {demain_label}</p>'
                '</div></div>'
                f'<p style="font-size:11px;color:#6B3FA0;margin:0;text-align:right;max-width:130px;line-height:1.3">{demain_conseil}</p>'
                '</div>',
                unsafe_allow_html=True
            )

    # Boutons action
    col_alt, col_yes, col_no = st.columns([1, 1.5, 1])

    with col_alt:
        if st.button("🔄 Autre", use_container_width=True, type="secondary"):
            st.session_state.alternative_count += 1
            st.cache_data.clear()
            st.rerun()

    with col_yes:
        if st.button("✓ J'accepte", use_container_width=True, type="primary"):
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
        if st.button("✕ Refus", use_container_width=True, type="secondary"):
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
        st.markdown(
            '<div style="background:linear-gradient(145deg,#EAF7EE,#D1F0D8);border-radius:20px;padding:28px 20px;text-align:center;margin:8px 0 16px">'
            '<div style="font-size:40px;margin-bottom:8px">✓</div>'
            '<p style="font-size:18px;font-weight:600;color:#1A5C2A;margin:0 0 4px">Tenue validée !</p>'
            '<p style="font-size:13px;color:#2E7D3A;margin:0">L\'IA retient ton choix et s\'améliore cette nuit.</p>'
            '</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div style="background:linear-gradient(145deg,#FFF3EE,#FFE4D5);border-radius:20px;padding:28px 20px;text-align:center;margin:8px 0 16px">'
            '<div style="font-size:40px;margin-bottom:8px">↺</div>'
            '<p style="font-size:18px;font-weight:600;color:#8B3A00;margin:0 0 4px">Noté !</p>'
            '<p style="font-size:13px;color:#A04A00;margin:0">L\'IA proposera autre chose demain.</p>'
            '</div>',
            unsafe_allow_html=True
        )

    best_score = int(float(recs['score_final'].max()) * 100)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            '<div style="background:white;border-radius:16px;padding:14px 10px;text-align:center;border:0.5px solid rgba(0,0,0,0.06)">'
            f'<p style="font-size:22px;font-weight:600;color:#1C1C1E;margin:0">{len(recs)}</p>'
            '<p style="font-size:11px;color:#8E8E93;margin:3px 0 0">Scorés</p></div>',
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            '<div style="background:white;border-radius:16px;padding:14px 10px;text-align:center;border:0.5px solid rgba(0,0,0,0.06)">'
            f'<p style="font-size:22px;font-weight:600;color:#1C1C1E;margin:0">{best_score}%</p>'
            '<p style="font-size:11px;color:#8E8E93;margin:3px 0 0">Meilleur score</p></div>',
            unsafe_allow_html=True
        )
    with col3:
        st.markdown(
            '<div style="background:white;border-radius:16px;padding:14px 10px;text-align:center;border:0.5px solid rgba(0,0,0,0.06)">'
            f'<p style="font-size:22px;font-weight:600;color:#1C1C1E;margin:0">{formality_req}</p>'
            '<p style="font-size:11px;color:#8E8E93;margin:3px 0 0">Formalité /5</p></div>',
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("↺  Nouvelle recommandation", use_container_width=True, type="primary"):
        st.session_state.feedback_sent = False
        st.session_state.alternative_count = random.randint(1, 5)
        st.rerun()

# ── Navigation ────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
col1, col2, col3, col4, col5 = st.columns(5)

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
    if st.button("✈️\nVoyage", use_container_width=True, type="secondary"):
        st.switch_page("pages/6_Voyage.py")
with col5:
    if st.button("➕\nAjouter", use_container_width=True, type="secondary"):
        st.switch_page("pages/5_Ajouter.py")