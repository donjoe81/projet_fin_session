from app.services.data import get_data_frame
from statsmodels.stats.proportion import proportion_confint


CONTRACTS = ("Month-to-month", "One year", "Two year")


def filter_clients(contract=None):
    df = get_data_frame()

    if contract is None:
        return df

    if contract not in CONTRACTS:
        raise ValueError("Type de contrat inconnu.")

    return df.loc[df["Contract"].eq(contract)].copy()


def get_dashboard_summary(contract=None):
    df = filter_clients(contract)

    total_clients = len(df)
    departures = int(df["Churn"].eq("Yes").sum())
    ci_low, ci_high = proportion_confint(
        count=departures,
        nobs=total_clients,
        alpha=0.05,
        method="wilson",
    )
    return {
        "total_clients": total_clients,
        "departures": departures,
        "remaining_clients": total_clients - departures,
        "churn_rate": departures / total_clients,
        "median_tenure": float(df["tenure"].median()),
        "mean_monthly_charges": float(df["MonthlyCharges"].mean()),
        "missing_total_charges": int(df["TotalCharges"].isna().sum()),
        "churn_ci_low": float(ci_low),
        "churn_ci_high": float(ci_high),
    }


def get_churn_by_contract(contract=None):
    df = filter_clients(contract)

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



def get_tenure_distribution(contract=None):
    df = filter_clients(contract)

    intervals = [
        (0, 11),
        (12, 23),
        (24, 35),
        (36, 47),
        (48, 59),
        (60, 72),
    ]

    results = []

    for lower, upper in intervals:
        group = df.loc[df["tenure"].between(lower, upper)]

        results.append({
            "label": f"{lower}–{upper} mois",
            "remaining": int(group["Churn"].eq("No").sum()),
            "departures": int(group["Churn"].eq("Yes").sum()),
        })

    return results