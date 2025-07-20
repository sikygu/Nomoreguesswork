import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.discrete.discrete_model import Logit
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
import random
from scipy import stats
import warnings

warnings.filterwarnings('ignore')


np.random.seed(42)
random.seed(42)

file_path = r"xxx\symtrain.xlsx"

df = pd.read_excel(file_path)

independent_vars = ['B', 'COM_RAT', 'Cyclic',
                     'DIT', 'DPT*', 'Inner', 'LCOM','Dcy*',
                    'NOAC', 'NOC', 'PDcy', 'PDpt',
                    'CLOC', 'Command', 'CONS', 'CSA', 'CSO',
                    'Dcy', 'DPT', 'INNER', 'jf', 'JLOC', 'Jm', 'Level',
                    'NOOC', 'NTP', 'OCavg', 'OPavg',
                    'TODO', "String processing", "File operations",
                    "Database operations", "Mathematical calculation", "User Interface",
                    "Business Logic", "Data Structures and Algorithms", "Systems and Tools",
                    "Concurrency and Multithreading", "Exception handling"]

dependent_var = '1-suite-LLM'

print("Data preview:")
print(df.head())

missing_cols = [col for col in independent_vars + [dependent_var] if col not in df.columns]
if missing_cols:
    print(f"Columns not found in file: {missing_cols}")
    raise ValueError("Some columns are missing in the data, please check!")

if not df[dependent_var].isin([0, 1]).all():
    print(f"Dependent variable {dependent_var} is not binary, please check the data!")
    raise ValueError("Dependent variable must be binary (0 or 1)")

print(f"\nDistribution of dependent variable {dependent_var}:")
print(df[dependent_var].value_counts(normalize=True))

print("\nChecking for NaN values in independent variables:")
nan_counts = df[independent_vars].isna().sum()
print(nan_counts[nan_counts > 0])

scaler = StandardScaler()
df_standardized = df.copy()
df_standardized[independent_vars] = scaler.fit_transform(df[independent_vars])

print("\nNaN values in independent variables after standardization:")
nan_counts_after = df_standardized[independent_vars].isna().sum()
print(nan_counts_after[nan_counts_after > 0])


def check_data_distribution(df, variables):
    results = []
    for var in variables:
        data = df[var].dropna()
        if len(data) < 3:
            results.append({
                'Variable': var,
                'Statistic': np.nan,
                'P-value': np.nan,
                'Normal(α=0.05)': np.nan
            })
            continue

        stat, p = stats.shapiro(data)
        results.append({
            'Variable': var,
            'Statistic': stat,
            'P-value': p,
            'Normal(α=0.05)': p > 0.05
        })

    return pd.DataFrame(results)


def check_complete_separation(X, y):
    X_vals = X.values.flatten()
    unique_vals = np.unique(X_vals)
    if len(unique_vals) > 10:
        percentiles = np.percentile(X_vals, [25, 50, 75])
        thresholds = np.unique(percentiles)
    else:
        thresholds = unique_vals

    for threshold in thresholds:
        mask = X_vals >= threshold
        y1 = y[mask]
        y0 = y[~mask]
        if (len(y1) > 0 and len(y0) > 0) and (y1.sum() == len(y1) and y0.sum() == 0):
            return True
        if (len(y1) > 0 and len(y0) > 0) and (y1.sum() == 0 and y0.sum() == len(y0)):
            return True
    return False


def calculate_bootstrap_pvalue(X, y, var_index, n_bootstraps=1000):
    model = fit_logit_model(X, y)
    if model is None:
        return np.nan, np.nan, np.nan, np.nan
    original_coef = model.params[var_index]

    bootstrap_coefs = []

    for _ in range(n_bootstraps):
        indices = np.random.choice(len(X), size=len(X), replace=True)
        X_boot = X[indices]
        y_boot = y[indices]

        try:
            model_boot = fit_logit_model(X_boot, y_boot)
            if model_boot is not None:
                bootstrap_coefs.append(model_boot.params[var_index])
        except:
            continue

    if len(bootstrap_coefs) < 100:
        return np.nan, original_coef, np.nan, np.nan

    bootstrap_coefs = np.array(bootstrap_coefs)
    p_value = 2 * min(
        np.mean(bootstrap_coefs >= abs(original_coef)),
        np.mean(bootstrap_coefs <= -abs(original_coef))
    )
    if p_value == 0:
        p_value = np.finfo(float).eps
    std_err = np.std(bootstrap_coefs)
    lower_ci = np.percentile(bootstrap_coefs, 2.5)
    upper_ci = np.percentile(bootstrap_coefs, 97.5)

    return p_value, original_coef, std_err, (lower_ci, upper_ci)


