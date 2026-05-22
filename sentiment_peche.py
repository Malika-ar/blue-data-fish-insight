"""
=============================================================
 ETAPE 5 — ANALYSE DE SENTIMENT
 CRI Guelmim — Smart Fisheries Analytics
=============================================================
Lancer : python sentiment_peche.py
=============================================================
"""
 
import pandas as pd
import numpy as np
from textblob import TextBlob
from langdetect import detect
from sqlalchemy import create_engine, text
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import os
import re
from datetime import datetime
 
# ─────────────────────────────────────────
# CONNEXION MYSQL
# ─────────────────────────────────────────
 
engine = create_engine(
    "mysql+pymysql://root:MALIKA2005@localhost:3306/cri_guelmim?charset=utf8mb4"
)
 
# ─────────────────────────────────────────
# DONNÉES — TEXTES SUR LA PÊCHE
# ─────────────────────────────────────────
 
TEXTES_PECHE = [
    # Positifs
    {
        "id": 1, "source": "ONP", "date": "2025-01",
        "port": "Tan-Tan",
        "texte": "Croissance exceptionnelle des debarquements au port de Tan-Tan avec une hausse de 65 pourcent des volumes. Les pecheurs enregistrent des resultats historiques cette annee.",
        "type": "Rapport officiel"
    },
    {
        "id": 2, "source": "INRH", "date": "2025-02",
        "port": "Tan-Tan",
        "texte": "La valeur marchande des debarquements a augmente de 34 pourcent. Le secteur halieautique de Tan-Tan connait une excellente performance avec des benefices record.",
        "type": "Rapport scientifique"
    },
    {
        "id": 3, "source": "CRI", "date": "2025-03",
        "port": "Tan-Tan",
        "texte": "Le port de Tan-Tan confirme sa position de leader regional avec une production remarquable de poisson pelagique. Les investissements portent leurs fruits.",
        "type": "Communique CRI"
    },
    {
        "id": 4, "source": "ONP", "date": "2025-04",
        "port": "Sidi Ifni",
        "texte": "Les cephalopodes de Sidi Ifni enregistrent une hausse spectaculaire de 79 pourcent en valeur. Le poulpe devient le moteur economique du port artisanal.",
        "type": "Rapport officiel"
    },
    {
        "id": 5, "source": "Media", "date": "2025-01",
        "port": "Tan-Tan",
        "texte": "Excellent bilan pour la peche industrielle au premier trimestre. Les marins celebrent une saison sans precedent avec des captures importantes.",
        "type": "Presse"
    },
    # Negatifs
    {
        "id": 6, "source": "ONP", "date": "2025-02",
        "port": "Sidi Ifni",
        "texte": "Chute dramatique des debarquements a Sidi Ifni avec une baisse alarmante de 58 pourcent. Les pecheurs expriment leur inquietude face a cette situation critique.",
        "type": "Rapport officiel"
    },
    {
        "id": 7, "source": "INRH", "date": "2025-03",
        "port": "Sidi Ifni",
        "texte": "La diminution severe des stocks de poisson pelagique a Sidi Ifni preoccupe les scientifiques. Une surpeche pourrait etre a l'origine de cette degradation.",
        "type": "Rapport scientifique"
    },
    {
        "id": 8, "source": "Media", "date": "2025-02",
        "port": "Sidi Ifni",
        "texte": "Les pecheurs de Sidi Ifni en difficulte apres une saison desastreuse. La valeur des prises a chute de 30 pourcent causant de graves problemes economiques.",
        "type": "Presse"
    },
    {
        "id": 9, "source": "CRI", "date": "2025-04",
        "port": "Sidi Ifni",
        "texte": "La situation difficile du port de Sidi Ifni necessite une intervention urgente. Les pertes enregistrees menacent les moyens de subsistance de milliers de marins.",
        "type": "Communique CRI"
    },
    {
        "id": 10, "source": "INRH", "date": "2025-01",
        "port": "Sidi Ifni",
        "texte": "Deterioration inquietante des ressources halieutiques. La baisse des captures risque de compromettre l'avenir du secteur si aucune mesure n'est prise.",
        "type": "Rapport scientifique"
    },
    # Neutres
    {
        "id": 11, "source": "ONP", "date": "2025-03",
        "port": "Region",
        "texte": "Le volume total regional se maintient a 119 490 tonnes en 2025. Les deux ports contribuent differemment aux resultats globaux de la region.",
        "type": "Rapport officiel"
    },
    {
        "id": 12, "source": "CRI", "date": "2025-01",
        "port": "Region",
        "texte": "Le secteur halieautique de Guelmim compte 11 700 emplois directs et 25 unites de transformation industrielle reparties entre Tan-Tan et Sidi Ifni.",
        "type": "Communique CRI"
    },
    {
        "id": 13, "source": "INRH", "date": "2025-02",
        "port": "Region",
        "texte": "Les investissements dans les infrastructures portuaires s'elevent a 208 millions de dirhams. Les travaux sont en cours dans les deux ports principaux.",
        "type": "Rapport scientifique"
    },
    {
        "id": 14, "source": "Media", "date": "2025-04",
        "port": "Tan-Tan",
        "texte": "Le port de Tan-Tan dispose de 18 etablissements de transformation dont 9 unites de congelation et 4 unites de farine et huile de poisson.",
        "type": "Presse"
    },
    {
        "id": 15, "source": "ONP", "date": "2025-03",
        "port": "Region",
        "texte": "La region Guelmim represente environ 20 pourcent de la production nationale de peche occupant la troisieme place au niveau du royaume.",
        "type": "Rapport officiel"
    },
]
 
 
# ─────────────────────────────────────────
# ANALYSE DE SENTIMENT
# ─────────────────────────────────────────
 
