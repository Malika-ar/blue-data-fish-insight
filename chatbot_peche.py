"""
=============================================================
 CHATBOT IA — Smart Fisheries Analytics
 CRI Guelmim — Basé sur MySQL (sans API externe)
=============================================================
"""
 
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
import re
 
# ─────────────────────────────────────────
# CONNEXION MYSQL
# ─────────────────────────────────────────
 
engine = create_engine(
    "mysql+pymysql://root:MALIKA2005@localhost:3306/cri_guelmim?charset=utf8mb4"
)
 
# ─────────────────────────────────────────
# CHARGEMENT DONNÉES
# ─────────────────────────────────────────
 
def charger_contexte():
    """Charge toutes les données depuis MySQL pour le contexte."""
    especes = pd.read_sql("""
        SELECT p.nom_port AS Port, e.nom_espece AS Espece,
               f.poids_tonnes AS Volume, f.valeur_kdh AS Valeur,
               f.variation_poids_pct AS Var_Vol,
               f.variation_valeur_pct AS Var_Val
        FROM fait_debarquements f
        JOIN dim_port p ON f.id_port = p.id_port
        JOIN dim_espece e ON f.id_espece = e.id_espece
        JOIN dim_date d ON f.id_date = d.id_date
    """, engine)
 
    serie = pd.read_sql("""
        SELECT annee, tantan_total_t, sidiifni_total_t,
               total_region_t, tantan_total_mkdh,
               sidiifni_total_mkdh, total_region_mkdh
        FROM serie_temporelle ORDER BY annee
    """, engine)
 
    flotte = pd.read_sql("""
        SELECT p.nom_port AS Port,
               f.nb_hauturiere, f.nb_cotiere, f.nb_artisanale
        FROM flotte_peche f
        JOIN dim_port p ON f.id_port = p.id_port
    """, engine)
 
    transform = pd.read_sql("""
        SELECT p.nom_port AS Port, t.total
        FROM transformation t
        JOIN dim_port p ON t.id_port = p.id_port
    """, engine)
 
    return especes, serie, flotte, transform
 
 
# ─────────────────────────────────────────
# MOTEUR DE RÉPONSE INTELLIGENT
# ─────────────────────────────────────────
 
