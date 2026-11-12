import pandas as pd

from app.services.data import get_data_frame


def get_dashboard_summary():
    df = get_data_frame()

    total_clients = len(df)
    departures = int(df["Churn"].eq("Yes").sum())
    remaining_clients = total_clients - departures

    return {
        "total_clients": total_clients,
        "departures": departures,
        "remaining_clients": remaining_clients,
        "churn_rate": departures / total_clients,
        "median_tenure": float(df["tenure"].median()),
        "mean_monthly_charges": float(df["MonthlyCharges"].mean()),
        "missing_total_charges": int(df["TotalCharges"].isna().sum()),
    }


def get_churn_by_contract():
    df = get_data_frame()

    results = (
        df.assign(departure=df["Churn"].eq("Yes"))
        .groupby("Contract", observed=True)
        .agg(
            total_clients=("departure", "size"),
            departures=("departure", "sum"),
        )
        .reset_index()
    )

    results["churn_rate"] = (
        results["departures"] / results["total_clients"]
    )

    return results.to_dict(orient="records")