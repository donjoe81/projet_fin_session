import pandas as pd
import numpy as np
from app.services.data import MyDataFrame
from scipy.stats import (
    pearsonr,
    spearmanr,
    chi2_contingency,
    fisher_exact,
    f_oneway,
    kruskal
)

from itertools import combinations
from statsmodels.stats.multitest import multipletests
from scipy.stats.contingency import association

def detect_variable_types(df):

    numeric_cols = df.select_dtypes(
        include=['number']
    ).columns.tolist()

    categorical_cols = df.select_dtypes(
        include=['object', 'category', 'bool']
    ).columns.tolist()

    return numeric_cols, categorical_cols

def numeric_numeric_test(df, var1, var2):

    data = df[[var1, var2]].dropna()

    if len(data) < 3:
        return []

    if data[var1].nunique() < 2 or data[var2].nunique() < 2:
        return []

    results = []

    # Pearson
    r, p = pearsonr(data[var1], data[var2])

    results.append({
        'Variable_1': var1,
        'Variable_2': var2,
        'Relationship': 'Numeric-Numeric',
        'Test': 'Pearson',
        'Statistic': r,
        'Effect_Size': abs(r),
        'P_value': p,
        'N': len(data)
    })

    # Spearman
    rho, p = spearmanr(data[var1], data[var2])

    results.append({
        'Variable_1': var1,
        'Variable_2': var2,
        'Relationship': 'Numeric-Numeric',
        'Test': 'Spearman',
        'Statistic': rho,
        'Effect_Size': abs(rho),
        'P_value': p,
        'N': len(data)
    })

    return results

def categorical_numeric_test(df, cat_var, num_var):

    data = df[[cat_var, num_var]].dropna()

    groups = [
        group[num_var].values
        for _, group in data.groupby(cat_var)
    ]

    if len(groups) < 2 or len(data) < 3:
        return []

    if data[cat_var].nunique() < 2:
        return []

    results = []

    # ANOVA
    if all(len(g) >= 2 for g in groups):

        f_stat, p_anova = f_oneway(*groups)

        grand_mean = data[num_var].mean()

        ss_between = sum(
            len(g) * (np.mean(g) - grand_mean) ** 2
            for g in groups
        )

        ss_total = np.sum(
            (data[num_var] - grand_mean) ** 2
        )

        eta_squared = (
            ss_between / ss_total
            if ss_total > 0 else np.nan
        )

        results.append({
            'Variable_1': cat_var,
            'Variable_2': num_var,
            'Relationship': 'Categorical-Numeric',
            'Test': 'ANOVA',
            'Statistic': f_stat,
            'Effect_Size': eta_squared,
            'P_value': p_anova,
            'N': len(data)
        })

    # Kruskal-Wallis
    if all(len(g) >= 1 for g in groups):

        h_stat, p_kruskal = kruskal(*groups)

        n = len(data)
        k = len(groups)

        epsilon_squared = max(
            0,
            (h_stat - k + 1) / (n - k)
        ) if n > k else np.nan

        results.append({
            'Variable_1': cat_var,
            'Variable_2': num_var,
            'Relationship': 'Categorical-Numeric',
            'Test': 'Kruskal-Wallis',
            'Statistic': h_stat,
            'Effect_Size': epsilon_squared,
            'P_value': p_kruskal,
            'N': len(data)
        })

    return results

def categorical_categorical_test(df, var1, var2):

    data = df[[var1, var2]].dropna()

    if len(data) < 2:
        return []

    contingency = pd.crosstab(
        data[var1],
        data[var2]
    )

    if contingency.shape[0] < 2 or contingency.shape[1] < 2:
        return []

    chi2, p_chi2, dof, expected = chi2_contingency(
        contingency
    )

    cramers_v = association(
        contingency,
        method='cramer'
    )

    results = []

    results.append({
        'Variable_1': var1,
        'Variable_2': var2,
        'Relationship': 'Categorical-Categorical',
        'Test': 'Chi-square',
        'Statistic': chi2,
        'Effect_Size': cramers_v,
        'P_value': p_chi2,
        'N': len(data)
    })

    # Fisher exact uniquement pour les tableaux 2x2
    if contingency.shape == (2, 2):

        odds_ratio, p_fisher = fisher_exact(
            contingency
        )

        results.append({
            'Variable_1': var1,
            'Variable_2': var2,
            'Relationship': 'Categorical-Categorical',
            'Test': 'Fisher Exact',
            'Statistic': odds_ratio,
            'Effect_Size': np.nan,
            'P_value': p_fisher,
            'N': len(data)
        })

    return results


def analyze_all_correlations(df):
    numeric_cols, categorical_cols = detect_variable_types(df)
    all_results = []
    analyzed_pairs = set()
    # Numeric vs Numeric
    for var1, var2 in combinations(numeric_cols, 2):
        pair = frozenset((var1, var2))
        if pair not in analyzed_pairs:
            analyzed_pairs.add(pair)
            all_results.extend(
                numeric_numeric_test(df, var1, var2)
            )
    # Categorical vs Numeric
    for cat_var in categorical_cols:
        for num_var in numeric_cols:
            pair = frozenset((cat_var, num_var))
            if pair not in analyzed_pairs:
                analyzed_pairs.add(pair)
                all_results.extend(
                    categorical_numeric_test(
                        df, cat_var, num_var
                    )
                )
    # Categorical vs Categorical
    for var1, var2 in combinations(categorical_cols, 2):
        pair = frozenset((var1, var2))
        if pair not in analyzed_pairs:
            analyzed_pairs.add(pair)
            all_results.extend(
                categorical_categorical_test(
                    df, var1, var2
                )
            )
    results_df = pd.DataFrame(all_results)
    if results_df.empty:
        return results_df
    # Élimination des p-values invalides
    results_df = results_df[
        np.isfinite(results_df['P_value'])
    ].copy()

    if results_df.empty:
        return results_df
    # Correction FDR
    results_df['P_adjusted'] = multipletests(
        results_df['P_value'],
        method='fdr_bh'
    )[1]

    results_df['Significant'] = (
        results_df['P_adjusted'] < 0.05
    )

    return results_df.sort_values(
        'P_adjusted'
    ).reset_index(drop=True)


def get_significant_relationships(
    alpha=0.05,
    min_effect_size=0.10
):
    results = analyze_all_correlations(MyDataFrame().getMyDataFrame())
    significant = results[
        (results['P_adjusted'] < alpha) &
        (results['Effect_Size'] >= min_effect_size)
    ].copy()

    return significant.sort_values(
        ['P_adjusted', 'Effect_Size'],
        ascending=[True, False]
    )