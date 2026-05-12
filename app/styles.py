# ============================================
# DESIGN SYSTEM - SmartWardrobe
# Aesthetic : Luxury minimal — Navy & Gold
# ============================================

GLOBAL_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&display=swap');

    :root {
        --bg:         #F7F5F0;
        --bg-card:    #FFFFFF;
        --navy:       #0D1B2A;
        --navy-light: #1A2F45;
        --gold:       #B8974A;
        --muted:      #8A8A8A;
        --border:     rgba(13, 27, 42, 0.08);
        --shadow:     0 2px 20px rgba(13, 27, 42, 0.06);
        --shadow-md:  0 8px 40px rgba(13, 27, 42, 0.10);
    }

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
        color: var(--navy);
    }

    .stApp { background-color: var(--bg); }

    .sw-page-header {
        padding: 2rem 0 1.5rem 0;
        border-bottom: 1px solid var(--border);
        margin-bottom: 2rem;
    }

    .sw-page-eyebrow {
        font-size: 0.72rem;
        font-weight: 500;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        color: var(--gold);
        margin-bottom: 0.4rem;
    }

    .sw-page-title {
        font-family: 'Syne', sans-serif;
        font-size: 2rem;
        font-weight: 800;
        color: var(--navy);
        letter-spacing: -0.03em;
        margin: 0;
        line-height: 1.1;
    }

    .sw-page-sub {
        font-size: 0.9rem;
        color: var(--muted);
        margin-top: 0.4rem;
        font-weight: 300;
    }

    .sw-card {
        background: var(--bg-card);
        border-radius: 16px;
        padding: 1.4rem 1.6rem;
        border: 1px solid var(--border);
        box-shadow: var(--shadow);
        transition: box-shadow 0.25s ease, transform 0.25s ease;
    }

    .sw-card:hover {
        box-shadow: var(--shadow-md);
        transform: translateY(-1px);
    }

    .sw-score-track {
        height: 3px;
        background: rgba(13, 27, 42, 0.08);
        border-radius: 99px;
        margin-top: 0.6rem;
        overflow: hidden;
    }

    .sw-score-fill {
        height: 100%;
        border-radius: 99px;
        background: linear-gradient(90deg, var(--navy), var(--gold));
    }

    .outfit-row {
        display: flex;
        align-items: center;
        gap: 1.2rem;
        background: white;
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 1.1rem 1.4rem;
        margin-bottom: 0.75rem;
        transition: all 0.2s ease;
    }

    .outfit-row:hover {
        border-color: rgba(184, 151, 74, 0.3);
        box-shadow: var(--shadow-md);
    }

    .outfit-rank-num {
        font-family: 'Syne', sans-serif;
        font-size: 1.6rem;
        font-weight: 800;
        color: rgba(13, 27, 42, 0.12);
        min-width: 2rem;
        line-height: 1;
    }

    .outfit-details { flex: 1; }

    .outfit-title {
        font-family: 'Syne', sans-serif;
        font-size: 1rem;
        font-weight: 700;
        color: var(--navy);
    }

    .outfit-sub {
        font-size: 0.8rem;
        color: var(--muted);
        margin-top: 0.2rem;
        font-weight: 300;
    }

    .outfit-badge {
        font-family: 'Syne', sans-serif;
        font-size: 0.9rem;
        font-weight: 700;
        color: var(--gold);
        background: rgba(184,151,74,0.08);
        border: 1px solid rgba(184,151,74,0.2);
        border-radius: 8px;
        padding: 0.3rem 0.7rem;
    }

    .stat-block {
        background: white;
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 1.2rem;
        text-align: center;
    }

    .stat-num {
        font-family: 'Syne', sans-serif;
        font-size: 2.2rem;
        font-weight: 800;
        color: var(--navy);
        line-height: 1;
    }

    .stat-gold { color: var(--gold); }

    .stat-lbl {
        font-size: 0.75rem;
        color: var(--muted);
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-top: 0.4rem;
        font-weight: 500;
    }

    .stButton > button {
        border-radius: 12px !important;
        font-family: 'Syne', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        padding: 0.65rem 1rem !important;
        transition: all 0.2s ease !important;
        letter-spacing: 0.02em !important;
    }

    .stButton > button[kind="primary"] {
        background: var(--navy) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 16px rgba(13, 27, 42, 0.2) !important;
    }

    .stButton > button[kind="primary"]:hover {
        background: var(--navy-light) !important;
        transform: translateY(-1px) !important;
    }

    .stButton > button[kind="secondary"] {
        background: white !important;
        color: var(--navy) !important;
        border: 1.5px solid var(--border) !important;
    }

    .wardrobe-item {
        background: white;
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 1.2rem;
        transition: all 0.2s;
        height: 100%;
    }

    .wardrobe-item:hover {
        border-color: rgba(184, 151, 74, 0.35);
        box-shadow: var(--shadow-md);
    }

    .wardrobe-name {
        font-family: 'Syne', sans-serif;
        font-size: 0.92rem;
        font-weight: 700;
        color: var(--navy);
        line-height: 1.3;
    }

    .wardrobe-meta {
        font-size: 0.76rem;
        color: var(--muted);
        margin-top: 0.3rem;
    }

    .dot-track { display: flex; gap: 3px; margin-top: 0.5rem; }

    .dot { width: 8px; height: 8px; border-radius: 50%; }
    .dot-filled       { background: var(--navy); }
    .dot-empty        { background: rgba(13,27,42,0.1); }
    .dot-gold-filled  { background: var(--gold); }

    .timeline-item {
        display: flex;
        gap: 1rem;
        align-items: flex-start;
        padding: 1rem 0;
        border-bottom: 1px solid var(--border);
    }

    .timeline-dot {
        width: 10px; height: 10px;
        border-radius: 50%;
        margin-top: 5px; flex-shrink: 0;
    }

    .timeline-dot-ok  { background: #22c55e; }
    .timeline-dot-no  { background: #f97316; }

    .timeline-date {
        font-size: 0.78rem; color: var(--muted);
        font-weight: 300; white-space: nowrap; min-width: 90px;
    }

    .timeline-content { flex: 1; }

    .timeline-name {
        font-family: 'Syne', sans-serif;
        font-size: 0.92rem; font-weight: 700; color: var(--navy);
    }

    .timeline-meta { font-size: 0.78rem; color: var(--muted); margin-top: 0.15rem; }

    .sw-divider {
        height: 1px;
        background: var(--border);
        margin: 1.5rem 0;
    }

    .sw-success {
        background: #f0fdf4; border: 1px solid #bbf7d0;
        border-radius: 16px; padding: 2rem; text-align: center;
    }

    .sw-refused {
        background: #fff7ed; border: 1px solid #fed7aa;
        border-radius: 16px; padding: 2rem; text-align: center;
    }

    .sw-result-emoji { font-size: 2.5rem; }

    .sw-result-title {
        font-family: 'Syne', sans-serif;
        font-size: 1.3rem; font-weight: 800;
        color: var(--navy); margin-top: 0.5rem;
    }

    .sw-result-sub { font-size: 0.85rem; color: var(--muted); margin-top: 0.3rem; }

    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 1rem !important; max-width: 720px !important; }
</style>
"""