def analyser_sentiment(texte):
    """Analyse le sentiment d'un texte en français."""
 
    # Mots positifs liés à la pêche
    mots_positifs = [
        'croissance', 'hausse', 'augmente', 'excellent', 'exceptionnel',
        'record', 'remarquable', 'spectaculaire', 'benefices', 'leader',
        'historique', 'celebrent', 'importantes', 'portent', 'confirme',
        'performant', 'positif', 'amelioration', 'succes', 'progression'
    ]
 
    # Mots négatifs liés à la pêche
    mots_negatifs = [
        'chute', 'baisse', 'diminution', 'difficile', 'critique', 'alarmante',
        'dramatique', 'desastreuse', 'preoccupe', 'menacent', 'inquietude',
        'deterioration', 'pertes', 'problemes', 'compromet', 'severe',
        'surpeche', 'degradation', 'urgente', 'negatif', 'grave'
    ]
 
    texte_lower = texte.lower()
 
    # Comptage des mots
    score_pos = sum(1 for mot in mots_positifs if mot in texte_lower)
    score_neg = sum(1 for mot in mots_negatifs if mot in texte_lower)
 
    # TextBlob pour analyse complémentaire
    blob = TextBlob(texte)
    polarity = blob.sentiment.polarity
 
    # Score final combiné
    score_final = (score_pos - score_neg) * 0.4 + polarity * 0.6
 
    # Classification
    if score_final > 0.1:
        sentiment = "Positif"
        emoji = "🟢"
        couleur = "#1a7a5a"
        score_normalise = min(100, 50 + score_final * 100)
    elif score_final < -0.1:
        sentiment = "Negatif"
        emoji = "🔴"
        couleur = "#e63946"
        score_normalise = max(0, 50 + score_final * 100)
    else:
        sentiment = "Neutre"
        emoji = "🟡"
        couleur = "#fd7e14"
        score_normalise = 50
 
    return {
        "sentiment":        sentiment,
        "emoji":            emoji,
        "couleur":          couleur,
        "score":            round(score_normalise, 1),
        "score_pos":        score_pos,
        "score_neg":        score_neg,
        "polarity":         round(polarity, 3),
        "mots_detectes_pos": [m for m in mots_positifs if m in texte_lower],
        "mots_detectes_neg": [m for m in mots_negatifs if m in texte_lower],
    }
 
 
# ─────────────────────────────────────────
# TRAITEMENT COMPLET
# ─────────────────────────────────────────
 
def analyser_tous_textes():
    """Analyse tous les textes et retourne un DataFrame."""
    resultats = []
 
    for item in TEXTES_PECHE:
        analyse = analyser_sentiment(item['texte'])
        resultats.append({
            "id":           item['id'],
            "source":       item['source'],
            "date":         item['date'],
            "port":         item['port'],
            "type":         item['type'],
            "texte":        item['texte'][:80] + "...",
            "sentiment":    analyse['sentiment'],
            "emoji":        analyse['emoji'],
            "score":        analyse['score'],
            "score_pos":    analyse['score_pos'],
            "score_neg":    analyse['score_neg'],
            "polarity":     analyse['polarity'],
            "couleur":      analyse['couleur'],
        })
 
    return pd.DataFrame(resultats)
 
 
# ─────────────────────────────────────────
# SAUVEGARDE DANS MYSQL
# ─────────────────────────────────────────
 
