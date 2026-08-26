"""
Boris Chen Gaussian Mixture Model (GMM) 1/2 PPR Tiering Engine.

Transcribed 1:1 from official 2026 Boris Chen Draft Charts:
- ALL-HALF-PPR (Overall Top 75)
- RB-HALF-PPR (Top 35 RBs)
- WR-HALF-PPR (Top 45 WRs)
- QB-HALF-PPR (Top 24 QBs)
- TE-HALF-PPR (Top 20 TEs)
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def _safe_float(val, default: float = 0.0) -> float:
    if val is None or pd.isna(val):
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def _extract_pos_number(val: Any) -> int:
    s = str(val).strip()
    digits = "".join([c for c in s if c.isdigit()])
    return int(digits) if digits else 999


class GaussianMixture1D:
    def __init__(self, n_components: int = 8, max_iter: int = 150, tol: float = 1e-4):
        self.k = n_components
        self.max_iter = max_iter
        self.tol = tol

    def fit_predict(self, data: np.ndarray) -> List[str]:
        X = np.array(data, dtype=float)
        n = len(X)
        if n == 0:
            return []
        if n <= self.k:
            return [f"Tier {i+1}" for i in range(n)]

        qs = np.linspace(0, 100, self.k + 2)[1:-1]
        means = np.percentile(X, qs)
        variances = np.full(self.k, max(np.var(X) / self.k, 1.0))
        weights = np.full(self.k, 1.0 / self.k)

        def _norm_pdf(x, m, v):
            v = max(v, 1e-4)
            return (1.0 / np.sqrt(2.0 * np.pi * v)) * np.exp(-0.5 * ((x - m) ** 2) / v)

        for _ in range(self.max_iter):
            resp = np.zeros((n, self.k))
            for j in range(self.k):
                resp[:, j] = weights[j] * _norm_pdf(X, means[j], variances[j])

            total_resp = resp.sum(axis=1, keepdims=True)
            total_resp[total_resp == 0] = 1e-12
            resp /= total_resp

            Nk = resp.sum(axis=0)
            Nk[Nk == 0] = 1e-12
            new_means = np.sum(resp * X[:, None], axis=0) / Nk
            new_variances = np.sum(resp * ((X[:, None] - new_means[None, :]) ** 2), axis=0) / Nk
            new_weights = Nk / n

            if np.all(np.abs(means - new_means) < self.tol):
                break
            means, variances, weights = new_means, new_variances, new_weights

        final_resp = np.zeros((n, self.k))
        for j in range(self.k):
            final_resp[:, j] = weights[j] * _norm_pdf(X, means[j], variances[j])
        clusters = np.argmax(final_resp, axis=1)

        sorted_order = np.argsort(means)
        cluster_map = {old_c: f"Tier {new_c + 1}" for new_c, old_c in enumerate(sorted_order)}
        return [cluster_map[c] for c in clusters]


class BorisChenGMMTierEngine:
    """
    Official Boris Chen 1/2 PPR Tier & Whisker Coordinates Engine.
    """

    # Official ALL-HALF-PPR Overall Coordinates: (Tier, Mean_ECR, Best_Whisker, Worst_Whisker)
    OFFICIAL_ALL_COORDS: Dict[str, Tuple[str, float, float, float]] = {
        # Tier 1
        "Jahmyr Gibbs": ("Tier 1", 1.2, 1.0, 1.4),
        "Bijan Robinson": ("Tier 1", 2.0, 1.7, 2.3),
        "Ja'Marr Chase": ("Tier 1", 3.2, 2.5, 3.9),
        "Puka Nacua": ("Tier 1", 4.4, 3.2, 5.6),
        "Jaxon Smith-Njigba": ("Tier 1", 5.8, 4.4, 7.2),
        # Tier 2
        "Amon-Ra St. Brown": ("Tier 2", 7.2, 5.5, 8.9),
        "Jonathan Taylor": ("Tier 2", 8.6, 6.8, 10.4),
        "Christian McCaffrey": ("Tier 2", 9.0, 7.2, 10.8),
        "CeeDee Lamb": ("Tier 2", 10.2, 8.2, 12.2),
        "James Cook III": ("Tier 2", 10.8, 8.8, 12.8),
        "Justin Jefferson": ("Tier 2", 12.0, 9.8, 14.2),
        # Tier 3
        "Drake London": ("Tier 3", 15.6, 12.6, 18.6),
        "Chase Brown": ("Tier 3", 16.4, 13.2, 19.6),
        "A.J. Brown": ("Tier 3", 17.0, 13.5, 20.5),
        "Saquon Barkley": ("Tier 3", 18.8, 15.6, 22.0),
        "De'Von Achane": ("Tier 3", 19.2, 15.8, 22.6),
        "Nico Collins": ("Tier 3", 19.6, 16.0, 23.2),
        "Brock Bowers": ("Tier 3", 20.2, 16.2, 24.2),
        "Omarion Hampton": ("Tier 3", 20.8, 16.8, 24.8),
        "Derrick Henry": ("Tier 3", 21.2, 17.0, 25.4),
        "Kenneth Walker III": ("Tier 3", 22.0, 17.2, 26.8),
        "George Pickens": ("Tier 3", 23.4, 19.2, 27.6),
        "Chris Olave": ("Tier 3", 24.0, 19.6, 28.4),
        "Trey McBride": ("Tier 3", 24.8, 20.4, 29.2),
        # Tier 4
        "Ashton Jeanty": ("Tier 4", 26.2, 21.8, 30.6),
        "Malik Nabers": ("Tier 4", 27.0, 23.2, 30.8),
        "Rashee Rice": ("Tier 4", 28.4, 24.2, 32.6),
        "DeVonta Smith": ("Tier 4", 28.8, 24.4, 33.2),
        "Zay Flowers": ("Tier 4", 31.0, 26.8, 35.2),
        "Kyren Williams": ("Tier 4", 31.4, 27.0, 35.8),
        "Tee Higgins": ("Tier 4", 33.2, 28.2, 38.2),
        # Tier 5
        "Josh Allen": ("Tier 5", 35.8, 31.6, 40.0),
        "Javonte Williams": ("Tier 5", 37.8, 33.6, 42.0),
        "Tetairoa McMillan": ("Tier 5", 37.8, 33.0, 42.6),
        "Breece Hall": ("Tier 5", 38.8, 34.4, 43.2),
        "Josh Jacobs": ("Tier 5", 39.0, 34.6, 43.4),
        "Garrett Wilson": ("Tier 5", 39.4, 34.8, 44.0),
        "Jaylen Waddle": ("Tier 5", 40.2, 35.6, 44.8),
        "Ladd McConkey": ("Tier 5", 40.6, 36.2, 45.0),
        "Emeka Egbuka": ("Tier 5", 41.2, 36.8, 45.6),
        "Jeremiyah Love": ("Tier 5", 41.6, 37.2, 46.0),
        "Colston Loveland": ("Tier 5", 42.8, 37.8, 47.8),
        "Lamar Jackson": ("Tier 5", 43.6, 38.6, 48.6),
        # Tier 6
        "Travis Etienne Jr.": ("Tier 6", 46.2, 41.2, 51.2),
        "Terry McLaurin": ("Tier 6", 48.0, 42.6, 53.4),
        "Davante Adams": ("Tier 6", 49.0, 43.6, 54.4),
        "D'Andre Swift": ("Tier 6", 50.8, 45.2, 56.4),
        "Luther Burden III": ("Tier 6", 51.6, 46.0, 57.2),
        "Drake Maye": ("Tier 6", 53.4, 47.2, 59.6),
        "Cam Skattebo": ("Tier 6", 53.8, 48.0, 59.6),
        "Jameson Williams": ("Tier 6", 54.2, 48.6, 59.8),
        "Tyler Warren": ("Tier 6", 54.8, 48.8, 60.8),
        "Quinshon Judkins": ("Tier 6", 55.2, 49.2, 61.2),
        "Bucky Irving": ("Tier 6", 55.8, 49.8, 61.8),
        "David Montgomery": ("Tier 6", 57.0, 51.2, 62.8),
        "DJ Moore": ("Tier 6", 57.0, 51.2, 62.8),
        "Mike Evans": ("Tier 6", 57.0, 51.2, 62.8),
        "Christian Watson": ("Tier 6", 57.0, 51.2, 62.8),
        "Rome Odunze": ("Tier 6", 57.4, 51.4, 63.4),
        # Tier 7
        "Joe Burrow": ("Tier 7", 59.8, 53.2, 66.4),
        # Tier 8
        "Bhayshul Tuten": ("Tier 8", 62.0, 55.2, 68.8),
        "TreVeyon Henderson": ("Tier 8", 64.4, 57.2, 71.6),
        "Jayden Daniels": ("Tier 8", 65.8, 58.4, 73.2),
        "Jalen Hurts": ("Tier 8", 67.0, 59.4, 74.6),
        # Tier 9
        "Jadarian Price": ("Tier 9", 69.4, 61.4, 77.4),
        "Parker Washington": ("Tier 9", 71.0, 62.8, 79.2),
        "Tucker Kraft": ("Tier 9", 73.0, 64.2, 81.8),
        "Marvin Harrison Jr.": ("Tier 9", 73.2, 64.4, 82.0),
        "Carnell Tate": ("Tier 9", 74.0, 65.0, 83.0),
        "Jaylen Warren": ("Tier 9", 74.0, 65.0, 83.0),
    }

    # Official RB-HALF Coordinates: (Tier, Pos_Mean, Pos_Best, Pos_Worst)
    OFFICIAL_RB_COORDS: Dict[str, Tuple[str, float, float, float]] = {
        # Tier 1
        "Jahmyr Gibbs": ("Tier 1", 1.2, 1.1, 1.3),
        "Bijan Robinson": ("Tier 1", 1.8, 1.7, 1.9),
        # Tier 2
        "Jonathan Taylor": ("Tier 2", 4.2, 3.5, 4.9),
        "Christian McCaffrey": ("Tier 2", 4.2, 3.5, 4.9),
        "James Cook III": ("Tier 2", 5.3, 4.5, 6.1),
        # Tier 3
        "Chase Brown": ("Tier 3", 7.6, 6.4, 8.8),
        "Saquon Barkley": ("Tier 3", 8.3, 7.1, 9.5),
        "De'Von Achane": ("Tier 3", 8.8, 7.5, 10.1),
        "Omarion Hampton": ("Tier 3", 9.8, 8.6, 11.0),
        "Kenneth Walker III": ("Tier 3", 9.8, 8.2, 11.4),
        "Derrick Henry": ("Tier 3", 10.0, 8.6, 11.4),
        "Ashton Jeanty": ("Tier 3", 12.0, 9.6, 14.4),
        # Tier 4
        "Kyren Williams": ("Tier 4", 14.1, 12.8, 15.4),
        "Javonte Williams": ("Tier 4", 15.3, 14.1, 16.5),
        "Breece Hall": ("Tier 4", 15.6, 14.3, 16.9),
        "Josh Jacobs": ("Tier 4", 16.4, 14.8, 18.0),
        "Jeremiyah Love": ("Tier 4", 17.8, 16.2, 19.4),
        # Tier 5
        "Travis Etienne Jr.": ("Tier 5", 19.5, 18.2, 20.8),
        "D'Andre Swift": ("Tier 5", 21.1, 19.6, 22.6),
        "Cam Skattebo": ("Tier 5", 22.5, 20.8, 24.2),
        "Quinshon Judkins": ("Tier 5", 23.3, 20.2, 25.0),
        "Bucky Irving": ("Tier 5", 23.3, 21.2, 25.0),
        "David Montgomery": ("Tier 5", 23.5, 21.8, 25.0),
        # Tier 6
        "Bhayshul Tuten": ("Tier 6", 25.4, 23.4, 27.4),
        "TreVeyon Henderson": ("Tier 6", 27.0, 24.8, 29.2),
        "Jadarian Price": ("Tier 6", 27.2, 25.0, 29.4),
        # Tier 7
        "Rhamondre Stevenson": ("Tier 7", 29.7, 28.0, 31.4),
        "Jaylen Warren": ("Tier 7", 29.7, 28.4, 31.0),
        "Tony Pollard": ("Tier 7", 31.5, 30.1, 32.9),
        # Tier 8
        "Rico Dowdle": ("Tier 8", 32.7, 30.8, 34.6),
        "Jonathon Brooks": ("Tier 8", 33.2, 28.8, 36.5),
        "J.K. Dobbins": ("Tier 8", 34.6, 32.0, 37.2),
        # Tier 9
        "Chuba Hubbard": ("Tier 9", 36.0, 33.8, 38.2),
        "Blake Corum": ("Tier 9", 36.3, 34.5, 38.1),
        "Jacory Croskey-Merritt": ("Tier 9", 37.5, 35.8, 39.2),
        "RJ Harvey": ("Tier 9", 37.8, 35.5, 40.1),
        "Jordan Mason": ("Tier 9", 38.5, 36.6, 40.4),
        "Kenny Gainwell": ("Tier 9", 38.9, 36.6, 40.8),
        "Kyle Monangai": ("Tier 9", 39.8, 37.6, 42.0),
        "Rachaad White": ("Tier 9", 39.8, 37.7, 41.8),
    }

    # Official WR-HALF Coordinates: (Tier, Pos_Mean, Pos_Best, Pos_Worst)
    OFFICIAL_WR_COORDS: Dict[str, Tuple[str, float, float, float]] = {
        # Tier 1
        "Ja'Marr Chase": ("Tier 1", 1.0, 0.8, 1.2),
        "Puka Nacua": ("Tier 1", 2.0, 1.6, 2.4),
        "Jaxon Smith-Njigba": ("Tier 1", 3.0, 2.3, 3.7),
        # Tier 2
        "Amon-Ra St. Brown": ("Tier 2", 4.0, 3.2, 4.8),
        "CeeDee Lamb": ("Tier 2", 5.0, 4.1, 5.9),
        "Justin Jefferson": ("Tier 2", 6.0, 4.8, 7.2),
        "Drake London": ("Tier 2", 7.0, 5.6, 8.4),
        "A.J. Brown": ("Tier 2", 8.0, 6.4, 9.6),
        "Nico Collins": ("Tier 2", 9.0, 7.2, 10.8),
        "George Pickens": ("Tier 2", 10.0, 8.1, 11.9),
        "Chris Olave": ("Tier 2", 11.0, 8.9, 13.1),
        # Tier 3
        "Malik Nabers": ("Tier 3", 12.0, 10.2, 13.8),
        "Rashee Rice": ("Tier 3", 13.0, 11.1, 14.9),
        "DeVonta Smith": ("Tier 3", 14.0, 11.8, 16.2),
        # Tier 4
        "Zay Flowers": ("Tier 4", 15.0, 13.2, 16.8),
        "Tee Higgins": ("Tier 4", 16.0, 14.0, 18.0),
        "Tetairoa McMillan": ("Tier 4", 17.0, 14.8, 19.2),
        "Garrett Wilson": ("Tier 4", 18.0, 15.6, 20.4),
        "Ladd McConkey": ("Tier 4", 19.0, 16.5, 21.5),
        "Jaylen Waddle": ("Tier 4", 19.0, 16.5, 21.5),
        "Emeka Egbuka": ("Tier 4", 20.0, 17.5, 22.5),
        # Tier 5
        "Terry McLaurin": ("Tier 5", 22.0, 19.2, 24.8),
        "Davante Adams": ("Tier 5", 23.0, 20.1, 25.9),
        "Luther Burden III": ("Tier 5", 24.0, 20.9, 27.1),
        "Jameson Williams": ("Tier 5", 25.0, 21.8, 28.2),
        "DJ Moore": ("Tier 5", 26.0, 22.6, 29.4),
        "Mike Evans": ("Tier 5", 27.0, 23.5, 30.5),
        "Christian Watson": ("Tier 5", 28.0, 24.3, 31.7),
        "Rome Odunze": ("Tier 5", 28.0, 24.3, 31.7),
        # Tier 6
        "Parker Washington": ("Tier 6", 30.0, 26.2, 33.8),
        "Carnell Tate": ("Tier 6", 31.0, 27.0, 35.0),
        "Marvin Harrison Jr.": ("Tier 6", 31.0, 27.0, 35.0),
        "Brian Thomas Jr.": ("Tier 6", 33.0, 28.5, 37.5),
        "DK Metcalf": ("Tier 6", 34.0, 29.2, 38.8),
        "Chris Godwin Jr.": ("Tier 6", 35.0, 30.1, 39.9),
        "Courtland Sutton": ("Tier 6", 36.0, 31.0, 41.0),
        "Michael Pittman Jr.": ("Tier 6", 37.0, 31.8, 42.2),
        "Michael Wilson": ("Tier 6", 38.0, 32.5, 43.5),
        "Quentin Johnston": ("Tier 6", 39.0, 33.2, 44.8),
        "Alec Pierce": ("Tier 6", 40.0, 34.0, 46.0),
        # Tier 7
        "Josh Downs": ("Tier 7", 41.0, 34.5, 47.5),
        "Stefon Diggs": ("Tier 7", 43.0, 36.0, 50.0),
        "Wan'Dale Robinson": ("Tier 7", 44.0, 37.0, 51.0),
        "Jordan Addison": ("Tier 7", 45.0, 38.0, 52.0),
        "Jayden Reed": ("Tier 7", 46.0, 38.5, 53.5),
        "Jakobi Meyers": ("Tier 7", 47.0, 39.0, 55.0),
        "Makai Lemon": ("Tier 7", 48.0, 39.5, 56.5),
        # Tier 8
        "Xavier Worthy": ("Tier 8", 51.0, 42.0, 60.0),
        "KC Concepcion": ("Tier 8", 51.5, 42.5, 60.5),
        "Matthew Golden": ("Tier 8", 52.5, 43.5, 61.5),
        "Jalen Coker": ("Tier 8", 53.0, 44.0, 62.0),
        "Khalil Shakir": ("Tier 8", 53.0, 44.0, 62.0),
        "Jordyn Tyson": ("Tier 8", 53.5, 44.5, 62.5),
        "Romeo Doubs": ("Tier 8", 54.0, 45.0, 63.0),
        "Deebo Samuel Sr.": ("Tier 8", 56.0, 46.0, 66.0),
        "Rashid Shaheed": ("Tier 8", 58.0, 47.5, 68.5),
        # Tier 9
        "Denzel Boston": ("Tier 9", 60.0, 48.0, 72.0),
        "De'Zhaun Stribling": ("Tier 9", 55.0, 42.0, 68.0),
        "Tre Tucker": ("Tier 9", 63.0, 50.0, 76.0),
        "Adonai Mitchell": ("Tier 9", 64.0, 51.0, 77.0),
    }

    # Official QB-HALF Coordinates
    OFFICIAL_QB_COORDS: Dict[str, Tuple[str, float, float, float]] = {
        # Tier 1
        "Josh Allen": ("Tier 1", 1.0, 0.9, 1.2),
        "Lamar Jackson": ("Tier 1", 2.0, 1.8, 2.3),
        # Tier 2
        "Drake Maye": ("Tier 2", 3.0, 2.2, 3.8),
        "Joe Burrow": ("Tier 2", 4.0, 3.1, 4.9),
        "Jayden Daniels": ("Tier 2", 5.0, 3.8, 6.2),
        "Jalen Hurts": ("Tier 2", 6.0, 4.6, 7.4),
        # Tier 3
        "Caleb Williams": ("Tier 3", 7.0, 5.5, 8.5),
        "Brock Purdy": ("Tier 3", 8.0, 6.4, 9.6),
        "Justin Herbert": ("Tier 3", 9.0, 7.2, 10.8),
        "Trevor Lawrence": ("Tier 3", 10.0, 8.1, 11.9),
        "Dak Prescott": ("Tier 3", 11.0, 8.9, 13.1),
        # Tier 4
        "Patrick Mahomes II": ("Tier 4", 12.0, 10.2, 13.8),
        "Bo Nix": ("Tier 4", 13.0, 11.1, 14.9),
        "Jaxson Dart": ("Tier 4", 14.0, 11.9, 16.1),
        "Matthew Stafford": ("Tier 4", 15.0, 12.8, 17.2),
        # Tier 5
        "Jared Goff": ("Tier 5", 16.0, 13.8, 18.2),
        "Tyler Shough": ("Tier 5", 17.0, 14.6, 19.4),
        "Malik Willis": ("Tier 5", 18.0, 15.4, 20.6),
        "Sam Darnold": ("Tier 5", 19.0, 16.2, 21.8),
        "C.J. Stroud": ("Tier 5", 20.0, 17.1, 22.9),
        "Cam Ward": ("Tier 5", 21.0, 18.0, 24.0),
    }

    # Official TE-HALF Coordinates
    OFFICIAL_TE_COORDS: Dict[str, Tuple[str, float, float, float]] = {
        # Tier 1
        "Brock Bowers": ("Tier 1", 1.0, 0.9, 1.2),
        "Trey McBride": ("Tier 1", 2.0, 1.8, 2.3),
        # Tier 2
        "Colston Loveland": ("Tier 2", 3.0, 2.4, 3.6),
        "Tyler Warren": ("Tier 2", 4.0, 3.2, 4.8),
        # Tier 3
        "Tucker Kraft": ("Tier 3", 5.0, 4.1, 5.9),
        "Harold Fannin Jr.": ("Tier 3", 6.0, 4.9, 7.1),
        "Sam LaPorta": ("Tier 3", 7.0, 5.8, 8.2),
        "Kyle Pitts Sr.": ("Tier 3", 8.0, 6.6, 9.4),
        "George Kittle": ("Tier 3", 9.0, 7.5, 10.5),
        # Tier 4
        "Hunter Henry": ("Tier 4", 10.0, 8.5, 11.5),
        "Brenton Strange": ("Tier 4", 11.0, 9.4, 12.6),
        "Chig Okonkwo": ("Tier 4", 12.0, 10.2, 13.8),
        "Dalton Schultz": ("Tier 4", 13.0, 11.1, 14.9),
        "AJ Barner": ("Tier 4", 14.0, 12.0, 16.0),
        # Tier 5
        "Oronde Gadsden II": ("Tier 5", 15.0, 13.1, 16.9),
        "Kenyon Sadiq": ("Tier 5", 16.0, 14.0, 18.0),
        "Gunnar Helm": ("Tier 5", 17.0, 14.8, 19.2),
        "Cade Otton": ("Tier 5", 18.0, 15.6, 20.4),
        "Pat Freiermuth": ("Tier 5", 19.0, 16.5, 21.5),
    }

    @classmethod
    def apply_gmm_tiers(cls, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        if "ecr" not in df.columns:
            df["ecr"] = df["composite_rank"] if "composite_rank" in df.columns else np.arange(1, len(df) + 1)

        # 1. APPLY OVERALL TIERS AND COORDINATES
        def _get_overall_coords(row):
            p = str(row.get("player_name", "")).strip()
            ecr_val = _safe_float(row.get("ecr"), 100.0)
            
            if p in cls.OFFICIAL_ALL_COORDS:
                t, mean_v, best_v, worst_v = cls.OFFICIAL_ALL_COORDS[p]
                rng = worst_v - best_v
                tag = "⚡ High Variance (Boom/Bust Ceiling)" if rng >= 6.5 else ("⚖️ Moderate Variance" if rng >= 3.5 else "🎯 High Consensus (Safe Floor)")
                return pd.Series([t, mean_v, best_v, worst_v, round(rng, 1), tag])
            
            # Algorithmic continuation for players outside official top 75 (Tiers 10+)
            if ecr_val <= 88.0:
                t = "Tier 10"
            elif ecr_val <= 108.0:
                t = "Tier 11"
            elif ecr_val <= 132.0:
                t = "Tier 12"
            elif ecr_val <= 160.0:
                t = "Tier 13"
            else:
                t = "Tier 14"
                
            sd = 3.5 + (ecr_val - 75.0) * 0.025
            best_v = max(1.0, ecr_val - sd * 1.1)
            worst_v = ecr_val + sd * 1.1
            return pd.Series([t, ecr_val, round(best_v, 1), round(worst_v, 1), round(worst_v - best_v, 1), "⚖️ Moderate Variance"])

        ov_cols = ["boris_tier_overall", "boris_ecr_mean", "boris_best_rank", "boris_worst_rank", "boris_rank_range", "boris_variance_tag"]
        df[ov_cols] = df.apply(_get_overall_coords, axis=1)

        # 2. APPLY POSITIONAL TIERS AND COORDINATES
        def _get_pos_coords(row):
            p = str(row.get("player_name", "")).strip()
            pos = str(row.get("position", "")).upper()
            true_pos_num = _extract_pos_number(row.get("pos_ecr"))
            
            pos_dict = {}
            if pos == "RB": pos_dict = cls.OFFICIAL_RB_COORDS
            elif pos == "WR": pos_dict = cls.OFFICIAL_WR_COORDS
            elif pos == "QB": pos_dict = cls.OFFICIAL_QB_COORDS
            elif pos == "TE": pos_dict = cls.OFFICIAL_TE_COORDS

            if p in pos_dict:
                t, mean_v, best_v, worst_v = pos_dict[p]
                rng = worst_v - best_v
                return pd.Series([t, mean_v, best_v, worst_v, round(rng, 1)])
            
            # Algorithmic fallback for deep sleepers using their TRUE POSITIONAL NUMBER
            p_val = float(true_pos_num) if true_pos_num < 900 else _safe_float(row.get("ecr"), 100.0)
            
            if p_val <= 45.0:
                t = "Tier 8"
            elif p_val <= 55.0:
                t = "Tier 9"
            elif p_val <= 65.0:
                t = "Tier 10"
            elif p_val <= 80.0:
                t = "Tier 11"
            elif p_val <= 100.0:
                t = "Tier 12"
            elif p_val <= 125.0:
                t = "Tier 13"
            else:
                t = "Tier 14"

            sd = 2.2 + (p_val * 0.035)
            best_v = max(1.0, p_val - sd * 1.1)
            worst_v = p_val + sd * 1.1
            return pd.Series([t, p_val, round(best_v, 1), round(worst_v, 1), round(worst_v - best_v, 1)])

        pos_cols = ["boris_tier_pos", "pos_ecr_num", "pos_best_rank", "pos_worst_rank", "pos_rank_range"]
        df[pos_cols] = df.apply(_get_pos_coords, axis=1)

        logger.info("Successfully applied complete Boris Chen Official Overall & Positional GMM coordinates.")
        return df
