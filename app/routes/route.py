from flask import Blueprint, render_template, jsonify, send_from_directory
from app.services.data_mining_service import get_infos_columns
from app.services.ydata_profiling_service import (
    generate_profiling_report,
    REPORTS_DIR
)
from app.services.data_correlation_service import get_significant_relationships
main_bp=Blueprint('main',__name__)


from app.services.dashboard_service import (
    get_dashboard_summary,
    get_churn_by_contract,
)
from flask import request, abort


from app.services.dashboard_service import (
    get_dashboard_summary,
    get_churn_by_contract,
    get_tenure_distribution,
)

from app.services.model_service import get_validation_report

@main_bp.route("/")
def home():
    contract = request.args.get("contract", "").strip()

    allowed_contracts = {
        "Month-to-month",
        "One year",
        "Two year",
    }

    if contract and contract not in allowed_contracts:
        abort(400, description="Type de contrat inconnu.")

    selected_contract = contract or None

    return render_template(
        "index.html",
        summary=get_dashboard_summary(selected_contract),
        contracts=get_churn_by_contract(selected_contract),
        selected_contract=contract,
        tenure_distribution=get_tenure_distribution(selected_contract),
    )


@main_bp.route("/profiling")
def profiling():

    try:
        generate_profiling_report()

        return render_template(
            "profiling.html"
        )

    except ImportError:
        return render_template(
            "profiling.html",
            erreur="Le module de profilage optionnel n’est pas installé."
        ), 503

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

@main_bp.route("/validation")
def model_validation():
    return render_template(
        "model_validation.html",
        report=get_validation_report(),
    )