from flask import Blueprint, render_template, jsonify, send_from_directory
from app.services.data_mining_service import get_infos_columns
from app.services.ydata_profiling_service import (
    generate_profiling_report,
    REPORTS_DIR
)
from app.services.data_correlation_service import get_significant_relationships
main_bp=Blueprint('main',__name__)

@main_bp.route('/')
def home():
    return render_template('index.html')


@main_bp.route("/profiling")
def profiling():

    try:
        generate_profiling_report()

        return render_template(
            "profiling.html"
        )

    except Exception:
        current_app.logger.exception(
            "Erreur pendant la génération du rapport."
        )

        return render_template(
            "profiling.html",
            erreur="Impossible de générer le rapport. "
                   "Vérifiez le dataset et les journaux de l'application."
        ), 500


@main_bp.route("/profiling/report")
def afficher_rapport():
    """
    Sert le rapport HTML généré dans le dossier reports.
    """

    return send_from_directory(
        str(REPORTS_DIR),
        "profiling_report.html"
    )

@main_bp.route('/analyse_exploratoire')
def analyse_exploratoire():

    return render_template('analyse_exploratoire.html', infos_columns = get_infos_columns())

@main_bp.route('/correlation_vars')
def correlation_vars():
    return render_template('correlation_vars.html', corr_vars = get_significant_relationships())