import pandas as pd
import numpy as np
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_curve,
    auc,
    classification_report,
    roc_auc_score
)
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


FEATURES = ["COM_RAT", "Cyclic", "Dcy*", "DPT"
                                         "8", "LCOM", "Level", "INNER", "jf", "Leve+l", "String processing", "PDpt", "CLOC", "JLOC", "Jm", "Business Logic"]


def clean_data(df):
    df_clean = df.copy()
    df_clean = df_clean[df_clean["1适合LLM"].isin([0, 1])]
    for col in FEATURES:
        df_clean.loc[:, col] = pd.to_numeric(df_clean[col], errors='coerce')
    df_clean = df_clean.dropna(
        subset=FEATURES,
        thresh=len(FEATURES) - 2
    )
    imputer = SimpleImputer(strategy='median')
    df_clean[FEATURES] = imputer.fit_transform(df_clean[FEATURES])
    return df_clean


def save_trained_model(model, model_name, output_dir="trained_models"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    model_path = os.path.join(output_dir, f"{model_name}_smote-15_model.pkl")
    joblib.dump(model, model_path)
    print(f"Model saved to: {model_path}")


def main():
    try:
        df1 = pd.read_excel(r"C:\Users\17958\Desktop\sym-train01.xlsx")
        df2 = pd.read_excel(r"C:\Users\17958\Desktop\sym-test01.xlsx")
        df_clean1 = clean_data(df1)
        df_clean2 = clean_data(df2)

        print("Target column distribution:\n", df_clean1["1适合LLM"].value_counts())

        X_train = df_clean1[FEATURES]
        y_train = df_clean1["1适合LLM"].astype(int)

        X_test = df_clean2[FEATURES]
        y_test = df_clean2["1适合LLM"].astype(int)

        smote = SMOTE(random_state=42)
        X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)

        print(f"Training set sample count after SMOTE: {len(X_train_resampled)}")
        print("Target column distribution after SMOTE:\n", pd.Series(y_train_resampled).value_counts())

        train_resampled = pd.DataFrame(X_train_resampled, columns=FEATURES)
        train_resampled["1适合LLM"] = y_train_resampled
        train_resampled.to_excel("train_resampled.xlsx", index=False)

        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train_resampled)
        X_test_scaled = scaler.transform(X_test)

        save_trained_model(scaler, "standard_scaler")

        models = [
            ("SVM", GridSearchCV(
                SVC(kernel='rbf', probability=True, random_state=42, class_weight='balanced'),
                param_grid={
                    'C': [16, 17, 19, 18, 20, 21, 30, 35, 40],
                    'gamma': [0.45, 0.5, 0.6, 0.7, 0.8, 0.9, 'scale']
                },
                cv=3,
                scoring='f1'
            )),
            ("Decision Tree", GridSearchCV(
                DecisionTreeClassifier(random_state=42, class_weight='balanced'),
                param_grid={
                    'max_depth': [5, 6, 7, 8],
                    'min_samples_split': [6, 7, 8, 9, 10]
                },
                cv=3,
                scoring='f1'
            )),
            ("Random Forest", GridSearchCV(
                RandomForestClassifier(class_weight='balanced', random_state=42),
                param_grid={
                    'n_estimators': [80, 85, 90, 95, 100],
                    'max_depth': [4, 5, 6, 7, 8],
                    'min_samples_split': [3, 4, 5]
                },
                cv=3,
                scoring='f1'
            )),
            ("XGBoost", GridSearchCV(
                XGBClassifier(eval_metric='logloss',
                              scale_pos_weight=np.sum(y_test == 0) / np.sum(y_test == 1),
                              random_state=42),
                param_grid={
                    'learning_rate': [0.22, 0.23, 0.24, 0.25, 0.26],
                    'max_depth': [3, 4, 2],
                    'subsample': [0.8, 0.9, 1.0]
                },
                cv=3,
                scoring='f1'
            ))
        ]

        results = []
        for name, model in models:
            try:
                train_data = X_train_scaled if name == "SVM" else X_train_resampled.values
                test_data = X_test_scaled if name == "SVM" else X_test.values

                model.fit(train_data, y_train_resampled)

                print(f"\n=== {name} Best Parameters ===")
                print(model.best_params_)

                y_pred = model.predict(test_data)
                y_proba = model.predict_proba(test_data)[:, 1]

                precision = precision_score(y_test, y_pred)
                recall = recall_score(y_test, y_pred)
                f1 = f1_score(y_test, y_pred)

                fpr, tpr, _ = roc_curve(y_test, y_proba)
                roc_auc = auc(fpr, tpr)

                if name == "Random Forest":
                    plt.figure(figsize=(10, 6))
                    importances = model.best_estimator_.feature_importances_
                    indices = np.argsort(importances)[::-1]
                    plt.title("Feature Importance - Random Forest")
                    plt.barh(range(len(indices)), importances[indices], align='center')
                    plt.yticks(range(len(indices)), [FEATURES[i] for i in indices])
                    plt.xlabel('Relative Importance')
                    plt.tight_layout()
                    plt.savefig('feature_importance.png', dpi=300)
                    plt.close()

                results.append({
                    "Model": name,
                    "Accuracy": accuracy_score(y_test, y_pred),
                    "Precision": precision,
                    "Recall": recall,
                    "F1": f1,
                    "AUC": roc_auc,
                    "fpr": fpr,
                    "tpr": tpr,
                    "Report": classification_report(y_test, y_pred)
                })

                save_trained_model(model.best_estimator_, name)

            except Exception as e:
                print(f"{name} Training Failed: {str(e)}")

        print("\n" + "=" * 50)
        for res in results:
            print(f"\n=== {res['Model']} ===")
            print(f"Accuracy: {res['Accuracy']:.4f} | Precision: {res['Precision']:.4f}")
            print(f"Recall: {res['Recall']:.4f} | F1: {res['F1']:.4f}")
            print(f"AUC: {res['AUC']:.4f}")
            print("Classification Report:\n", res['Report'])

        if results:
            def plot_detailed_metrics(results):
                plt.figure(figsize=(16, 6))

                plt.subplot(1, 2, 1)
                metrics = ['Accuracy', 'Precision', 'Recall', 'F1', 'AUC']
                colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']

                bar_width = 0.15
                x = np.arange(len(results))

                for i, metric in enumerate(metrics):
                    values = [res[metric] for res in results]
                    plt.bar(x + i * bar_width, values, bar_width,
                            color=colors[i], label=metric)

                plt.title('Model Performance Comparison', fontsize=14)
                plt.xticks(x + bar_width * 2, [res['Model'] for res in results])
                plt.ylabel('Score', fontsize=12)
                plt.ylim(0, 1.05)
                plt.legend(bbox_to_anchor=(1.05, 1))
                plt.grid(axis='y', alpha=0.3)

                plt.subplot(1, 2, 2)
                for res in results:
                    plt.plot(res['fpr'], res['tpr'],
                             label=f"{res['Model']} (AUC={res['AUC']:.2f})")

                plt.plot([0, 1], [0, 1], 'k--')
                plt.xlim([0.0, 1.0])
                plt.ylim([0.0, 1.05])
                plt.xlabel('False Positive Rate', fontsize=12)
                plt.ylabel('True Positive Rate', fontsize=12)
                plt.title('ROC Curve Comparison', fontsize=14)
                plt.legend(loc="lower right")
                plt.grid(alpha=0.3)

                plt.tight_layout()
                plt.savefig('detailed_metrics-SMOTE.png', dpi=300)
                plt.close()

            plot_detailed_metrics(results)

    except Exception as e:
        print(f"Program Exception: {str(e)}")
        if 'df_clean1' in locals():
            print("Cleaned training data sample:\n", df_clean1[FEATURES].head())
        if 'df_clean2' in locals():
            print("Cleaned test data sample:\n", df_clean2[FEATURES].head())


if __name__ == "__main__":
    main()