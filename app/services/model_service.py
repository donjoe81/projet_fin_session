from functools import lru_cache

from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from app.services.data import get_data_frame


SEED = 5103

NUMERIC_FEATURES = ["tenure", "MonthlyCharges"]
CATEGORICAL_FEATURES = ["Contract"]
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES


def compute_metrics(y_true, predictions, probabilities):
    return {
        "accuracy": float(accuracy_score(y_true, predictions)),
        "precision": float(
            precision_score(y_true, predictions, zero_division=0)
        ),
        "recall": float(
            recall_score(y_true, predictions, zero_division=0)
        ),
        "f1": float(
            f1_score(y_true, predictions, zero_division=0)
        ),
        "roc_auc": float(
            roc_auc_score(y_true, probabilities)
        ),
        "confusion_matrix": confusion_matrix(
            y_true,
            predictions,
            labels=[0, 1],
        ).tolist(),
    }


@lru_cache(maxsize=1)
def train_model():
    df = get_data_frame()

    X = df[FEATURES]
    y = df["Churn"].map({"No": 0, "Yes": 1})

    # 20 % réservés au test final.
    X_dev, X_test, y_dev, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        stratify=y,
        random_state=SEED,
    )

    # 25 % des 80 % restants = 20 % du total.
    X_train, X_val, y_train, y_val = train_test_split(
        X_dev,
        y_dev,
        test_size=0.25,
        stratify=y_dev,
        random_state=SEED,
    )

    numeric_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])

    categorical_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(
            drop="first",
            handle_unknown="ignore",
        )),
    ])

    preprocessor = ColumnTransformer([
        ("numeric", numeric_pipeline, NUMERIC_FEATURES),
        ("categorical", categorical_pipeline, CATEGORICAL_FEATURES),
    ])

    model = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", LogisticRegression(
            max_iter=1000,
            random_state=SEED,
        )),
    ])

    # Imputation, standardisation et encodage sont ajustés
    # exclusivement à partir des clients d'entraînement.
    model.fit(X_train, y_train)

    probabilities = model.predict_proba(X_val)[:, 1]
    predictions = (probabilities >= 0.5).astype(int)

    # Référence : prédire systématiquement la classe majoritaire.
    baseline = DummyClassifier(strategy="most_frequent")
    baseline.fit(X_train, y_train)

    report = {
        "train_size": len(X_train),
        "validation_size": len(X_val),
        "test_size": len(X_test),
        "threshold": 0.5,
        "model": compute_metrics(
            y_val,
            predictions,
            probabilities,
        ),
        "baseline": compute_metrics(
            y_val,
            baseline.predict(X_val),
            baseline.predict_proba(X_val)[:, 1],
        ),
    }



    threshold_comparison = []

    for threshold in [0.20, 0.35, 0.50, 0.65, 0.80]:
        threshold_predictions = (
            probabilities >= threshold
        ).astype(int)

        scores = compute_metrics(
            y_val,
            threshold_predictions,
            probabilities,
        )

        matrix = scores["confusion_matrix"]

        threshold_comparison.append({
            "threshold": threshold,
            "precision": scores["precision"],
            "recall": scores["recall"],
            "f1": scores["f1"],
            "false_positives": matrix[0][1],
            "false_negatives": matrix[1][0],
            "alerts": int(threshold_predictions.sum()),
        })

    report["threshold_comparison"] = threshold_comparison

    # Les clients de test sont conservés sans être évalués ici.
    return model, report, X_test, y_test


def get_validation_report():
    return train_model()[1]