def generer_reponse(question, especes, serie, flotte, transform):
    """Génère une réponse intelligente basée sur les données MySQL."""
 
    q = question.lower().strip()
 
    # ── Salutations ──
    if any(w in q for w in ['bonjour', 'salam', 'salut', 'hello', 'bonsoir']):
        return (
            "👋 **Bonjour !** Je suis votre assistant IA spécialisé dans "
            "les données halieutiques de la région Guelmim.\n\n"
            "Je peux répondre à vos questions sur :\n"
            "-  Les ports et espèces\n"
            "-  Les volumes et valeurs\n"
            "-  Les prédictions 2026-2027\n"
            "-  Les opportunités d'investissement\n\n"
            "Comment puis-je vous aider ?"
        )
 
    # ── Volume par port ──
    if any(w in q for w in ['volume', 'debarquement', 'tonne', 'production', 'quantite']):
        if 'tan' in q or 'tantan' in q:
            vol = especes[especes['Port']=='Tan-Tan']['Volume'].sum()
            var = especes[especes['Port']=='Tan-Tan']['Var_Vol'].mean()
            return (
                f" **Port de Tan-Tan — Volume 2025 :**\n\n"
                f" Volume total : **{vol:,.0f} Tonnes**\n"
                f" Variation vs 2024 : **+{var:.0f}%** (croissance exceptionnelle)\n\n"
                f" Espèce dominante : **Poisson Pélagique** (sardine)\n"
                f" Tan-Tan est le **port n°1** de la région !"
            )
        elif 'sidi' in q or 'ifni' in q:
            vol = especes[especes['Port']=='Sidi Ifni']['Volume'].sum()
            var = especes[especes['Port']=='Sidi Ifni']['Var_Vol'].mean()
            return (
                f" **Port de Sidi Ifni — Volume 2025 :**\n\n"
                f" Volume total : **{vol:,.0f} Tonnes**\n"
                f" Variation vs 2024 : **{var:.0f}%** (baisse importante)\n\n"
                f" Point fort : **Céphalopodes** (+52% volume, +79% valeur)\n"
                f" Situation à surveiller pour le poisson pélagique."
            )
        else:
            vol_tt = especes[especes['Port']=='Tan-Tan']['Volume'].sum()
            vol_si = especes[especes['Port']=='Sidi Ifni']['Volume'].sum()
            total = vol_tt + vol_si
            return (
                f" **Volumes débarqués 2025 — Région Guelmim :**\n\n"
                f" Tan-Tan : **{vol_tt:,.0f} T** (+65%)\n"
                f" Sidi Ifni : **{vol_si:,.0f} T** (-58%)\n"
                f" **Total région : {total:,.0f} T**\n\n"
                f" Part nationale : **~20%** (3ème rang national)"
            )
 
    # ── Valeur marchande ──
    if any(w in q for w in ['valeur', 'prix', 'dirham', 'mdh', 'argent', 'chiffre']):
        val_tt = especes[especes['Port']=='Tan-Tan']['Valeur'].sum() / 1000
        val_si = especes[especes['Port']=='Sidi Ifni']['Valeur'].sum() / 1000
        return (
            f" **Valeurs marchandes 2025 :**\n\n"
            f" Tan-Tan : **{val_tt:,.1f} Millions DH** (+34%)\n"
            f" Sidi Ifni : **{val_si:,.1f} Millions DH** (-30%)\n"
            f" **Total région : {val_tt+val_si:,.1f} Millions DH**\n\n"
            f" Soit **1,239 Milliard DH** au total (+17% vs 2024)"
        )
 
    # ── Espèces ──
    if any(w in q for w in ['espece', 'poisson', 'sardine', 'pelagique', 'blanc']):
        tt = especes[especes['Port']=='Tan-Tan']
        best = tt.loc[tt['Volume'].idxmax()]
        return (
            f" **Espèces par port 2025 :**\n\n"
            f"**Port Tan-Tan :**\n"
            f"- Poisson Pélagique : {tt[tt['Espece'].str.contains('lagique', na=False)]['Volume'].sum():,.0f} T (+86%)\n"
            f"- Poisson Blanc : {tt[tt['Espece'].str.contains('Blanc', na=False)]['Volume'].sum():,.0f} T (+20%)\n"
            f"- Céphalopodes : {tt[tt['Espece'].str.contains('phalo', na=False)]['Volume'].sum():,.0f} T\n\n"
            f"**Port Sidi Ifni :**\n"
            f"-  Céphalopodes : +52% volume, **+79% valeur** ⭐\n"
            f"- Poisson Blanc : +1% valeur\n"
            f"- Pélagique : -60% (baisse importante)"
        )
 
    # ── Céphalopodes / Poulpe ──
    if any(w in q for w in ['poulpe', 'cephalopode', 'mollusque', 'cephalo']):
        si = especes[(especes['Port']=='Sidi Ifni') &
                     (especes['Espece'].str.contains('phalo', na=False))]
        tt = especes[(especes['Port']=='Tan-Tan') &
                     (especes['Espece'].str.contains('phalo', na=False))]
        return (
            f" **Céphalopodes (Poulpe & Mollusques) :**\n\n"
            f"**Sidi Ifni :**\n"
            f"- Volume : {si['Volume'].sum():,.0f} T (+52%)\n"
            f"- Valeur : {si['Valeur'].sum()/1000:,.1f} MKDH (**+79%** 🏆)\n\n"
            f"**Tan-Tan :**\n"
            f"- Volume : {tt['Volume'].sum():,.0f} T\n"
            f"- Valeur : {tt['Valeur'].sum()/1000:,.1f} MKDH (+13%)\n\n"
            f" Le poulpe est l'espèce à **plus fort potentiel** de la région !"
        )
 
    # ── Emplois ──
    if any(w in q for w in ['emploi', 'marin', 'travail', 'poste', 'worker']):
        return (
            f" **Emplois dans le secteur halieutique :**\n\n"
            f"| Port | Emplois directs |\n"
            f"|------|----------------|\n"
            f"|  Tan-Tan | **8 500 marins** |\n"
            f"|  Sidi Ifni | **3 200 marins** |\n"
            f"| **Total** | **11 700+ postes** |\n\n"
            f" Sans compter les emplois indirects dans la transformation,\n"
            f"la logistique et le commerce !"
        )
 
    # ── Prédictions LSTM ──
    if any(w in q for w in ['prediction', 'predit', '2026', '2027', 'futur', 'avenir', 'lstm']):
        derniere = serie.iloc[-1]
        return (
            f" **Prédictions LSTM 2026-2027 :**\n\n"
            f"| Port | 2025 (réel) | 2026 (prédit) | 2027 (prédit) |\n"
            f"|------|------------|--------------|---------------|\n"
            f"| Tan-Tan | 93 063 T | **100 749 T** | **103 885 T** |\n"
            f"| Sidi Ifni | 26 427 T | **60 624 T** | **57 047 T** |\n"
            f"| Total | 119 490 T | **203 391 T** | **195 882 T** |\n\n"
            f" Modèle LSTM entraîné sur 7 ans de données\n"
            f" Précision : **96%** | MAE : 3 956 T"
        )
 
    # ── Flotte ──
    if any(w in q for w in ['flotte', 'bateau', 'navire', 'barque', 'chalutier']):
        return (
            f" **Flotte de pêche 2024 :**\n\n"
            f"**Port de Tan-Tan :**\n"
            f"- Hauturière : 42 navires\n"
            f"- Côtière : 251 unités\n"
            f"- Artisanale : 247 unités\n"
            f"- TJB total : 33 789\n\n"
            f"**Port de Sidi Ifni :**\n"
            f"- Hauturière : 1 navire\n"
            f"- Côtière : 25 unités\n"
            f"- Artisanale : **579 unités** (dominant)\n"
            f"- TJB total : 2 467"
        )
 
    # ── Transformation ──
    if any(w in q for w in ['transformation', 'conserve', 'congelation', 'farine', 'industrie', 'unite']):
        return (
            f" **Établissements de transformation 2024 :**\n\n"
            f"**Tan-Tan (18 unités) :**\n"
            f"- Semi-conserve : 2\n"
            f"- Conserve : 2\n"
            f"- Congélation : 9 ⭐\n"
            f"- Farine/Huile : 4\n"
            f"- Autres : 1\n\n"
            f"**Sidi Ifni (2 unités) :**\n"
            f"- Semi-conserve : 2\n\n"
            f" Tan-Tan domine la transformation industrielle !"
        )
 
    # ── Investissement ──
    if any(w in q for w in ['investir', 'investissement', 'secteur', 'recommand', 'budget', 'roi']):
        return (
            f" **Meilleurs secteurs d'investissement :**\n\n"
            f"| Rang | Secteur | Score | ROI/an |\n"
            f"|------|---------|-------|--------|\n"
            f"|  | Pêche Pélagique Tan-Tan | 100/100 | 22.5% |\n"
            f"|  | Pêche Céphalopodes Sidi Ifni | 88.9/100 | 20% |\n"
            f"|  | Transformation & Conserve | 77.8/100 | 20% |\n\n"
            f" Utilisez la page **Aide à la Décision** pour une\n"
            f"recommandation personnalisée selon votre budget !"
        )
 
    # ── Aquaculture ──
    if any(w in q for w in ['aquaculture', 'elevage', 'offshore']):
        return (
            f" **Potentiel Aquaculture — Région Guelmim :**\n\n"
            f"**Aquaculture à terre :**\n"
            f"- Ras Kebdana (Tan-Tan) : **114 Ha** disponibles\n"
            f"- Sud El Ouatia : **101 Ha** disponibles\n\n"
            f"**Aquaculture offshore :**\n"
            f"- Zone large Sidi Ifni qualifiée par l'INRH\n"
            f"- Élevage poissons & coquillages\n\n"
            f" Score investissement : **50.6/100** — Secteur d'avenir !"
        )
 
    # ── Région / Général ──
    if any(w in q for w in ['region', 'guelmim', 'national', 'maroc', 'total', 'bilan']):
        total_vol = serie.iloc[-1]['total_region_t']
        total_val = serie.iloc[-1]['total_region_mkdh']
        return (
            f" **Bilan Région Guelmim-Oued Noun 2025 :**\n\n"
            f" Volume total : **{total_vol:,.0f} Tonnes**\n"
            f" Valeur totale : **{total_val:,.0f} Millions DH** (+17%)\n"
            f" Part nationale : **~20%** (3ème rang)\n"
            f" Unités industrielles : **25+**\n"
            f" Emplois directs : **11 700+**\n"
            f" Ports principaux : Tan-Tan + Sidi Ifni\n\n"
            f" Croissance soutenue depuis 2019 !"
        )
 
    # ── Évolution historique ──
    if any(w in q for w in ['historique', 'evolution', 'annee', '2019', '2020', '2021', '2022', '2023', '2024']):
        meilleure = serie.loc[serie['total_region_t'].idxmax()]
        return (
            f" **Évolution historique 2019-2025 :**\n\n"
            f"| Année | Volume Total | Valeur |\n"
            f"|-------|-------------|--------|\n"
            + "\n".join([
                f"| {int(r['annee'])} | {r['total_region_t']:,.0f} T | {r['total_region_mkdh']:,.0f} MKDH |"
                for _, r in serie.iterrows()
            ]) +
            f"\n\n🏆 Meilleure année : **{int(meilleure['annee'])}** "
            f"avec {meilleure['total_region_t']:,.0f} T"
        )
 
    # ── Aide / Aide moi ──
    if any(w in q for w in ['aide', 'help', 'question', 'quoi', 'comment', 'que']):
        return (
            f" **Je peux répondre à vos questions sur :**\n\n"
            f" **Volumes** — 'Quel est le volume de Tan-Tan ?'\n"
            f" **Valeurs** — 'Quelle est la valeur marchande ?'\n"
            f" **Espèces** — 'Quelle espèce est la plus rentable ?'\n"
            f" **Emplois** — 'Combien d'emplois dans la région ?'\n"
            f" **Prédictions** — 'Quelles sont les prédictions 2026 ?'\n"
            f" **Flotte** — 'Combien de bateaux à Tan-Tan ?'\n"
            f" **Transformation** — 'Combien d'unités industrielles ?'\n"
            f" **Investissement** — 'Où investir dans la pêche ?'\n"
            f" **Aquaculture** — 'Quel est le potentiel aquacole ?'\n"
            f" **Histoire** — 'Quelle était la production en 2022 ?'"
        )
 
    # ── Réponse par défaut ──
    return (
        f"🤔 Je n'ai pas trouvé de réponse précise pour **'{question}'**.\n\n"
        f"Essayez de poser votre question avec ces mots-clés :\n"
        f"- **volume**, **valeur**, **prix**\n"
        f"- **Tan-Tan**, **Sidi Ifni**, **région**\n"
        f"- **poulpe**, **sardine**, **espèce**\n"
        f"- **emplois**, **marins**, **flotte**\n"
        f"- **prédiction**, **2026**, **LSTM**\n"
        f"- **investissement**, **ROI**, **secteur**\n\n"
        f" Tapez **'aide'** pour voir toutes les questions possibles."
    )
 
 
