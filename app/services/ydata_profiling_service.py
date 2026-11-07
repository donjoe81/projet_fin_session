from app.services.data import MyDataFrame

from pathlib import Path

import pandas as pd
from ydata_profiling import ProfileReport


# Chemin racine du projet
BASE_DIR = Path(__file__).resolve().parent.parent

# Chemins des fichiers

REPORTS_DIR = BASE_DIR / "reports"
REPORT_PATH = REPORTS_DIR / "profiling_report.html"


def generate_profiling_report() -> Path:
    """
    Génère un rapport YData Profiling au format HTML.
    """

    # Charger les données
    df = MyDataFrame().getMyDataFrame()

    # Créer le dossier reports s'il n'existe pas
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    # Générer le rapport
    profile = ProfileReport(
        df,
        title="Rapport de profilage des données",
        explorative=True
    )

    # Enregistrer le rapport HTML
    profile.to_file(str(REPORT_PATH))

    return REPORT_PATH