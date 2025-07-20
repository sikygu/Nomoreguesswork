import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score, roc_curve
from imblearn.over_sampling import SMOTE
import matplotlib.pyplot as plt

try:
    file_path = r"C:\Users\17958\Desktop\train_4.0.xlsx"
    data = pd.read_excel(file_path)
    print("Data read successfully. Number of samples:", len(data))

    X = data[['B', 'COM_RAT', 'Cyclic', 'D',
    'Dcy*', 'DIT', 'DPT*', 'E', 'Inner', 'LCOM', 'Level', 'LOC', 'N',
    'NCLOC', 'NOAC', 'NOC', 'NOIC', 'OCmax', 'PDcy', 'PDpt', 'STAT', 'SUB',
    'TCOM_RAT', 'V', 'WMC', 'CBO', 'CLOC', 'Command', 'CONS', 'CSA', 'CSO',
    'CSOA', 'Dcy', 'DPT', 'INNER', 'jf', 'JLOC', 'Jm', 'Level*', 'MPC', 'n',
    'NAAC', 'NAIC', 'NOOC', 'NTP', 'OCavg', 'OPavg', 'OSavg', 'OSmax',
    'Query', 'RFC', 'TODO']]
    y = data['1-suit-LLM']
    X = X.fillna(0)
    y = y.fillna(0)
    if X.isnull().sum().sum() > 0 or y.isnull().sum() > 0:
        raise ValueError("Missing values found in data. Please handle them first!")

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    smote = SMOTE(random_state=42)
    X_train_balanced, y_train_balanced = smote.fit_resample(X_train, y_train)
    print("Number of training samples after SMOTE:", len(X_train_balanced))

    param_grid = {
        'max_depth': [1,2,3, 5, 7,None],
        'learning_rate': [0.1,0.15,0.2,0.21,0.22,0.23,0.24,0.25, 0.3],
        'n_estimators': [100, 150,200,220,240, 300],
        'min_child_weight': [1, 2,3, 5],
        'subsample': [0.8, 0.9,0.92,0.94,0.95,0.96,0.97,0.98,1.0,1.5]
    }

    xgb = XGBClassifier(eval_metric='logloss', random_state=42)

    grid_search = GridSearchCV(xgb, param_grid, cv=5, scoring='f1', n_jobs=-1)
    grid_search.fit(X_train_balanced, y_train_balanced)

    print("Best parameters:", grid_search.best_params_)

    best_model = grid_search.best_estimator_
    y_pred = best_model.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    print("\nOverall Accuracy: {:.4f}".format(accuracy))

    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['Negative (0)', 'Positive (1)']))

    y_pred_proba = best_model.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, y_pred_proba)
    print("AUC Score: {:.4f}".format(auc))

    fpr, tpr, _ = roc_curve(y_test, y_pred_proba)

    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, color='blue', label=f'ROC Curve (AUC = {auc:.4f})')
    plt.plot([0, 1], [0, 1], color='red', linestyle='--')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curve')
    plt.legend()
    plt.grid(True)
    plt.savefig('roc_curve.png')
    plt.close()

    print("\nTest Set Distribution:")
    print("Negative (0) Samples:", sum(y_test == 0))
    print("Positive (1) Samples:", sum(y_test == 1))

except Exception as e:
    print("An error occurred:", str(e))