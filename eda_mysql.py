"""
=============================================================
 ETAPE 2 — EDA CONNECTÉE À MYSQL
 CRI Guelmim — Smart Fisheries Analytics
=============================================================
Lancer : python eda_mysql.py
=============================================================
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from sqlalchemy import create_engine, text
import os

# ─────────────────────────────────────────
# CONFIGURATION MYSQL
# ─────────────────────────────────────────

DB_CONFIG = {
    "host":     "localhost",
    "port":     3306,
    "user":     "root",
    "password": "MALIKA2005",
    "database": "cri_guelmim"
}

def creer_connexion():
    url = (f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
           f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
           f"?charset=utf8mb4")
    return create_engine(url)


# ─────────────────────────────────────────
# CHARGEMENT DONNÉES DEPUIS MYSQL
# ─────────────────────────────────────────

def charger_donnees(engine):
    print("📥 Chargement des données depuis MySQL...")

    # Données espèces
    especes = pd.read_sql("""
        SELECT
            p.nom_port AS Port,
            e.nom_espece AS Categorie,
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

    # Série temporelle
    serie = pd.read_sql("""
        SELECT annee AS Annee,
               tantan_total_t AS TanTan_Volume_T,
               sidiifni_total_t AS SidiIfni_Volume_T,
               total_region_t AS Total_Volume_T,
               tantan_total_mkdh AS TanTan_Valeur_MKDH,
               sidiifni_total_mkdh AS SidiIfni_Valeur_MKDH,
               total_region_mkdh AS Total_Valeur_MKDH
        FROM serie_temporelle
        ORDER BY annee
    """, engine)

    # Flotte
    flotte = pd.read_sql("""
        SELECT p.nom_port AS Port,
               f.nb_hauturiere, f.nb_cotiere,
               f.nb_artisanale, f.tjb_total
        FROM flotte_peche f
        JOIN dim_port p ON f.id_port = p.id_port
    """, engine)

    # Transformation
    transform = pd.read_sql("""
        SELECT p.nom_port AS Port,
               t.semi_conserve, t.conserve,
               t.congelation, t.farine_huile,
               t.autres, t.total
        FROM transformation t
        JOIN dim_port p ON t.id_port = p.id_port
    """, engine)

    print("✅ Données chargées depuis MySQL !")
    return especes, serie, flotte, transform


# ─────────────────────────────────────────
# GRAPHIQUES
# ─────────────────────────────────────────

def graph_volumes(especes):
    couleurs = {
        'Poisson Pelagique': '#0077b6',
        'Poisson Blanc':     '#2ca02c',
        'Cephalopodes':      '#ff7f0e',
        'Crustaces':         '#d62728'
    }
    fig = make_subplots(rows=1, cols=2,
        subplot_titles=("Port de Tan-Tan", "Port de Sidi Ifni"))

    for i, port in enumerate(['Tan-Tan', 'Sidi Ifni'], start=1):
        df = especes[especes['Port'] == port]
        for _, row in df.iterrows():
            fig.add_trace(go.Bar(
                name=row['Categorie'],
                x=[row['Categorie']],
                y=[row['Poids_2025_T']],
                marker_color=couleurs.get(row['Categorie'], '#7f7f7f'),
                showlegend=(i == 1),
                legendgroup=row['Categorie']
            ), row=1, col=i)

    fig.update_layout(
        title="📦 Volumes Débarqués par Espèce 2025 (Tonnes)",
        barmode='group', height=450, template='plotly_white'
    )
    return fig


def graph_valeurs(especes):
    couleurs = {
        'Poisson Pelagique': '#0077b6',
        'Poisson Blanc':     '#2ca02c',
        'Cephalopodes':      '#ff7f0e',
        'Crustaces':         '#d62728'
    }
    fig = make_subplots(rows=1, cols=2,
        subplot_titles=("Port de Tan-Tan", "Port de Sidi Ifni"))

    for i, port in enumerate(['Tan-Tan', 'Sidi Ifni'], start=1):
        df = especes[especes['Port'] == port]
        for _, row in df.iterrows():
            fig.add_trace(go.Bar(
                name=row['Categorie'],
                x=[row['Categorie']],
                y=[row['Valeur_2025_KDH'] / 1000],
                marker_color=couleurs.get(row['Categorie'], '#7f7f7f'),
                showlegend=(i == 1),
                legendgroup=row['Categorie']
            ), row=1, col=i)

    fig.update_layout(
        title="💰 Valeurs Marchandes par Espèce 2025 (Millions DH)",
        barmode='group', height=450, template='plotly_white'
    )
    return fig


def graph_variations(especes):
    especes = especes.copy()
    especes['Label'] = especes['Port'].str[:2].str.upper() + ' — ' + especes['Categorie']

    fig = make_subplots(rows=1, cols=2,
        subplot_titles=("Variation Volume (%)", "Variation Valeur (%)"))

    for col_idx, col in enumerate(['Var_Poids_pct', 'Var_Valeur_pct'], start=1):
        colors = ['#1a7a5a' if v >= 0 else '#e63946'
                  for v in especes[col]]
        fig.add_trace(go.Bar(
            x=especes[col], y=especes['Label'],
            orientation='h', marker_color=colors,
            showlegend=False
        ), row=1, col=col_idx)

    fig.add_vline(x=0, line_dash="dash", line_color="black", opacity=0.5)
    fig.update_layout(
        title="📈 Variations 2024 → 2025 (%)",
        height=450, template='plotly_white'
    )
    return fig


