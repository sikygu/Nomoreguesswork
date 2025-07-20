import pandas as pd
import numpy as np

# Read Excel file
file_path = r"C:\Users\17958\Desktop\geminiall_results.xlsx"
df = pd.read_excel(file_path, usecols=['class', 'yes', 'predict', 'project'])

# 1. Project statistics
# Calculate class counts per project
project_stats = df.groupby('project').agg(
    total_classes=('class', 'count'),
    count_0=('predict', lambda x: (x == 0).sum()),
    count_1=('predict', lambda x: (x == 1).sum())
).reset_index()

# Calculate 0:1 ratio and add to statistics
project_stats['0:1'] = np.round(project_stats['count_0'] / project_stats['count_1'], 2)

# 2. Global confusion matrix calculation
# Calculate confusion matrix elements
TN = ((df['yes'] == 0) & (df['predict'] == 0)).sum()
FP = ((df['yes'] == 0) & (df['predict'] == 1)).sum()
FN = ((df['yes'] == 1) & (df['predict'] == 0)).sum()
TP = ((df['yes'] == 1) & (df['predict'] == 1)).sum()

# Calculate support counts
support_0 = (df['yes'] == 0).sum()
support_1 = (df['yes'] == 1).sum()
total = support_0 + support_1


# Calculate classification metrics
def safe_div(a, b):
    return a / b if b != 0 else 0


precision_0 = safe_div(TN, (TN + FN))
recall_0 = safe_div(TN, (TN + FP))
f1_0 = safe_div(2 * precision_0 * recall_0, precision_0 + recall_0)

precision_1 = safe_div(TP, (TP + FP))
recall_1 = safe_div(TP, (TP + FN))
f1_1 = safe_div(2 * precision_1 * recall_1, precision_1 + recall_1)

accuracy = (TN + TP) / total

# Calculate averages
macro_precision = (precision_0 + precision_1) / 2
macro_recall = (recall_0 + recall_1) / 2
macro_f1 = (f1_0 + f1_1) / 2

weighted_precision = (precision_0 * support_0 + precision_1 * support_1) / total
weighted_recall = (recall_0 * support_0 + recall_1 * support_1) / total
weighted_f1 = (f1_0 * support_0 + f1_1 * support_1) / total

print("\nProject Statistics:")
print("{:<15} {:<10} {:<10} {:<10} {:<10}".format(
    "Project", "Total Classes", "Predicted 0", "Predicted 1", "0:1 Ratio"))
for _, row in project_stats.iterrows():
    print("{:<15} {:<10} {:<10} {:<10} {:<10.2f}".format(
        row['project'], row['total_classes'], row['count_0'],
        row['count_1'], row['0:1']))

# Global classification report
print("\nGlobal Classification Report:")
header = f"{'':<11}{'precision':<10}{'recall':<10}{'f1-score':<10}{'support':<10}"
row_0 = f"0.0        {precision_0:<10.2f}{recall_0:<10.2f}{f1_0:<10.2f}{support_0:<10}"
row_1 = f"1.0        {precision_1:<10.2f}{recall_1:<10.2f}{f1_1:<10.2f}{support_1:<10}"
footer_acc = f"\naccuracy       {'':<30}{accuracy:.2f}{total:>14}"
footer_macro = f"macro avg      {macro_precision:<10.2f}{macro_recall:<10.2f}{macro_f1:<10.2f}{total:<10}"
footer_weighted = f"weighted avg   {weighted_precision:<10.2f}{weighted_recall:<10.2f}{weighted_f1:<10.2f}{total:<10}"

print("\n".join([
    header,
    row_0,
    row_1,
    footer_acc,
    footer_macro,
    footer_weighted
]))
