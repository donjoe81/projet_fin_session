from functools import lru_cache

import numpy as np

from sklearn.base import clone
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline

from app.services.data import get_data_frame
from app.services.model_service import (
    FEATURES,
    SEED,
    compute_metrics,
    train_model,
)


THRESHOLDS = [0.20, 0.35, 0.50, 0.65, 0.80]
CAPACITY_RATE = 0.35


def evaluate_at_threshold(y_true, probabilities, threshold):
    """Même calcul pour chaque modèle, sur validation ou test."""
    predictions = (np.asarray(probabilities) >= threshold).astype(int)
    scores = compute_metrics(y_true, predictions, probabilities)
    matrix = scores["confusion_matrix"]
    alerts = int(predictions.sum())
    max_contacts = int(len(y_true) * CAPACITY_RATE)
    return {
        **scores,
        "threshold": float(threshold),
        "alerts": alerts,
        "contact_rate": alerts / len(y_true),
        "max_contacts": max_contacts,
        "capacity_respected": alerts <= max_contacts,
        "false_positives": matrix[0][1],
        "false_negatives": matrix[1][0],
        "true_positives": matrix[1][1],
    }


def compare_thresholds(y_true, probabilities):
    """Compare les seuils uniquement sur la validation."""
    rows = []

    for threshold in THRESHOLDS:
        rows.append(evaluate_at_threshold(y_true, probabilities, threshold))

    max_contacts = int(len(y_true) * CAPACITY_RATE)

    eligible = [
        row for row in rows
        if row["alerts"] <= max_contacts
    ]

    selected = None

    if eligible:
        selected = max(
            eligible,
            key=lambda row: (
                row["recall"],
                row["precision"],
                row["threshold"],
            ),
        )

    return {
        "max_contacts": max_contacts,
        "thresholds": rows,
        "selected": selected,
    }


@lru_cache(maxsize=1)
def _train_comparison():
    df = get_data_frame()

    X = df[FEATURES]
    y = df["Churn"].map({"No": 0, "Yes": 1})

    # Même séparation que le modèle initial.
    # Le test n'est évalué que par get_test_comparison(), sans réglage.
    X_dev, X_test, y_dev, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        stratify=y,
        random_state=SEED,
    )

    X_train, X_val, y_train, y_val = train_test_split(
        X_dev,
        y_dev,
        test_size=0.25,
        stratify=y_dev,
        random_state=SEED,
    )

    # Récupère la régression logistique existante.
    # train_model() n'évalue pas le test final.
    logistic_model, _, _, _ = train_model()

    # clone() crée un prétraitement neuf, non ajusté.
    # Il sera ajusté uniquement sur X_train.
    neural_model = Pipeline([
        (
            "preprocessor",
            clone(logistic_model.named_steps["preprocessor"]),
        ),
        (
            "classifier",
            MLPClassifier(
                hidden_layer_sizes=(8,4),
                activation="relu",
                solver="adam",
                alpha=0.01,
                learning_rate_init=0.001,
                max_iter=1000,
                early_stopping=True,
                validation_fraction=0.15,
                n_iter_no_change=30,
                random_state=SEED,
            ),
        ),
    ])

    neural_model.fit(X_train, y_train)

    models = {
        "logistic_regression": logistic_model,
        "neural_network": neural_model,
    }

    results = {}

    for name, model in models.items():
        probabilities = model.predict_proba(X_val)[:, 1]
        scores = evaluate_at_threshold(y_val, probabilities, 0.50)

        results[name] = {
            "metrics_at_050": scores,
            "capacity_comparison": compare_thresholds(
                y_val,
                probabilities,
            ),
        }

    classifier = neural_model.named_steps["classifier"]

    report = {
        "evaluation": "Validation complémentaire",
        "train_size": len(X_train),
        "validation_size": len(X_val),
        "test_size": len(X_test),
        "dataset": "validation",
        "features": FEATURES,
        "capacity_rate": CAPACITY_RATE,
        "network": {
            "hidden_layers": [8, 4],
            "activation": "relu",
            "early_stopping": True,
            "iterations": int(classifier.n_iter_),
        },
        "models": results,
        "baseline": evaluate_at_threshold(
            y_val, np.full(len(y_val), float(y_train.mode().iloc[0])), 0.50
        ),
    }
    return report, models, X_test, y_test, int(y_train.mode().iloc[0])


def get_model_comparison():
    """Rapport de validation ; aucun score du test n'est consulté ici."""
    return _train_comparison()[0]


@lru_cache(maxsize=1)
def get_test_comparison():
    """Évaluation des deux modèles avec les seuils choisis sur validation.

    Le test a déjà été consulté dans le projet : cette comparaison est
    complémentaire et ne constitue pas une nouvelle évaluation indépendante.
    """
    validation, models, X_test, y_test, majority = _train_comparison()
    results = {}
    for name, model in models.items():
        probabilities = model.predict_proba(X_test)[:, 1]
        choice = validation["models"][name]["capacity_comparison"]["selected"]
        selected = None if choice is None else evaluate_at_threshold(
            y_test, probabilities, choice["threshold"]
        )
        results[name] = {
            "metrics_at_050": evaluate_at_threshold(y_test, probabilities, 0.50),
            "capacity_comparison": {
                "max_contacts": int(len(y_test) * CAPACITY_RATE),
                "thresholds": [],
                "selected": selected,
            },
        }
    return {
        **validation,
        "evaluation": "Comparaison complémentaire sur le test déjà consulté",
        "dataset": "test",
        "models": results,
        "baseline": evaluate_at_threshold(y_test, np.full(len(y_test), float(majority)), 0.50),
    }
