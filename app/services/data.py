from functools import lru_cache
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
CSV_FILE = ROOT / "dataset" / "WA_Fn-UseC_-Telco-Customer-Churn.csv"


@lru_cache(maxsize=1)
def _load_data():
    """Charge et nettoie les données sans modifier le CSV original."""
    df = pd.read_csv(CSV_FILE)

    # Les espaces deviennent des valeurs manquantes.
    df["TotalCharges"] = pd.to_numeric(
        df["TotalCharges"],
        errors="coerce",
    )

    # SeniorCitizen est une catégorie, pas une mesure numérique.
    df["SeniorCitizen"] = df["SeniorCitizen"].map({
        0: "No",
        1: "Yes",
    })

    return df


def get_data_frame():
    # Une copie évite qu'un module modifie les données des autres.
    return _load_data().copy(deep=True)


class MyDataFrame:
    """Conserve la compatibilité avec le code existant."""

    def getMyDataFrame(self):
        return get_data_frame()