def sauvegarder_mysql(df):
    """Sauvegarde les résultats dans MySQL."""
    try:
        # Créer la table si elle n'existe pas
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS analyse_sentiment (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    source VARCHAR(50),
                    date_rapport VARCHAR(20),
                    port VARCHAR(100),
                    type_source VARCHAR(50),
                    texte_extrait TEXT,
                    sentiment VARCHAR(20),
                    score DECIMAL(5,1),
                    score_positif INT,
                    score_negatif INT,
                    polarity DECIMAL(5,3),
                    date_analyse DATETIME DEFAULT CURRENT_TIMESTAMP
                ) CHARACTER SET utf8mb4
            """))
            conn.commit()
 
        # Insérer les données
        df_mysql = df[['source','date','port','type','texte',
                       'sentiment','score','score_pos','score_neg','polarity']].copy()
        df_mysql.columns = ['source','date_rapport','port','type_source',
                            'texte_extrait','sentiment','score',
                            'score_positif','score_negatif','polarity']
        df_mysql.to_sql('analyse_sentiment', engine,
                        if_exists='replace', index=False)
        print("✅ Résultats sauvegardés dans MySQL — table analyse_sentiment")
    except Exception as e:
        print(f"⚠️  Erreur MySQL : {e}")
 
 
# ─────────────────────────────────────────
# VISUALISATIONS
# ─────────────────────────────────────────
 
def creer_graphiques(df):
    os.makedirs("graphs", exist_ok=True)
 
    # 1. Distribution des sentiments
    distribution = df['sentiment'].value_counts().reset_index()
    distribution.columns = ['Sentiment', 'Nombre']
    couleurs_sent = {
        'Positif': '#1a7a5a',
        'Negatif': '#e63946',
        'Neutre':  '#fd7e14'
    }
    fig1 = go.Figure(go.Pie(
        labels=distribution['Sentiment'],
        values=distribution['Nombre'],
        marker=dict(colors=[couleurs_sent.get(s,'#aaa')
                            for s in distribution['Sentiment']]),
        hole=0.4,
        textinfo='label+percent+value'
    ))
    fig1.update_layout(
        title="Distribution des Sentiments — Textes Halieutiques",
        height=420, template='plotly_white'
    )
    fig1.write_html("graphs/sentiment_distribution.html")
 
    # 2. Sentiment par port
    port_sent = df.groupby(['port','sentiment']).size().reset_index(name='count')
    fig2 = px.bar(port_sent, x='port', y='count', color='sentiment',
                  color_discrete_map=couleurs_sent,
                  title="Sentiments par Port",
                  barmode='group')
    fig2.update_layout(height=420, template='plotly_white')
    fig2.write_html("graphs/sentiment_par_port.html")
 
    # 3. Sentiment par source
    source_sent = df.groupby(['source','sentiment']).size().reset_index(name='count')
    fig3 = px.bar(source_sent, x='source', y='count', color='sentiment',
                  color_discrete_map=couleurs_sent,
                  title="Sentiments par Source (ONP, INRH, CRI, Media)",
                  barmode='stack')
    fig3.update_layout(height=420, template='plotly_white')
    fig3.write_html("graphs/sentiment_par_source.html")
 
    # 4. Score de sentiment par texte
    df_sorted = df.sort_values('score', ascending=True)
    colors = [couleurs_sent.get(s, '#aaa') for s in df_sorted['sentiment']]
    fig4 = go.Figure(go.Bar(
        x=df_sorted['score'],
        y=[f"Texte {i}" for i in df_sorted['id']],
        orientation='h',
        marker_color=colors,
        text=[f"{s} ({sc})" for s, sc in
              zip(df_sorted['sentiment'], df_sorted['score'])],
        textposition='outside'
    ))
    fig4.add_vline(x=50, line_dash="dash", line_color="black",
                   annotation_text="Neutre")
    fig4.update_layout(
        title="Score de Sentiment par Texte (0=Tres Negatif, 100=Tres Positif)",
        height=500, template='plotly_white',
        xaxis=dict(range=[0, 120])
    )
    fig4.write_html("graphs/sentiment_scores.html")
 
    print("✅ 4 graphiques sauvegardés dans graphs/")
 
 
# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────
 
def run_sentiment():
    print("=" * 60)
    print("  ANALYSE DE SENTIMENT — SECTEUR PECHE CRI GUELMIM")
    print("=" * 60)
 
    # Analyse
    print("\n🔍 Analyse des textes en cours...")
    df = analyser_tous_textes()
 
    # Résultats
    print(f"\n✅ {len(df)} textes analysés !")
    print("\n📊 Résultats :")
    print(f"   🟢 Positifs : {len(df[df['sentiment']=='Positif'])} textes")
    print(f"   🔴 Négatifs : {len(df[df['sentiment']=='Negatif'])} textes")
    print(f"   🟡 Neutres  : {len(df[df['sentiment']=='Neutre'])} textes")
 
    print("\n📋 Détail par texte :")
    print("-" * 60)
    for _, row in df.iterrows():
        print(f"  {row['emoji']} [{row['source']}] {row['port']} — "
              f"Score: {row['score']} | {row['sentiment']}")
        print(f"     → {row['texte'][:60]}...")
 
    # Analyse par port
    print("\n📊 Sentiment moyen par port :")
    port_scores = df.groupby('port')['score'].mean().round(1)
    for port, score in port_scores.items():
        emoji = "🟢" if score > 55 else "🔴" if score < 45 else "🟡"
        print(f"   {emoji} {port} : {score}/100")
 
    # Sauvegarde MySQL
    print("\n💾 Sauvegarde dans MySQL...")
    sauvegarder_mysql(df)
 
    # Graphiques
    print("\n📈 Génération des graphiques...")
    creer_graphiques(df)
 
    print("\n" + "=" * 60)
    print("  ✅ ANALYSE DE SENTIMENT TERMINÉE !")
    print("  📂 Graphiques dans graphs/")
    print("  🗄️  Données dans MySQL — table analyse_sentiment")
    print("=" * 60)
 
    return df
 
 
if __name__ == "__main__":
    df_resultats = run_sentiment()