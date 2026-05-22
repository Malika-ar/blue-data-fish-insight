"""
=============================================================
 ETAPE 1 — ETL + DATA WAREHOUSE MYSQL (VERSION CORRIGEE)
 CRI Guelmim — Smart Fisheries Analytics
=============================================================
Lancer : python etl_mysql.py
=============================================================
"""

import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text

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
# DÉSACTIVER / ACTIVER LES CLÉS ÉTRANGÈRES
# ─────────────────────────────────────────

def desactiver_fk(engine):
    with engine.connect() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        conn.commit()

def activer_fk(engine):
    with engine.connect() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
        conn.commit()


# ─────────────────────────────────────────
# CHARGEMENT DES TABLES
# ─────────────────────────────────────────

def charger_dim_port(engine):
    data = pd.DataFrame({
        'id_port':                  [1, 2],
        'nom_port':                 ['Tan-Tan', 'Sidi Ifni'],
        'localisation':             ['El Ouatia', 'Sidi Ifni'],
        'type_port':                ['Industriel', 'Artisanal Cotier'],
        'capacite_tjb':             [153417, 12936],
        'nb_unites_transformation': [18, 2],
    })
    data.to_sql('dim_port', engine, if_exists='replace', index=False)
    print(f"✅ dim_port : {len(data)} lignes")


def charger_dim_espece(engine):
    data = pd.DataFrame({
        'id_espece':  [1, 2, 3, 4],
        'nom_espece': ['Poisson Pelagique', 'Poisson Blanc',
                       'Cephalopodes', 'Crustaces'],
        'categorie':  ['Pelagique', 'Demersal',
                       'Mollusque', 'Crustace'],
        'type_peche': ['Hauturier/Cotier', 'Cotier',
                       'Artisanal', 'Artisanal'],
    })
    data.to_sql('dim_espece', engine, if_exists='replace', index=False)
    print(f"✅ dim_espece : {len(data)} lignes")


def charger_dim_date(engine):
    data = pd.DataFrame({
        'id_date':   list(range(1, 8)),
        'annee':     [2019, 2020, 2021, 2022, 2023, 2024, 2025],
        'trimestre': [4, 4, 4, 4, 4, 4, 4],
        'semestre':  [2, 2, 2, 2, 2, 2, 2],
    })
    data.to_sql('dim_date', engine, if_exists='replace', index=False)
    print(f"✅ dim_date : {len(data)} lignes")


def charger_fait_debarquements(engine):
    data = pd.DataFrame({
        'id_port':              [1, 1, 1, 1, 2, 2, 2, 2],
        'id_espece':            [1, 2, 3, 4, 1, 2, 3, 4],
        'id_date':              [7, 7, 7, 7, 7, 7, 7, 7],
        'poids_tonnes':         [73672, 13172, 6,   187,
                                 24855, 949,   608, 14],
        'valeur_kdh':           [311295, 307835, 413552, 13297,
                                 94311,  37331,  58377,  3306],
        'variation_poids_pct':  [86,  20,  7,  -2,
                                 -60, -3,  52, -31],
        'variation_valeur_pct': [92,  28,  13, 42,
                                 -53, 1,   79, -21],
    })
    data.to_sql('fait_debarquements', engine, if_exists='replace', index=False)
    print(f"✅ fait_debarquements : {len(data)} lignes")


def charger_serie_temporelle(engine):
    data = pd.DataFrame({
        'annee':               [2019,    2020,    2021,    2022,     2023,     2024,     2025],
        'tantan_total_t':      [117524,  96664,   122947,  144139,   102722,   56355,    93063],
        'sidiifni_total_t':    [42099,   44306,   48400,   76136,    61521,    63356,    26427],
        'total_region_t':      [159641,  140987,  171369,  220290,   164261,   119591,   119490],
        'tantan_total_mkdh':   [644.255, 525.444, 791.221, 904.993,  853.793,  778,      1046],
        'sidiifni_total_mkdh': [192.754, 168.461, 201.183, 300.371,  283.489,  275.321,  193],
        'total_region_mkdh':   [838.116, 694.677, 993.990, 1206.332, 1138.113, 1052.406, 1239],
    })
    data.to_sql('serie_temporelle', engine, if_exists='replace', index=False)
    print(f"✅ serie_temporelle : {len(data)} lignes")


def charger_flotte(engine):
    data = pd.DataFrame({
        'id_port':       [1,      2],
        'id_date':       [6,      6],
        'nb_hauturiere': [42,     1],
        'nb_cotiere':    [251,    25],
        'nb_artisanale': [247,    579],
        'tjb_total':     [33789,  2467],
        'pm_total':      [153417, 12936],
    })
    data.to_sql('flotte_peche', engine, if_exists='replace', index=False)
    print(f"✅ flotte_peche : {len(data)} lignes")


def charger_transformation(engine):
    data = pd.DataFrame({
        'id_port':       [1,  2],
        'id_date':       [6,  6],
        'semi_conserve': [2,  2],
        'conserve':      [2,  0],
        'congelation':   [9,  0],
        'farine_huile':  [4,  0],
        'autres':        [1,  0],
        'total':         [18, 2],
    })
    data.to_sql('transformation', engine, if_exists='replace', index=False)
    print(f"✅ transformation : {len(data)} lignes")


def charger_securite(engine):
    data = pd.DataFrame({
        'id_port':          [1,    2],
        'id_date':          [6,    6],
        'visites_securite': [656,  551],
        'prescriptions':    [1855, 516],
    })
    data.to_sql('securite', engine, if_exists='replace', index=False)
    print(f"✅ securite : {len(data)} lignes")


# ─────────────────────────────────────────
# VÉRIFICATION
# ─────────────────────────────────────────

def verifier_chargement(engine):
    print("\n📊 Vérification du Data Warehouse :")
    tables = ['dim_port', 'dim_espece', 'dim_date',
              'fait_debarquements', 'serie_temporelle',
              'flotte_peche', 'transformation', 'securite']
    with engine.connect() as conn:
        for table in tables:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.fetchone()[0]
            print(f"   {table:<25} : {count} lignes ✅")


# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────

def run_etl():
    print("=" * 60)
    print("  ETL → DATA WAREHOUSE MYSQL — CRI GUELMIM")
    print("=" * 60)

    print("\n🔌 Connexion à MySQL...")
    try:
        engine = creer_connexion()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Connexion MySQL réussie !")
    except Exception as e:
        print(f"❌ Erreur connexion : {e}")
        return

    # Désactiver les clés étrangères avant le chargement
    print("\n🔓 Désactivation des clés étrangères...")
    desactiver_fk(engine)

    print("\n📥 Chargement des tables...")
    charger_dim_port(engine)
    charger_dim_espece(engine)
    charger_dim_date(engine)
    charger_fait_debarquements(engine)
    charger_serie_temporelle(engine)
    charger_flotte(engine)
    charger_transformation(engine)
    charger_securite(engine)

    # Réactiver les clés étrangères
    print("\n🔒 Réactivation des clés étrangères...")
    activer_fk(engine)

    verifier_chargement(engine)

    print("\n" + "=" * 60)
    print("  ✅ ETL TERMINÉ — Data Warehouse MySQL chargé !")
    print("=" * 60)

    return engine


if __name__ == "__main__":
    run_etl()