# ─────────────────────────────────────────
# INTERFACE STREAMLIT
# ─────────────────────────────────────────
 
def page_chatbot():
    """Page chatbot à intégrer dans dashboard_final.py"""
    import streamlit as st
 
    st.markdown("""
    <div style='background: linear-gradient(135deg, #03045e, #0077b6, #00b4d8);
                padding: 25px; border-radius: 15px; color: white;
                text-align: center; margin-bottom: 20px;'>
        <h1> Assistant IA — Smart Fisheries</h1>
        <p>Posez vos questions sur les données halieutiques de la région Guelmim</p>
    </div>
    """, unsafe_allow_html=True)
 
    # Suggestions rapides
    st.markdown("** Questions suggérées :**")
    col1, col2, col3, col4 = st.columns(4)
    q1 = col1.button(" Volume Tan-Tan ?",     use_container_width=True)
    q2 = col2.button(" Données poulpe ?",      use_container_width=True)
    q3 = col3.button(" Prédictions 2026 ?",    use_container_width=True)
    q4 = col4.button(" Où investir ?",         use_container_width=True)
    col5, col6, col7, col8 = st.columns(4)
    q5 = col5.button(" Emplois région ?",      use_container_width=True)
    q6 = col6.button(" Flotte de pêche ?",     use_container_width=True)
    q7 = col7.button(" Transformation ?",      use_container_width=True)
    q8 = col8.button(" Evolution historique ?",use_container_width=True)
 
    # Initialiser historique
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [{
            "role": "assistant",
            "content": (
                "👋 **Bonjour !** Je suis votre assistant IA spécialisé dans "
                "les données halieutiques de la région Guelmim-Oued Noun.\n\n"
                "Je peux répondre à vos questions sur les ports, espèces, "
                "volumes, valeurs, prédictions et investissements.\n\n"
                " Tapez votre question ou cliquez sur un bouton ci-dessus !"
            )
        }]
 
    # Charger données
    especes, serie, flotte, transform = charger_contexte()
 
    # Gérer boutons rapides
    questions_rapides = {
        q1: "Quel est le volume de Tan-Tan ?",
        q2: "Données sur le poulpe ?",
        q3: "Quelles sont les prédictions 2026 ?",
        q4: "Où investir dans la pêche ?",
        q5: "Combien d'emplois dans la région ?",
        q6: "Quelle est la flotte de pêche ?",
        q7: "Combien d'unités de transformation ?",
        q8: "Quelle est l'évolution historique ?",
    }
 
    for btn, question in questions_rapides.items():
        if btn:
            st.session_state.chat_messages.append({"role": "user", "content": question})
            reponse = generer_reponse(question, especes, serie, flotte, transform)
            st.session_state.chat_messages.append({"role": "assistant", "content": reponse})
 
    # Afficher historique
    st.divider()
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
 
    # Input utilisateur
    if prompt := st.chat_input("💬 Posez votre question sur la pêche..."):
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        reponse = generer_reponse(prompt, especes, serie, flotte, transform)
        st.session_state.chat_messages.append({"role": "assistant", "content": reponse})
        with st.chat_message("assistant"):
            st.markdown(reponse)
 
    # Bouton effacer
    if st.button("🗑️ Effacer la conversation", use_container_width=False):
        st.session_state.chat_messages = []
        st.rerun()
 
 
if __name__ == "__main__":
    # Test standalone
    especes, serie, flotte, transform = charger_contexte()
    print("✅ Données chargées !")
    print("\nTest chatbot :")
    questions_test = [
        "Quel est le volume de Tan-Tan ?",
        "Quelles sont les prédictions 2026 ?",
        "Où investir dans la pêche ?"
    ]
    for q in questions_test:
        print(f"\n❓ {q}")
        print(f"🤖 {generer_reponse(q, especes, serie, flotte, transform)[:100]}...")