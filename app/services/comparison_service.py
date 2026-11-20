from functools import lru_cache

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


def compare_thresholds(y_true, probabilities):
    """Compare les seuils uniquement sur la validation."""
    rows = []

    for threshold in THRESHOLDS:
        predictions = (probabilities >= threshold).astype(int)

        scores = compute_metrics(
            y_true,
            predictions,
            probabilities,
        )

        matrix = scores["confusion_matrix"]

        rows.append({
            "threshold": threshold,
            "alerts": int(predictions.sum()),
            "precision": scores["precision"],
            "recall": scores["recall"],
            "f1": scores["f1"],
            "false_positives": matrix[0][1],
            "false_negatives": matrix[1][0],
        })

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
def get_model_comparison():
    df = get_data_frame()

    X = df[FEATURES]
    y = df["Churn"].map({"No": 0, "Yes": 1})

    # Même séparation que le modèle initial.
    # Le groupe de test est écarté sans être évalué.
    X_dev, _, y_dev, _ = train_test_split(
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
        predictions = (probabilities >= 0.50).astype(int)

        scores = compute_metrics(
            y_val,
            predictions,
            probabilities,
        )

        results[name] = {
            "metrics_at_050": scores,
            "capacity_comparison": compare_thresholds(
                y_val,
                probabilities,
            ),
        }

    classifier = neural_model.named_steps["classifier"]

    return {
        "evaluation": "Validation complémentaire",
        "train_size": len(X_train),
        "validation_size": len(X_val),
        "features": FEATURES,
        "capacity_rate": CAPACITY_RATE,
        "network": {
            "hidden_layers": [8, 4],
            "activation": "relu",
            "early_stopping": True,
            "iterations": int(classifier.n_iter_),
        },
        "models": results,
    }