def fit_logit_model(X, y):
    try:
        model = Logit(y, X).fit(
            disp=0,
            maxiter=1000,
            method='bfgs'
        )
        return model
    except:
        pass

    try:
        model = Logit(y, X).fit(
            disp=0,
            method='firth',
            maxiter=1000
        )
        return model
    except:
        pass

    try:
        X_sk = X[:, 1:] if X.shape[1] > 1 else X
        model_sk = LogisticRegression(
            penalty='l2',
            C=0.1,
            solver='liblinear',
            max_iter=1000,
            random_state=42
        ).fit(X_sk, y)

        class SklearnModelWrapper:
            def __init__(self, coef, intercept):
                self.params = np.array([intercept, coef[0]]) if X.shape[1] > 1 else np.array([coef[0]])

        return SklearnModelWrapper(model_sk.coef_, model_sk.intercept_)
    except:
        pass

    return None


results = []

p_value_method = 'bootstrap'
n_bootstraps = 1000

print("\n=== Data Distribution Check ===")
distribution_results = check_data_distribution(df_standardized, independent_vars)
print("\nNormality Test Results (Shapiro-Wilk Test):")
print(distribution_results)

normal_vars_ratio = distribution_results['Normal(α=0.05)'].mean() * 100
print(f"\nRatio of normally distributed variables: {normal_vars_ratio:.1f}%")

if p_value_method == 'bootstrap':
    print(f"\nUsing bootstrap method ({n_bootstraps} samples) to calculate p-values...")
else:
    print("\nUsing traditional method to calculate p-values")

for var in independent_vars:
    X = df_standardized[[var]].dropna()
    y = df_standardized.loc[X.index, dependent_var]
    X = sm.add_constant(X)

    has_separation = check_complete_separation(X[[var]], y)
    if has_separation:
        print(f"Warning: Complete separation exists for variable {var}, which may cause estimation bias")

    model = fit_logit_model(X, y)
    if model is None:
        print(f"All fitting methods failed for variable {var}")
        results.append({
            'Variable': var,
            'Coefficient': None,
            'Std Error': None,
            'Z Value': None,
            'P-value': None,
            'Odds Ratio': None,
            '95% CI Lower (OR)': None,
            '95% CI Upper (OR)': None,
            'Fitting Method': 'Failed'
        })
        continue

    try:
        coef = model.params[var]
        if hasattr(model, 'bse'):
            std_err = model.bse[var]
            z_value = coef / std_err if std_err != 0 else np.nan
            p_value = model.pvalues[var] if p_value_method == 'traditional' else np.nan
        else:
            std_err = np.nan
            z_value = np.nan
            p_value = np.nan

        if p_value_method == 'bootstrap':
            p_value, coef, std_err, conf_int = calculate_bootstrap_pvalue(
                X.values, y.values, X.columns.get_loc(var), n_bootstraps
            )
        else:
            conf_int = model.conf_int().loc[var].values

        if p_value == 0:
            p_value = np.finfo(float).eps

        odds_ratio = np.exp(coef)
        conf_int_or = np.exp(conf_int) if conf_int is not None else (np.nan, np.nan)

        results.append({
            'Variable': var,
            'Coefficient': coef,
            'Std Error': std_err,
            'Z Value': z_value,
            'P-value': p_value,
            'Odds Ratio': odds_ratio,
            '95% CI Lower (OR)': conf_int_or[0],
            '95% CI Upper (OR)': conf_int_or[1],
            'Fitting Method': 'Firth' if 'firth' in model.method else 'Traditional' if model.method == 'bfgs' else 'Regularized'
        })
    except Exception as e:
        print(f"Failed to extract results for variable {var}: {e}")
        results.append({
            'Variable': var,
            'Coefficient': None,
            'Std Error': None,
            'Z Value': None,
            'P-value': None,
            'Odds Ratio': None,
            '95% CI Lower (OR)': None,
            '95% CI Upper (OR)': None,
            'Fitting Method': 'Partially Failed'
        })

