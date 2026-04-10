import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from pathlib import Path
import logging

logger = logging.getLogger("api.match")

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = BASE_DIR / "models" / "tennis_model.h5"
CSV_PATH = BASE_DIR / "models" / "atp_tennis.csv"

class MatchPredictor:
    def __init__(self):
        self.model = None
        self.df = None
        self.stats_surface = None
        self.scaler = None
        self.columns = None

    def charger_modele(self):
        # 1. Chargement du modèle Keras
        if self.model is None:
            try:
                self.model = tf.keras.models.load_model(str(MODEL_PATH))
                logger.info(f"Modèle de match chargé depuis {MODEL_PATH}")
            except Exception as e:
                logger.error(f"Erreur chargement modèle h5: {e}")
                # Fallback sur le keras s'il existe
                fallback_path = BASE_DIR / "models" / "tennis_model.keras"
                if fallback_path.exists():
                    self.model = tf.keras.models.load_model(str(fallback_path))
                    logger.info(f"Modèle de match fallback keras chargé depuis {fallback_path}")
                else:
                    raise FileNotFoundError(f"Modèle de match introuvable: {e}")

        # 2. Chargement des données et recalcul du contexte (caler l'exact même scaler que le notebook)
        if self.df is None and CSV_PATH.exists():
            logger.info(f"Calcul des statistiques à partir de {CSV_PATH}...")
            # Lecture du csv
            df = pd.read_csv(str(CSV_PATH), low_memory=False)
            cols_to_keep = ['Surface', 'Player_1', 'Player_2', 'Winner', 'Rank_1', 'Rank_2']
            df = df[cols_to_keep].dropna()
            
            # Target et Loser
            df['target'] = (df['Winner'] == df['Player_1']).astype(int)
            df['Loser'] = np.where(df['Winner'] == df['Player_1'], df['Player_2'], df['Player_1'])
            
            # Historique
            winners = df[['Winner', 'Surface']].copy()
            winners['Victoire'] = 1
            winners.columns = ['Player', 'Surface', 'Victoire']
            
            losers = df[['Loser', 'Surface']].copy()
            losers['Victoire'] = 0
            losers.columns = ['Player', 'Surface', 'Victoire']
            
            historique = pd.concat([winners, losers])
            stats_surface = historique.groupby(['Player', 'Surface'])['Victoire'].agg(['sum', 'count']).reset_index()
            
            # Lissage bayésien
            C = 10 
            M = 0.5 
            stats_surface['win_rate_on_surface'] = (stats_surface['sum'] + C * M) / (stats_surface['count'] + C)
            
            # Injection de l'info dans le df d'entraînement pour reconstruire les bonnes structures
            df = df.merge(stats_surface[['Player', 'Surface', 'win_rate_on_surface']], left_on=['Player_1', 'Surface'], right_on=['Player', 'Surface'], how='left')
            df = df.rename(columns={'win_rate_on_surface': 'p1_surface_win_rate'})
            df = df.drop(columns=['Player']) 
            
            df = df.merge(stats_surface[['Player', 'Surface', 'win_rate_on_surface']], left_on=['Player_2', 'Surface'], right_on=['Player', 'Surface'], how='left')
            df = df.rename(columns={'win_rate_on_surface': 'p2_surface_win_rate'})
            df = df.drop(columns=['Player'])
            
            df['p1_surface_win_rate'] = df['p1_surface_win_rate'].fillna(0.5)
            df['p2_surface_win_rate'] = df['p2_surface_win_rate'].fillna(0.5)
            
            df['surface_affinity_diff'] = df['p1_surface_win_rate'] - df['p2_surface_win_rate']
            df['rank_diff'] = df['Rank_2'] - df['Rank_1']
            
            df_final = pd.get_dummies(df, columns=['Surface'])
            df_final = df_final.drop(columns=['Player_1', 'Player_2', 'Winner', 'Loser'])
            
            y = df_final['target']
            X = df_final.drop('target', axis=1)
            
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            scaler = StandardScaler()
            scaler.fit(X_train)  # On fitte sur les mêmes données que dans le notebook !
            
            # Sauvegarde en mémoire
            self.df = df  # df avant transformation (utile pour get_latest_rank)
            self.stats_surface = stats_surface
            self.scaler = scaler
            self.columns = X.columns
            logger.info("Statistiques et Scaler construits avec succès.")
        elif not CSV_PATH.exists():
            logger.warning(f"Le fichier {CSV_PATH} n'existe pas. Les prédictions sans champs manuels seront impossibles.")

    def predire_match(self, nom_joueur_1: str, nom_joueur_2: str, surface_choisie: str):
        if self.df is None or self.scaler is None:
            raise RuntimeError("Le set de données n'a pas pu être chargé (CSV manquant). Impossible de calculer l'aisance automatiquement.")
            
        def get_latest_rank(player_name):
            r1 = self.df[self.df['Player_1'] == player_name]['Rank_1']
            r2 = self.df[self.df['Player_2'] == player_name]['Rank_2']
            if not r1.empty and not r2.empty:
                return r1.iloc[-1] if r1.index[-1] > r2.index[-1] else r2.iloc[-1]
            elif not r1.empty: return r1.iloc[-1]
            elif not r2.empty: return r2.iloc[-1]
            else: return np.nan
        
        rank_p1 = get_latest_rank(nom_joueur_1)
        rank_p2 = get_latest_rank(nom_joueur_2)
        
        if pd.isna(rank_p1): raise ValueError(f"Erreur : '{nom_joueur_1}' introuvable dans le datset historique !")
        if pd.isna(rank_p2): raise ValueError(f"Erreur : '{nom_joueur_2}' introuvable dans le datset historique !")
        
        def get_surface_win_rate(player_name, surf):
            row = self.stats_surface[(self.stats_surface['Player'] == player_name) & (self.stats_surface['Surface'] == surf)]
            if not row.empty: return row['win_rate_on_surface'].values[0]
            return 0.5 

        win_rate_p1 = get_surface_win_rate(nom_joueur_1, surface_choisie)
        win_rate_p2 = get_surface_win_rate(nom_joueur_2, surface_choisie)

        diff_affinite = win_rate_p1 - win_rate_p2
        diff_classement = rank_p2 - rank_p1

        # Construction du DataFrame d'inférence
        match_data = pd.DataFrame(np.zeros((1, len(self.columns))), columns=self.columns)
        
        # Le modèle attend ces colonnes :
        if 'Rank_1' in match_data.columns: match_data['Rank_1'] = rank_p1
        if 'Rank_2' in match_data.columns: match_data['Rank_2'] = rank_p2
        if 'p1_surface_win_rate' in match_data.columns: match_data['p1_surface_win_rate'] = win_rate_p1
        if 'p2_surface_win_rate' in match_data.columns: match_data['p2_surface_win_rate'] = win_rate_p2
        if 'surface_affinity_diff' in match_data.columns: match_data['surface_affinity_diff'] = diff_affinite
        if 'rank_diff' in match_data.columns: match_data['rank_diff'] = diff_classement
        
        col_surface_name = f'Surface_{surface_choisie}'
        if col_surface_name in match_data.columns:
            match_data[col_surface_name] = 1.0

        match_scaled = self.scaler.transform(match_data)
        
        prob_p1_wins = float(self.model.predict(match_scaled, verbose=0)[0][0])
        
        return {
            "joueur_1": nom_joueur_1,
            "joueur_2": nom_joueur_2,
            "surface": surface_choisie,
            "rank_1_actuel": float(rank_p1),
            "rank_2_actuel": float(rank_p2),
            "win_rate_1_lisse": float(win_rate_p1),
            "win_rate_2_lisse": float(win_rate_p2),
            "gagnant_predit": nom_joueur_1 if prob_p1_wins > 0.5 else nom_joueur_2,
            "probabilite_j1": prob_p1_wins,
            "probabilite_j2": 1.0 - prob_p1_wins
        }

match_predictor = MatchPredictor()