def graph_serie(serie):
    fig = make_subplots(rows=2, cols=1,
        subplot_titles=("Volume (Tonnes)", "Valeur (Millions DH)"),
        shared_xaxes=True, vertical_spacing=0.12)

    for nom, col_v, col_val, couleur in [
        ('Tan-Tan',      'TanTan_Volume_T',   'TanTan_Valeur_MKDH',   '#0077b6'),
        ('Sidi Ifni',    'SidiIfni_Volume_T', 'SidiIfni_Valeur_MKDH', '#e63946'),
        ('Total Region', 'Total_Volume_T',    'Total_Valeur_MKDH',    '#1a7a5a'),
    ]:
        fig.add_trace(go.Scatter(
            x=serie['Annee'], y=serie[col_v],
            name=nom, mode='lines+markers',
            line=dict(color=couleur, width=3),
            marker=dict(size=8)
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=serie['Annee'], y=serie[col_val],
            name=nom, mode='lines+markers',
            line=dict(color=couleur, width=3),
            marker=dict(size=8), showlegend=False
        ), row=2, col=1)

    fig.update_layout(
        title="🕰️ Évolution Historique 2019-2025 — Région Guelmim",
        height=600, template='plotly_white'
    )
    return fig


def graph_flotte(flotte):
    fig = go.Figure()
    categories = ['Hauturière', 'Côtière', 'Artisanale']
    cols = ['nb_hauturiere', 'nb_cotiere', 'nb_artisanale']
    couleurs = ['#0077b6', '#1a7a5a', '#fd7e14']

    for cat, col, couleur in zip(categories, cols, couleurs):
        fig.add_trace(go.Bar(
            name=cat,
            x=flotte['Port'],
            y=flotte[col],
            marker_color=couleur
        ))

    fig.update_layout(
        title="🚢 Flotte de Pêche par Port 2024",
        barmode='group', height=400, template='plotly_white'
    )
    return fig


def graph_transformation(transform):
    categories = ['Semi-Conserve', 'Conserve', 'Congélation',
                  'Farine/Huile', 'Autres']
    cols = ['semi_conserve', 'conserve', 'congelation',
            'farine_huile', 'autres']
    couleurs = ['#0077b6','#1a7a5a','#ff7f0e','#e63946','#9467bd']

    fig = go.Figure()
    for cat, col, couleur in zip(categories, cols, couleurs):
        fig.add_trace(go.Bar(
            name=cat,
            x=transform['Port'],
            y=transform[col],
            marker_color=couleur
        ))

    fig.update_layout(
        title="🏭 Établissements de Transformation par Port 2024",
        barmode='stack', height=400, template='plotly_white'
    )
    return fig


def graph_camembert(especes):
    fig = make_subplots(rows=1, cols=2,
        specs=[[{'type': 'pie'}, {'type': 'pie'}]],
        subplot_titles=("Tan-Tan — Volume 2025", "Sidi Ifni — Volume 2025"))

    couleurs = ['#0077b6', '#2ca02c', '#ff7f0e', '#d62728']

    for i, port in enumerate(['Tan-Tan', 'Sidi Ifni'], start=1):
        df = especes[especes['Port'] == port]
        fig.add_trace(go.Pie(
            labels=df['Categorie'],
            values=df['Poids_2025_T'],
            marker=dict(colors=couleurs),
            hole=0.35,
            textinfo='label+percent',
            name=port
        ), row=1, col=i)

    fig.update_layout(
        title="🥧 Répartition des Espèces — 2025",
        height=420, template='plotly_white'
    )
    return fig


# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────

def run_eda():
    print("=" * 60)
    print("  EDA MYSQL — ANALYSE PÊCHE CRI GUELMIM")
    print("=" * 60)

    engine = creer_connexion()
    especes, serie, flotte, transform = charger_donnees(engine)

    print(f"\n📊 Données disponibles :")
    print(f"   Espèces    : {len(especes)} lignes")
    print(f"   Série temp : {len(serie)} années")
    print(f"   Flotte     : {len(flotte)} ports")
    print(f"   Transform  : {len(transform)} ports")

    # Générer les graphiques
    os.makedirs("graphs", exist_ok=True)

    figs = {
        "1_volumes":        graph_volumes(especes),
        "2_valeurs":        graph_valeurs(especes),
        "3_variations":     graph_variations(especes),
        "4_serie":          graph_serie(serie),
        "5_flotte":         graph_flotte(flotte),
        "6_transformation": graph_transformation(transform),
        "7_camembert":      graph_camembert(especes),
    }

    for nom, fig in figs.items():
        chemin = os.path.join("graphs", f"{nom}.html")
        fig.write_html(chemin)
        print(f"💾 {chemin}")

    print("\n" + "=" * 60)
    print("  ✅ EDA TERMINÉE — 7 graphiques générés !")
    print("  📂 Ouvre le dossier graphs/ dans Chrome")
    print("=" * 60)


if __name__ == "__main__":
    run_eda()