results_df = pd.DataFrame(results)


def get_significance(p_value):
    if pd.isna(p_value):
        return ''
    if p_value < 0.001:
        return '***'
    elif p_value < 0.01:
        return '**'
    elif p_value < 0.05:
        return '*'
    else:
        return ''


results_df['Significance'] = results_df['P-value'].apply(get_significance)


def format_ci(row):
    lower = row['95% CI Lower (OR)']
    upper = row['95% CI Upper (OR)']
    if pd.isna(lower) or pd.isna(upper):
        return 'N/A'
    else:
        return f"[{lower:.2f}, {upper:.2f}]"


results_df['95% CI (OR)'] = results_df.apply(format_ci, axis=1)

columns_order = [
    'Variable', 'Coefficient', 'Std Error', 'Z Value', 'P-value', 'Significance',
    'Odds Ratio', '95% CI (OR)', 'Fitting Method'
]
results_df = results_df[columns_order]

print(f"\nUnivariate Logistic Regression Results (standardized, p-value method: {p_value_method}):")
with pd.option_context(
        'display.float_format',
        lambda x: f'{x:.10e}' if 'P-value' in str(x) else f'{x:.4f}'
):
    print(results_df)

results_df_sorted = results_df.dropna(subset=['Coefficient']).sort_values(by='Coefficient', key=abs, ascending=False)
top_n = min(63, len(results_df_sorted))
if len(results_df_sorted) > top_n:
    results_df_sorted = results_df_sorted.head(top_n)

plt.figure(figsize=(15, 10))

colors = ['#FFD700', '#FFA500', '#FF4500', '#C71585', '#800080', '#4B0082']
cmap = LinearSegmentedColormap.from_list("custom_cmap", colors)

min_coef, max_coef = results_df_sorted['Coefficient'].min(), results_df_sorted['Coefficient'].max()
norm = plt.Normalize(min_coef, max_coef)
colors_mapped = [cmap(norm(val)) for val in results_df_sorted['Coefficient']]

bars = plt.barh(results_df_sorted['Variable'], results_df_sorted['Coefficient'],
                color=colors_mapped, alpha=0.7, edgecolor='white', linewidth=1.5)

for i, bar in enumerate(bars):
    p_value = results_df_sorted.iloc[i]['P-value']
    or_value = results_df_sorted.iloc[i]['Odds Ratio']
    ci_text = results_df_sorted.iloc[i]['95% CI (OR)']
    sig = results_df_sorted.iloc[i]['Significance']

    p_formatted = f"{p_value:.2e}" if not pd.isna(p_value) else "N/A"
    label = f'OR={or_value:.2f} {ci_text}\nP={p_formatted} {sig}'

    plt.text(bar.get_width() + 0.02 if bar.get_width() >= 0 else bar.get_width() - 0.02,
             bar.get_y() + bar.get_height() / 2, label,
             ha='left' if bar.get_width() >= 0 else 'right', va='center',
             color='black', fontsize=7)

plt.title(f'Top {top_n}  Logistic Regression Coefficients (with {dependent_var})\n(Including Convergence Optimization)', fontsize=16, pad=20)
plt.xlabel(' Logistic Regression Coefficient', fontsize=12)
plt.ylabel('Independent Variable', fontsize=12)
plt.grid(True, axis='x', linestyle='--', alpha=0.3)
plt.gca().set_facecolor('#FFFFFF')
plt.gcf().set_facecolor('#FFFFFF')
plt.tight_layout()
plt.savefig(f'logistic-sym{p_value_method}_converged.png', dpi=300)
plt.show()

results_df.to_excel(f"logistic-sym{p_value_method}_converged.xlsx", index=False)
print(f"Results saved to 'logistic-sym{p_value_method}_converged.xlsx' and corresponding image file")