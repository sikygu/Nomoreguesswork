import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


def check_data_distribution(df, variables, sample_size=1000):
    if len(df) > sample_size:
        df_sample = df.sample(sample_size, random_state=42)
    else:
        df_sample = df

    normality_results = []

    for var in variables:
        if var in df_sample.columns:
            stat, p = stats.shapiro(df_sample[var].dropna())
            normality_results.append({
                'Variable': var,
                'Statistic': stat,
                'P-value': p,
                'Normal(α=0.05)': p > 0.05
            })

    return pd.DataFrame(normality_results)


def identify_high_correlations(df, variables, threshold=0.8, method='spearman'):
    corr_matrix = df[variables].dropna().corr(method=method)
    high_correlations = []

    for i in range(len(corr_matrix.columns)):
        for j in range(i + 1, len(corr_matrix.columns)):
            if abs(corr_matrix.iloc[i, j]) > threshold:
                high_correlations.append((
                    corr_matrix.columns[i],
                    corr_matrix.columns[j],
                    corr_matrix.iloc[i, j]
                ))

    high_correlations.sort(key=lambda x: abs(x[2]), reverse=True)
    return high_correlations, corr_matrix


def visualize_correlation_matrix(corr_matrix, title="Correlation Matrix"):
    plt.figure(figsize=(15, 12))
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    cmap = sns.diverging_palette(230, 20, as_cmap=True)

    sns.heatmap(corr_matrix, mask=mask, annot=True, fmt=".2f", cmap=cmap,
                square=True, linewidths=.5, cbar_kws={"shrink": .8})

    plt.title(title, fontsize=16)
    plt.tight_layout()
    plt.savefig('correlation_matrix.png', dpi=300)
    plt.show()


def main():
    file_path = r"xxx\symtrain.xlsx"

    try:
        df = pd.read_excel(file_path)
        print(f"Data loaded successfully, {df.shape[0]} rows, {df.shape[1]} columns")
    except Exception as e:
        print(f"Data loading failed: {e}")
        return

    independent_vars =['B', 'COM_RAT', 'Cyclic', 'D',
   'Dcy*', 'DIT', 'DPT*', 'E', 'Inner', 'LCOM', 'Level', 'LOC', 'N',
   'NCLOC', 'NOAC', 'NOC', 'NOIC', 'OCmax', 'PDcy', 'PDpt',
   'STAT', 'TCOM_RAT', 'V', 'WMC', 'CBO', 'CLOC',  'CONS', 'CSA', 'CSO',
   'CSOA', 'Dcy', 'DPT', 'jf', 'JLOC', 'Jm', 'Level*', 'n', 'NAAC', 'NAIC',
   'NOOC', 'NTP', 'OCavg', 'OPavg', 'OSavg', 'OSmax', 'Query', 'RFC', 'TODO',
   'MPC', 'INNER', 'String processing', 'File operations',
   'Database operations', 'Mathematical calculation', 'User Interface',
   'Business Logic', 'Data Structures and Algorithms', 'Systems and Tools',
   'Concurrency and Multithreading', 'Exception handling']


    missing_cols = [col for col in independent_vars if col not in df.columns]
    if missing_cols:
        print(f"Columns not found: {missing_cols}")
        print("Please check the independent variable list!")
        return

    print("\nData preview:")
    print(df.head().to_string())

    print("\n=== Data Distribution Check ===")
    normality_results = check_data_distribution(df, independent_vars)
    print("\nNormality Test Results (Shapiro-Wilk Test):")
    print(normality_results)

    normal_vars_ratio = normality_results['Normal(α=0.05)'].mean() * 100
    print(f"\nRatio of normally distributed variables: {normal_vars_ratio:.1f}%")

    if normal_vars_ratio > 70:
        corr_method = 'pearson'
        print("\nNote: Most variables are normally distributed, using Pearson correlation.")
    else:
        corr_method = 'spearman'
        print("\nNote: Most variables are not normally distributed, using Spearman correlation.")

    print("\n=== Identify Highly Correlated Variable Pairs ===")
    threshold = 0.8
    high_correlations, corr_matrix = identify_high_correlations(df, independent_vars, threshold, corr_method)

    print(f"\nHighly correlated variable pairs (correlation > {threshold}, method: {corr_method}):")
    if high_correlations:
        for var1, var2, corr in high_correlations:
            print(f"{var1} and {var2}: correlation = {corr:.4f}")
    else:
        print("No highly correlated variable pairs found")

    print("\n=== Visualization Analysis ===")

    visualize_correlation_matrix(corr_matrix, f"Correlation Matrix (Method: {corr_method})")

    if high_correlations:
        high_corr_df = pd.DataFrame(high_correlations, columns=['Variable 1', 'Variable 2', 'Correlation'])
        high_corr_df.to_excel(f"high_correlations_{corr_method}.xlsx", index=False)

    print("\n=== Analysis Complete ===")
    print(f"Highly correlated variable pairs saved to 'high_correlations_{corr_method}.xlsx'")
    print("Correlation matrix chart saved to 'correlation_matrix.png'")


if __name__ == "__main__":
    main()