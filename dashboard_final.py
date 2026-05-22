"""
=============================================================
 ETAPE 4 — DASHBOARD STREAMLIT + AUTHENTIFICATION + MYSQL
 CRI Guelmim — Smart Fisheries Analytics
=============================================================
Lancer : python -m streamlit run dashboard_mysql.py
=============================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from sqlalchemy import create_engine, text
import streamlit_authenticator as stauth
import bcrypt
import yaml
from yaml.loader import SafeLoader
import os
import io
from datetime import datetime

# ─────────────────────────────────────────
# CONFIGURATION PAGE
# ─────────────────────────────────────────

st.set_page_config(
    page_title="Blue Data fish insight — CRI Guelmim",
    page_icon="🐬",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ─────────────────────────────────────────
# GÉNÉRATION PDF
# ─────────────────────────────────────────

def generer_pdf_bytes(nom_invest, budget, risque, preference, top, gains_list):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors as rl_colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (SimpleDocTemplate, Paragraph,
                                    Spacer, Table, TableStyle, HRFlowable)
    from reportlab.lib.enums import TA_CENTER

    BLEU  = rl_colors.HexColor("#0077b6")
    BLEU2 = rl_colors.HexColor("#023e8a")
    BLANC = rl_colors.white

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=1.5*cm, leftMargin=1.5*cm,
                            topMargin=1.5*cm, bottomMargin=1.5*cm)
    styles = getSampleStyleSheet()
    s_titre = ParagraphStyle("Titre2", fontSize=20, fontName="Helvetica-Bold",
                              textColor=BLANC, alignment=TA_CENTER, spaceAfter=6)
    s_sous  = ParagraphStyle("Sous2",  fontSize=11, fontName="Helvetica",
                              textColor=BLANC, alignment=TA_CENTER, spaceAfter=4)
    s_h1    = ParagraphStyle("H12",    fontSize=13, fontName="Helvetica-Bold",
                              textColor=BLEU, spaceBefore=12, spaceAfter=6)
    s_corps = ParagraphStyle("Corps2", fontSize=10, fontName="Helvetica",
                              textColor=rl_colors.HexColor("#333333"),
                              spaceAfter=4, leading=14)
    s_foot  = ParagraphStyle("Footer2", fontSize=8, fontName="Helvetica",
                              textColor=rl_colors.grey, alignment=TA_CENTER)

    elements = []
    date_str = datetime.now().strftime("%d/%m/%Y a %H:%M")

    entete = Table([[Paragraph("SMART FISHERIES ANALYTICS — CRI GUELMIM", s_titre)]],
                   colWidths=[18*cm])
    entete.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), BLEU2),
        ("ROWPADDING", (0,0), (-1,-1), 18),
    ]))
    elements.append(entete)
    elements.append(Spacer(1, 0.3*cm))

    sous = Table([[Paragraph("Systeme Intelligent d Aide a la Decision", s_sous)]],
                 colWidths=[18*cm])
    sous.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), BLEU),
        ("ROWPADDING", (0,0), (-1,-1), 8)
    ]))
    elements.append(sous)
    elements.append(Spacer(1, 0.5*cm))

    elements.append(Paragraph("1. Profil Investisseur", s_h1))
    profil_data = [
        ["Investisseur", nom_invest],
        ["Budget",       f"{budget:,.0f} DH"],
        ["Risque",       risque.upper()],
        ["Preference",   preference],
        ["Date",         date_str],
    ]
    t_profil = Table(profil_data, colWidths=[6*cm, 12*cm])
    t_profil.setStyle(TableStyle([
        ("FONTNAME",      (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 10),
        ("TEXTCOLOR",     (0,0), (0,-1), BLEU),
        ("BACKGROUND",    (0,0), (0,-1), rl_colors.HexColor("#d1ecf1")),
        ("ROWBACKGROUNDS",(0,0), (-1,-1), [rl_colors.HexColor("#f8f9fa"), BLANC]),
        ("GRID",          (0,0), (-1,-1), 0.5, rl_colors.HexColor("#dee2e6")),
        ("PADDING",       (0,0), (-1,-1), 8),
    ]))
    elements.append(t_profil)
    elements.append(Spacer(1, 0.5*cm))

    elements.append(Paragraph("2. Recommandations Personnalisees", s_h1))
    rec_header = [["Rang", "Secteur", "Port", "Score", "ROI/an", "Gain 3 ans"]]
    rec_rows = []
    medailles = ["1er", "2eme", "3eme"]
    for i, (_, row) in enumerate(top.iterrows()):
        gain_total = gains_list[i] if i < len(gains_list) else 0
        roi = (row["Rentabilite"]/10)*0.25
        rec_rows.append([
            medailles[i], row["Secteur"], row["Port"],
            f"{row['Score_100']}/100", f"{roi*100:.1f}%",
            f"{gain_total:,.0f} DH"
        ])
    t_rec = Table(rec_header + rec_rows,
                  colWidths=[1.5*cm, 5.5*cm, 2.5*cm, 2*cm, 2*cm, 4.5*cm])
    t_rec.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), BLEU2),
        ("TEXTCOLOR",     (0,0), (-1,0), BLANC),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTNAME",      (0,1), (-1,-1), "Helvetica"),
        ("FONTSIZE",      (0,0), (-1,-1), 9),
        ("ALIGN",         (0,0), (-1,-1), "CENTER"),
        ("ALIGN",         (1,0), (1,-1), "LEFT"),
        ("GRID",          (0,0), (-1,-1), 0.5, rl_colors.HexColor("#dee2e6")),
        ("PADDING",       (0,0), (-1,-1), 7),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [BLANC, rl_colors.HexColor("#f8f9fa")]),
    ]))
    elements.append(t_rec)
    elements.append(Spacer(1, 0.5*cm))

    elements.append(Paragraph("3. Predictions LSTM 2026-2027", s_h1))
    pred_data = [
        ["Annee",         "Volume Predit", "Evolution", "Precision"],
        ["2025 (reel)",   "119 490 T",     "Reference", "-"],
        ["2026 (predit)", "100 749 T",     "+8.3%",     "96%"],
        ["2027 (predit)", "103 885 T",     "+3.1%",     "96%"],
    ]
    t_pred = Table(pred_data, colWidths=[4*cm, 4*cm, 4*cm, 6*cm])
    t_pred.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), BLEU2),
        ("TEXTCOLOR",     (0,0), (-1,0), BLANC),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 9),
        ("ALIGN",         (0,0), (-1,-1), "CENTER"),
        ("GRID",          (0,0), (-1,-1), 0.5, rl_colors.HexColor("#dee2e6")),
        ("PADDING",       (0,0), (-1,-1), 8),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [BLANC, rl_colors.HexColor("#f8f9fa")]),
    ]))
    elements.append(t_pred)
    elements.append(Spacer(1, 0.5*cm))

    avert = Table([[Paragraph(
        "AVERTISSEMENT : Rapport genere automatiquement. "
        "Contactez le CRI Guelmim pour toute decision d investissement.",
        s_corps)]], colWidths=[18*cm])
    avert.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), rl_colors.HexColor("#fff3cd")),
        ("PADDING",    (0,0), (-1,-1), 10),
        ("LINEABOVE",  (0,0), (-1,0),  2, rl_colors.HexColor("#fd7e14")),
    ]))
    elements.append(avert)
    elements.append(Spacer(1, 0.3*cm))
    elements.append(HRFlowable(width="100%", thickness=1, color=BLEU))
    elements.append(Spacer(1, 0.2*cm))
    elements.append(Paragraph(
        f"Smart Fisheries Analytics — CRI Guelmim | {date_str}",
        s_foot))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()

# ─────────────────────────────────────────
# CONNEXION MYSQL
# ─────────────────────────────────────────

@st.cache_resource
def get_engine():
    return create_engine(
        "mysql+pymysql://root:MALIKA2005@localhost:3306/cri_guelmim?charset=utf8mb4"
    )

# ─────────────────────────────────────────
# AUTHENTIFICATION
# ─────────────────────────────────────────

CONFIG_FILE = "config_auth.yaml"

def hash_pw(pw):
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()

if not os.path.exists(CONFIG_FILE):
    passwords = [hash_pw('cri2025'), hash_pw('invest2025')]
    config = {
        'credentials': {
            'usernames': {
                'analyst': {
                    'email': 'analyst@cri-guelmim.ma',
                    'name': 'Analyste CRI',
                    'password': passwords[0],
                    'role': 'analyst'
                },
                'investisseur': {
                    'email': 'invest@email.ma',
                    'name': 'Investisseur',
                    'password': passwords[1],
                    'role': 'investor'
                }
            }
        },
        'cookie': {
            'expiry_days': 1,
            'key': 'cri_guelmim_2025',
            'name': 'cri_cookie'
        },
        'preauthorized': {'emails': []}
    }
    with open(CONFIG_FILE, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)

with open(CONFIG_FILE) as f:
    config = yaml.load(f, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
)

# ─────────────────────────────────────────
# CSS GLOBAL
# ─────────────────────────────────────────

st.markdown("""
<style>
    .stApp { background-color: #e8f4f8; }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #03045e 0%, #0077b6 60%, #00b4d8 100%);
    }
    [data-testid="stSidebar"] * { color: white !important; }
    .main-header {
        background: linear-gradient(135deg, #03045e, #0077b6, #00b4d8);
        padding: 25px; border-radius: 15px; color: white;
        text-align: center; margin-bottom: 20px;
        box-shadow: 0 8px 32px rgba(0,119,182,0.3);
    }
    .stDownloadButton button {
        background: linear-gradient(135deg, #0077b6, #00b4d8) !important;
        color: white !important; border: none !important;
        border-radius: 8px !important; font-weight: 700 !important;
        font-size: 1.1em !important; padding: 15px !important;
    }
    .stButton > button {
        background: linear-gradient(135deg, #03045e, #0077b6) !important;
        color: white !important; border: none !important;
        border-radius: 8px !important;
    }
    .kpi-card {
        background: white; padding: 20px; border-radius: 12px;
        border-top: 5px solid #0077b6; text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    }
    .kpi-value { font-size: 2em; font-weight: 800; color: #03045e; }
    .kpi-label { font-size: 0.85em; color: #666; }
    .kpi-delta-pos { color: #0077b6; font-weight: 700; }
    .kpi-delta-neg { color: #e63946; font-weight: 700; }
    [data-testid="stMetric"] {
        background: white; padding: 15px; border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border-left: 4px solid #0077b6;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# PAGE DE CONNEXION
# ─────────────────────────────────────────

authenticator.login(location='main')
name = st.session_state.get('name')
authentication_status = st.session_state.get('authentication_status')
username = st.session_state.get('username')

if authentication_status is False:
    st.error("❌ Nom d'utilisateur ou mot de passe incorrect !")
    st.info("""
    **Comptes disponibles :**
    - 👤 `analyst` / `cri2025` — Analyste CRI
    - 👤 `investisseur` / `invest2025` — Investisseur
    """)
    st.stop()
    

    # ─────────────────────────────────────────
    # BACKGROUND LOGIN PAGE
    # ─────────────────────────────────────────
elif authentication_status is None:
    st.markdown("""
    <style>

/* ===== Background ===== */
.stApp{
    background-image:url("https://images.unsplash.com/photo-1500375592092-40eb2168fd21?q=80&w=1920");
    background-size:cover;
    background-position:center;
    background-attachment:fixed;
}

/* Overlay */
.stApp::before{
    content:"";
    position:fixed;
    inset:0;
    background:linear-gradient(
        135deg,
        rgba(3,4,94,0.82),
        rgba(0,119,182,0.55),
        rgba(0,180,216,0.35)
    );
    z-index:0;
}

/* Main content */
.main{
    position:relative;
    z-index:1;
}

/* ===== Login Container ===== */
[data-testid="stForm"]{
    background:rgba(255,255,255,0.10);
    border:1px solid rgba(255,255,255,0.18);
    backdrop-filter:blur(14px);
    -webkit-backdrop-filter:blur(14px);

    padding:40px;
    border-radius:25px;

    box-shadow:
        0 8px 32px rgba(0,0,0,0.35),
        inset 0 0 0 1px rgba(255,255,255,0.08);

    margin-top:30px;
}

/* ===== Login Title ===== */
h1{
    color:white !important;
    font-size:3rem !important;
    font-weight:800 !important;
    text-align:center;
    margin-bottom:25px !important;
    text-shadow:0 4px 15px rgba(0,0,0,0.45);
}

/* ===== Labels ===== */
label{
    color:white !important;
    font-weight:600 !important;
    font-size:15px !important;
}

/* ===== Inputs ===== */
.stTextInput input{
    background:rgba(255,255,255,0.92) !important;

    border:none !important;
    border-radius:14px !important;

    height:55px !important;

    padding-left:18px !important;

    font-size:16px !important;
    font-weight:500 !important;

    box-shadow:0 4px 12px rgba(0,0,0,0.10);
}

/* Focus input */
.stTextInput input:focus{
    border:2px solid #00b4d8 !important;
    box-shadow:0 0 15px rgba(0,180,216,0.6) !important;
}

/* ===== Login Button ===== */
.stButton button{
    width:100%;
    height:55px;

    border:none !important;
    border-radius:14px !important;

    background:linear-gradient(
        135deg,
        #0077b6,
        #00b4d8
    ) !important;

    color:white !important;
    font-size:18px !important;
    font-weight:700 !important;

    transition:0.3s ease;
    box-shadow:0 6px 20px rgba(0,119,182,0.35);
}

/* Hover button */
.stButton button:hover{
    transform:translateY(-2px);
    box-shadow:0 10px 25px rgba(0,180,216,0.45);
}

/* ===== Hide Streamlit Footer ===== */
footer{
    visibility:hidden;
}

header{
    visibility:hidden;
}

/* ===== Sidebar hidden login ===== */
[data-testid="stSidebar"]{
    display:none;
}

</style>
    """, unsafe_allow_html=True)

    st.stop()
# ─────────────────────────────────────────
# RÔLE UTILISATEUR
# ─────────────────────────────────────────

role = config['credentials']['usernames'][username].get('role', 'investor')

# ─────────────────────────────────────────
# CHARGEMENT DONNÉES MYSQL
# ─────────────────────────────────────────

@st.cache_data(ttl=300)
def charger_especes():
    engine = get_engine()
    return pd.read_sql("""
        SELECT p.nom_port AS Port, e.nom_espece AS Categorie,
               f.poids_tonnes AS Poids_2025_T,
               f.valeur_kdh AS Valeur_2025_KDH,
               f.variation_poids_pct AS Var_Poids_pct,
               f.variation_valeur_pct AS Var_Valeur_pct
        FROM fait_debarquements f
        JOIN dim_port p ON f.id_port = p.id_port
        JOIN dim_espece e ON f.id_espece = e.id_espece
        JOIN dim_date d ON f.id_date = d.id_date
        WHERE d.annee = 2025
    """, engine)

@st.cache_data(ttl=300)
def charger_serie():
    engine = get_engine()
    return pd.read_sql("""
        SELECT annee AS Annee,
               tantan_total_t AS TanTan_Volume_T,
               sidiifni_total_t AS SidiIfni_Volume_T,
               total_region_t AS Total_Volume_T,
               tantan_total_mkdh AS TanTan_Valeur_MKDH,
               sidiifni_total_mkdh AS SidiIfni_Valeur_MKDH,
               total_region_mkdh AS Total_Valeur_MKDH
        FROM serie_temporelle ORDER BY annee
    """, engine)

@st.cache_data(ttl=300)
def charger_flotte():
    engine = get_engine()
    return pd.read_sql("""
        SELECT p.nom_port AS Port, f.nb_hauturiere,
               f.nb_cotiere, f.nb_artisanale, f.tjb_total
        FROM flotte_peche f
        JOIN dim_port p ON f.id_port = p.id_port
    """, engine)

@st.cache_data(ttl=300)
def charger_transformation():
    engine = get_engine()
    return pd.read_sql("""
        SELECT p.nom_port AS Port, t.semi_conserve,
               t.conserve, t.congelation, t.farine_huile,
               t.autres, t.total
        FROM transformation t
        JOIN dim_port p ON t.id_port = p.id_port
    """, engine)

especes   = charger_especes()
serie     = charger_serie()
flotte    = charger_flotte()
transform = charger_transformation()

# ─────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────

with st.sidebar:
    st.markdown(f"""
    <div style='text-align:center; padding:15px 0;'>
        <div style='font-size:3em;'>🦈</div>
        <div style='font-size:1.2em; font-weight:800;'>Blue Data fish insight</div>
        <div style='font-size:0.8em; opacity:0.8;'>CRI Guelmim</div>
        <hr style='border-color:rgba(255,255,255,0.3);'>
        <div style='font-size:0.85em;'>👤 {name}</div>
        <div style='font-size:0.75em; opacity:0.7;'>
            {' Admin' if role=='admin' else ' Analyste' if role=='analyst' else ' Investisseur'}
        </div>
    </div>
    """, unsafe_allow_html=True)

    if role == 'investor':
        pages = [
            "  Dashboard Analytique",
            "  Prévisions du Marché",
            "  Aide a la Decision",
            "  Conseiller Intelligent",
        ]
    else:
        pages = [
            "  Dashboard Analytique",
            "  Visualisation Geographique",
            "  Analyse Sectorielle",
            "  Tendances Historiques",
            "  Performance des Ports",
            "  Ecosysteme Halieutique",
            "  Prévisions du Marché",
            "  Analyse Sentiment",
        ]

    page = st.radio("Navigation", pages)
    st.divider()
    authenticator.logout("Se deconnecter", location="sidebar")
    st.caption("2025 CRI Guelmim")


# ═══════════════════════════════════════════
# PAGE 1 — TABLEAU DE BORD
# ═══════════════════════════════════════════

if "Dashboard Analytique" in page:
    st.markdown("""
    <div class='main-header'>
        <h1>Smart insights for sustainable fisheries</h1>
        <p>Centre Regional d'Investissement — Region Guelmim-Oued Noun</p>
        <p>Systeme Intelligent d'Aide a la Decision pour l'Investissement Halieautique</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Indicateurs Cles — Region Guelmim 2025")
    c1, c2, c3, c4  = st.columns(4)
    kpis = [
        ("119 490 T",  "Volume Total",     "Stable vs 2024",  True),
        ("1,239 MDH",  "Valeur Marchande",  "+17% vs 2024",   True),
        ("11 700+",    "Emplois Directs",   "Marins actifs",  True),
        ("~20%",       "Part Nationale",    "3eme rang",      True),
    ]
    for col, (val, label, delta, pos) in zip([c1,c2,c3,c4], kpis):
        col.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-value'>{val}</div>
            <div class='kpi-label'>{label}</div>
            <div class='{"kpi-delta-pos" if pos else "kpi-delta-neg"}'>{delta}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2])
    with col1:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=serie['Annee'], y=serie['Total_Volume_T'],
            name='Volume', marker_color='#1a7a5a', opacity=0.85
        ))
        fig.add_trace(go.Scatter(
            x=serie['Annee'], y=serie['Total_Valeur_MKDH'] * 80,
            name='Valeur (x80)', mode='lines+markers',
            line=dict(color='#e63946', width=3),
            marker=dict(size=8), yaxis='y2'
        ))
        fig.update_layout(
            title="Volume & Valeur — Evolution Regionale",
            yaxis=dict(title="Volume (T)"),
            yaxis2=dict(title="Valeur (MKDHx80)", overlaying='y', side='right'),
            height=380, template='plotly_white',
            legend=dict(orientation='h', y=-0.2)
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        totaux = especes.groupby('Port').agg(Vol=('Poids_2025_T','sum')).reset_index()
        fig = go.Figure(go.Pie(
            labels=totaux['Port'], values=totaux['Vol'],
            hole=0.5, marker=dict(colors=['#0077b6','#e63946']),
            textinfo='label+percent'
        ))
        fig.update_layout(title="Repartition Volume 2025",
                          height=380, template='plotly_white')
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    col1, col2, col3 = st.columns(3)
    col1.success("Tan-Tan : +65% volume en 2025")
    col2.error("Sidi Ifni : -58% volume — Investigation requise")
    col3.warning("Cephalopodes : +79% valeur a Sidi Ifni")


# ═══════════════════════════════════════════
# PAGE 2 — ANALYSE PAR ESPECE
# ═══════════════════════════════════════════

elif "Analyse Sectorielle" in page:
    st.title("Analyse Detaillee par Espece")
    st.caption("Donnees chargees depuis MySQL — cri_guelmim")

    port_filtre = st.selectbox("Port :", ["Les deux", "Tan-Tan", "Sidi Ifni"])
    df = especes if port_filtre == "Les deux" else especes[especes['Port'] == port_filtre]

    col1, col2 = st.columns(2)
    couleurs = ['#0077b6','#2ca02c','#ff7f0e','#d62728','#9467bd','#8c564b']

    with col1:
        fig = go.Figure()
        for i, (_, row) in enumerate(df.iterrows()):
            fig.add_trace(go.Bar(
                name=f"{row['Port']} - {row['Categorie']}",
                x=[f"{row['Port'][:2]} - {row['Categorie']}"],
                y=[row['Poids_2025_T']],
                marker_color=couleurs[i % len(couleurs)]
            ))
        fig.update_layout(title="Volumes 2025 (T)",
                          height=400, template='plotly_white')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        df_plot = df.copy()
        df_plot['Label'] = df_plot['Port'].str[:2] + ' — ' + df_plot['Categorie']
        colors = ['#1a7a5a' if v >= 0 else '#e63946' for v in df_plot['Var_Poids_pct']]
        fig = go.Figure(go.Bar(
            x=df_plot['Var_Poids_pct'], y=df_plot['Label'],
            orientation='h', marker_color=colors
        ))
        fig.add_vline(x=0, line_dash="dash", line_color="black")
        fig.update_layout(title="Variations Volume (%)",
                          height=400, template='plotly_white')
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Tableau Detaille — MySQL")
    st.dataframe(df.style.background_gradient(
        subset=['Var_Poids_pct','Var_Valeur_pct'], cmap='RdYlGn'),
        use_container_width=True)


# ═══════════════════════════════════════════
# PAGE 3 — EVOLUTION HISTORIQUE
# ═══════════════════════════════════════════

elif "Tendances Historiques" in page:
    st.title("Evolution Historique 2019-2025")
    st.caption("Donnees reelles depuis MySQL — table serie_temporelle")

    fig = make_subplots(rows=2, cols=1,
        subplot_titles=("Volume (Tonnes)", "Valeur (Millions DH)"),
        shared_xaxes=True, vertical_spacing=0.12)

    for nom, col_v, col_val, couleur in [
        ('Tan-Tan',      'TanTan_Volume_T',   'TanTan_Valeur_MKDH',   '#0077b6'),
        ('Sidi Ifni',    'SidiIfni_Volume_T', 'SidiIfni_Valeur_MKDH', '#e63946'),
        ('Total Region', 'Total_Volume_T',    'Total_Valeur_MKDH',    '#1a7a5a'),
    ]:
        fig.add_trace(go.Scatter(
            x=serie['Annee'], y=serie[col_v], name=nom,
            mode='lines+markers',
            line=dict(color=couleur, width=3), marker=dict(size=8)
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=serie['Annee'], y=serie[col_val], name=nom,
            mode='lines+markers', showlegend=False,
            line=dict(color=couleur, width=3), marker=dict(size=8)
        ), row=2, col=1)

    fig.update_layout(height=600, template='plotly_white')
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(serie, use_container_width=True)


# ═══════════════════════════════════════════
# PAGE 4 — COMPARAISON DES PORTS
# ═══════════════════════════════════════════

elif "Performance des Ports" in page:
    st.title("Comparaison — Tan-Tan vs Sidi Ifni")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div style='background:linear-gradient(135deg,#0077b6,#023e8a);
                    padding:20px;border-radius:12px;color:white;'>
            <h3>Port de Tan-Tan</h3>
            <p>Volume : 93 063 T (+65%)</p>
            <p>Valeur : 1 046 MKDH (+34%)</p>
            <p>Emplois : 8 500 marins</p>
            <p>Unites : 18 etablissements</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style='background:linear-gradient(135deg,#e63946,#9b1c1c);
                    padding:20px;border-radius:12px;color:white;'>
            <h3>Port de Sidi Ifni</h3>
            <p>Volume : 26 427 T (-58%)</p>
            <p>Valeur : 193 MKDH (-30%)</p>
            <p>Emplois : 3 200 marins</p>
            <p>Unites : 2 etablissements</p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    totaux = especes.groupby('Port').agg(
        Vol=('Poids_2025_T','sum'), Val=('Valeur_2025_KDH','sum')).reset_index()

    col1, col2 = st.columns(2)
    with col1:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=totaux['Port'], y=totaux['Vol'],
                             marker_color=['#0077b6','#e63946']))
        fig.update_layout(title="Volume Total (T)", height=350, template='plotly_white')
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=totaux['Port'], y=totaux['Val']/1000,
                             marker_color=['#0077b6','#e63946']))
        fig.update_layout(title="Valeur (MKDH)", height=350, template='plotly_white')
        st.plotly_chart(fig, use_container_width=True)


# ═══════════════════════════════════════════
# PAGE 5 — FLOTTE & TRANSFORMATION
# ═══════════════════════════════════════════

elif "Ecosysteme Halieutique" in page:
    st.title("Flotte de Peche et Transformation")
    st.caption("Donnees depuis MySQL — flotte_peche et transformation")

    col1, col2 = st.columns(2)
    with col1:
        fig = go.Figure()
        for cat, col, couleur in [
            ('Hauturiere', 'nb_hauturiere', '#0077b6'),
            ('Cotiere',    'nb_cotiere',    '#1a7a5a'),
            ('Artisanale', 'nb_artisanale', '#fd7e14'),
        ]:
            fig.add_trace(go.Bar(name=cat, x=flotte['Port'],
                                 y=flotte[col], marker_color=couleur))
        fig.update_layout(title="Flotte par Port 2024",
                          barmode='group', height=400, template='plotly_white')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = go.Figure()
        for cat, col, couleur in [
            ('Semi-Conserve', 'semi_conserve', '#0077b6'),
            ('Conserve',      'conserve',      '#1a7a5a'),
            ('Congelation',   'congelation',   '#ff7f0e'),
            ('Farine/Huile',  'farine_huile',  '#e63946'),
            ('Autres',        'autres',        '#9467bd'),
        ]:
            fig.add_trace(go.Bar(name=cat, x=transform['Port'],
                                 y=transform[col], marker_color=couleur))
        fig.update_layout(title="Transformation par Port 2024",
                          barmode='stack', height=400, template='plotly_white')
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Detail Flotte")
    st.dataframe(flotte, use_container_width=True)
    st.subheader("Detail Transformation")
    st.dataframe(transform, use_container_width=True)


# ═══════════════════════════════════════════
# PAGE 6 — PREDICTIONS LSTM
# ═══════════════════════════════════════════

elif "Prévisions du Marché" in page:
    st.title("Predictions LSTM — 2026 et 2027")
    st.info("3 modeles LSTM entraines separement — Precision ~96%")

    col1, col2, col3 = st.columns(3)
    col1.metric("Tan-Tan 2026",   "100 749 T", "+8.3% vs 2025")
    col2.metric("Sidi Ifni 2026", "60 624 T",  "+129% vs 2025")
    col3.metric("Total 2026",     "203 391 T", "+70% vs 2025")

    st.divider()
    annees_hist = serie['Annee'].tolist()
    fig = go.Figure()

    for nom, col, pred_2026, pred_2027, couleur in [
        ('Tan-Tan',      'TanTan_Volume_T',   100749, 103885, '#0077b6'),
        ('Sidi Ifni',    'SidiIfni_Volume_T', 60624,  57047,  '#e63946'),
        ('Total Region', 'Total_Volume_T',    203391, 195882, '#1a7a5a'),
    ]:
        hist = serie[col].tolist()
        fig.add_trace(go.Scatter(
            x=annees_hist, y=hist, name=f"{nom} (reel)",
            mode='lines+markers',
            line=dict(color=couleur, width=3), marker=dict(size=8)
        ))
        fig.add_trace(go.Scatter(
            x=[annees_hist[-1], 2026, 2027],
            y=[hist[-1], pred_2026, pred_2027],
            name=f"{nom} (predit)", mode='lines+markers',
            line=dict(color=couleur, width=3, dash='dash'),
            marker=dict(size=10, symbol='star')
        ))

    fig.add_vrect(x0=2025.5, x1=2027.5,
                  fillcolor='rgba(200,200,200,0.15)',
                  layer='below', line_width=0)
    fig.update_layout(title="Predictions LSTM par Port",
                      height=500, template='plotly_white',
                      hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)


# ═══════════════════════════════════════════
# PAGE 7 — AIDE A LA DECISION
# ═══════════════════════════════════════════

elif "Aide" in page:
    st.markdown("""
    <div style='background:linear-gradient(#023047,#219ebc,#00b4d8);
                padding:25px;border-radius:15px;color:white;
                text-align:center;margin-bottom:25px;'>
        <h1>Systeme d'Aide a la Decision</h1>
        <p>Investissement dans le Secteur Halieautique — CRI Guelmim</p>
    </div>
    """, unsafe_allow_html=True)

    from sklearn.preprocessing import MinMaxScaler

    secteurs = pd.DataFrame({
        'Secteur': ['Peche Pelagique Industrielle','Peche Cephalopodes',
                    'Transformation Conserve','Farine Huile Poisson',
                    'Aquaculture Offshore','Peche Poisson Blanc',
                    'Aquaculture Terre','Peche Crustaces'],
        'Port': ['Tan-Tan','Sidi Ifni','Tan-Tan','Tan-Tan',
                 'Sidi Ifni','Tan-Tan','Tan-Tan','Tan-Tan'],
        'Rentabilite': [9,8,7,8,7,6,5,7],
        'Croissance':  [9,9,6,7,8,7,4,6],
        'Risque':      [4,3,5,3,6,5,6,4],
        'Emploi':      [9,7,6,8,5,6,4,7],
        'Budget_Min':  [1_000_000,300_000,2_000_000,3_000_000,
                        1_500_000,200_000,1_000_000,150_000]
    })
    secteurs['Score_Risque_Inv'] = 10 - secteurs['Risque']
    secteurs['Score_Global'] = (
        secteurs['Rentabilite']*0.35 + secteurs['Croissance']*0.30 +
        secteurs['Score_Risque_Inv']*0.20 + secteurs['Emploi']*0.15
    ).round(2)
    scaler = MinMaxScaler(feature_range=(0,100))
    secteurs['Score_100'] = scaler.fit_transform(
        secteurs[['Score_Global']]).round(1).flatten()
    secteurs['Recommandation'] = secteurs['Score_100'].apply(
        lambda x: 'Fortement recommande' if x >= 70
        else ('Recommande' if x >= 45 else 'Risque'))

    col1, col2, col3 = st.columns(3)
    with col1:
        budget = st.slider("Budget (DH)", 100_000, 5_000_000,
                           500_000, 50_000, format="%d DH")
    with col2:
        risque = st.radio("Tolerance risque", ["faible","moyen","eleve"], index=1)
    with col3:
        preference = st.selectbox("Preference",
            ["Aucune","Pelagique","Cephalopodes","Transformation",
             "Aquaculture","Poisson Blanc","Crustaces"])

    if st.button("Analyser et Recommander", use_container_width=True):
        df = secteurs.copy()
        risque_map = {'faible':4,'moyen':6,'eleve':10}
        df = df[df['Risque'] <= risque_map[risque]]
        if preference != "Aucune":
            df_pref = df[df['Secteur'].str.contains(preference, case=False)]
            if len(df_pref) > 0:
                df = df_pref
        df = df[df['Budget_Min'] <= budget]

        if len(df) == 0:
            st.error("Aucun secteur ne correspond — augmentez le budget !")
        else:
            top = df.nlargest(3,'Score_100').reset_index(drop=True)
            st.markdown("### Recommandations")
            for i, row in top.iterrows():
                roi = (row['Rentabilite']/10)*0.25
                gains = [budget*roi*(1+0.1*an) for an in range(1,4)]
                bg = '#d4edda' if row['Score_100']>=70 else '#fff3cd' if row['Score_100']>=45 else '#f8d7da'
                st.markdown(f"""
                <div style='background:{bg};padding:15px;border-radius:10px;
                            margin-bottom:10px;border-left:5px solid #0a3d2e;'>
                    <b>Recommandation #{i+1} — {row['Secteur']}</b><br>
                    Port : {row['Port']} | Score : {row['Score_100']}/100 |
                    ROI/an : {roi*100:.1f}% | {row['Recommandation']}<br>
                    Gains : An1={gains[0]:,.0f} DH | An2={gains[1]:,.0f} DH |
                    An3={gains[2]:,.0f} DH | Total={sum(gains):,.0f} DH
                </div>
                """, unsafe_allow_html=True)

            # Calcul gains pour PDF
            gains_totaux = []
            for _, r in top.iterrows():
                roi_r = (r['Rentabilite']/10)*0.25
                gains_r = [budget*roi_r*(1+0.1*an) for an in range(1,4)]
                gains_totaux.append(sum(gains_r))

            # Bouton PDF
            st.divider()
            st.markdown("### Telecharger le Rapport PDF")
            pdf_bytes = generer_pdf_bytes(
                nom_invest=name,
                budget=budget,
                risque=risque,
                preference=preference,
                top=top,
                gains_list=gains_totaux
            )
            st.download_button(
                label="Telecharger mon Rapport PDF",
                data=pdf_bytes,
                file_name=f"rapport_{name}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

            # Sauvegarder dans MySQL
            engine = get_engine()
            rec = pd.DataFrame([{
                'nom_investisseur': name,
                'budget_dh': budget,
                'tolerance_risque': risque,
                'preference': preference,
                'secteur_recommande': top.iloc[0]['Secteur'],
                'score': top.iloc[0]['Score_100'],
                'roi_estime': (top.iloc[0]['Rentabilite']/10)*0.25*100,
                'gain_estime_3ans': gains_totaux[0] if gains_totaux else 0
            }])
            rec.to_sql('recommandations', engine, if_exists='append', index=False)
            st.success("Recommandation sauvegardee dans MySQL !")


# ═══════════════════════════════════════════
# PAGE 8 — CARTE
# ═══════════════════════════════════════════

elif "Visualisation Geographique" in page:
    st.title("Carte des Ports — Region Guelmim")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Tan-Tan", "93 063 T", "+65%")
        st.metric("Valeur",  "1 046 MKDH", "+34%")
        st.metric("Marins",  "8 500", "directs")
    with col2:
        st.metric("Sidi Ifni", "26 427 T", "-58%")
        st.metric("Valeur",    "193 MKDH", "-30%")
        st.metric("Marins",    "3 200", "directs")

    try:
        import pydeck as pdk
        ports = pd.DataFrame({
            'nom':    ['Port Tan-Tan', 'Port Sidi Ifni'],
            'lat':    [28.4333, 29.3833],
            'lon':    [-11.1333, -10.1667],
            'volume': [93063, 26427],
            'couleur':[[0,119,182,200],[230,57,70,200]],
            'rayon':  [30000, 15000],
        })
        layer = pdk.Layer("ScatterplotLayer", data=ports,
            get_position='[lon, lat]', get_color='couleur',
            get_radius='rayon', pickable=True)
        view = pdk.ViewState(latitude=28.9, longitude=-10.7, zoom=6, pitch=30)
        st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view,
            tooltip={"text": "{nom}\n{volume} T"}))
    except:
        st.info("Tan-Tan : 28.4N, 11.1W | Sidi Ifni : 29.4N, 10.2W")
elif "Conseiller Intelligent" in page:
    from chatbot_peche import page_chatbot
    page_chatbot()
elif "Sentiment" in page:
    engine = get_engine()
    df_sent = pd.read_sql(
        "SELECT * FROM analyse_sentiment", engine)

    st.markdown("""
    <div class='main-header'>
        <h1> Analyse de Sentiment</h1>
        <p>Evaluation automatique du climat économique halieutique</p>
    </div>
    """, unsafe_allow_html=True)

    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🟢 Positifs",
                len(df_sent[df_sent['sentiment']=='Positif']))
    col2.metric("🔴 Négatifs",
                len(df_sent[df_sent['sentiment']=='Negatif']))
    col3.metric("🟡 Neutres",
                len(df_sent[df_sent['sentiment']=='Neutre']))
    col4.metric("📄 Total textes", len(df_sent))

    st.divider()

    # Graphiques
    col1, col2 = st.columns(2)
    with col1:
        import plotly.express as px
        fig = px.pie(df_sent, names='sentiment',
                     color_discrete_map={
                         'Positif':'#0077b6',
                         'Negatif':'#e63946',
                         'Neutre': '#fd7e14'
                     },
                     title="Distribution des Sentiments",
                     hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.bar(df_sent, x='port', y='score',
                     color='sentiment',
                     color_discrete_map={
                         'Positif':'#0077b6',
                         'Negatif':'#e63946',
                         'Neutre': '#fd7e14'
                     },
                     title="Score par Port",
                     barmode='group')
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Graphique scores
    fig = px.bar(df_sent, x='score', y='source',
                 color='sentiment',
                 orientation='h',
                 color_discrete_map={
                     'Positif':'#0077b6',
                     'Negatif':'#e63946',
                     'Neutre': '#fd7e14'
                 },
                 title="Score de Sentiment par Source")
    fig.add_vline(x=50, line_dash="dash",
                  line_color="black",
                  annotation_text="Neutre")
    st.plotly_chart(fig, use_container_width=True)

    # Tableau détaillé
    st.subheader("📋 Détail des Analyses — MySQL")
    st.dataframe(
        df_sent[['source','port','sentiment',
                 'score','texte_extrait']],
        use_container_width=True
    )