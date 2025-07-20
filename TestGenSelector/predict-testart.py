import pandas as pd
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_curve,
    auc,
    classification_report
)
import matplotlib.pyplot as plt
import joblib
import os

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

MODEL_DIR = 'TestGenSelector-model'
PREDICTION_DIR = 'predictions-testart'

FEATURES = ["COM_RAT", "Cyclic", "Dcy*", "DPT*", "LCOM", "Level", "INNER", "jf",
            "Level*", "String processing", "PDpt", "CLOC", "JLOC", "Jm", "Business Logic"]


def clean_data(df, features):
    df_clean = df.copy()
    df_clean = df_clean[df_clean["1-suit-LLM"].isin([0, 1])]
    for col in features:
        df_clean.loc[:, col] = pd.to_numeric(df_clean[col], errors='coerce')
    df_clean = df_clean.dropna(
        subset=features,
        thresh=len(features) - 2
    )
    return df_clean


def load_model(model_path):
    if os.path.exists(model_path):
        model = joblib.load(model_path)
        print(f"Model loaded from {model_path}")
        return model
    else:
        raise FileNotFoundError(f"Model file {model_path} does not exist")


def save_predictions(df_original, y_true, y_pred, model_name, dataset_type, prediction_dir=PREDICTION_DIR):
    os.makedirs(prediction_dir, exist_ok=True)
    result_df = pd.DataFrame({
        'True Label': y_true,
        'Predicted Label': y_pred
    })
    result_with_original = pd.concat([df_original.reset_index(drop=True), result_df], axis=1)
    file_path = os.path.join(prediction_dir, f'{model_name}_{dataset_type}_predictions.csv')
    result_with_original.to_csv(file_path, index=False, encoding='utf-8-sig')
    print(f"Predictions saved to {file_path}")
    return file_path


def main():
    try:
        model_types = ["Random Forest", "XGBoost"]
        dataset_types = ["sym", "testart"]
        models = {}

        for model_type in model_types:
            for dataset_type in dataset_types:
                model_name = f"{model_type}_{dataset_type}"
                model_path = os.path.join(MODEL_DIR, f'{model_type}-{dataset_type}.pkl')
                models[model_name] = load_model(model_path)

        test_data_path = r"C:\Users\17958\Desktop\testart-test01.xlsx"
        df_test = pd.read_excel(test_data_path)

        original_test_size = len(df_test)
        df_test_clean = clean_data(df_test, FEATURES)

        print(f"Test data cleaned. Original size: {original_test_size}, Processed size: {len(df_test_clean)}")
        print("Test data target distribution:\n", df_test_clean["1-suit-LLM"].value_counts())

        X_test = df_test_clean[FEATURES].values
        y_test = df_test_clean["1-suit-LLM"].astype(int)

        results = []

        for model_name, model in models.items():
            try:
                model_type, dataset_type = model_name.split('_')
                y_pred = model.predict(X_test)
                y_proba = model.predict_proba(X_test)[:, 1]

                save_predictions(df_test_clean, y_test, y_pred, model_type, dataset_type)

                precision = precision_score(y_test, y_pred)
                recall = recall_score(y_test, y_pred)
                f1 = f1_score(y_test, y_pred)

                fpr, tpr, _ = roc_curve(y_test, y_proba)
                roc_auc = auc(fpr, tpr)

                results.append({
                    "Model": model_name,
                    "Accuracy": accuracy_score(y_test, y_pred),
                    "Precision": precision,
                    "Recall": recall,
                    "F1": f1,
                    "AUC": roc_auc,
                    "fpr": fpr,
                    "tpr": tpr,
                    "Report": classification_report(y_test, y_pred)
                })

                print(f"\n=== Evaluation Results for {model_name} ===")
                print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
                print(f"Precision: {precision:.4f} | Recall: {recall:.4f} | F1-Score: {f1:.4f}")
                print(f"AUC: {roc_auc:.4f}")
                print("Classification Report:")
                print(classification_report(y_test, y_pred))

            except Exception as e:
                print(f"Error evaluating {model_name}: {str(e)}")

        if results:
            plt.figure(figsize=(12, 6))

            plt.subplot(1, 2, 1)
            for res in results:
                plt.plot(res['fpr'], res['tpr'],
                         label=f"{res['Model']} (AUC = {res['AUC']:.2f})")

            plt.plot([0, 1], [0, 1], 'k--')
            plt.xlim([0.0, 1.0])
            plt.ylim([0.0, 1.05])
            plt.xlabel('False Positive Rate')
            plt.ylabel('True Positive Rate')
            plt.title('ROC Curve Comparison')
            plt.legend(loc="lower right")
            plt.grid(alpha=0.3)

            plt.subplot(1, 2, 2)
            metrics = ['Accuracy', 'Precision', 'Recall', 'F1', 'AUC']
            x = np.arange(len(results))
            width = 0.15

            for i, metric in enumerate(metrics):
                plt.bar(x + i * width, [res[metric] for res in results], width, label=metric)

            plt.xlabel('Models')
            plt.ylabel('Score')
            plt.title('Model Performance Comparison')
            plt.xticks(x + width * (len(metrics) - 1) / 2, [res['Model'] for res in results], rotation=45)
            plt.ylim(0, 1.05)
            plt.legend(bbox_to_anchor=(1.05, 1))
            plt.grid(axis='y', alpha=0.3)

            plt.tight_layout()
            plt.savefig('model_evaluation.png', dpi=300)
            plt.close()

            print("\nModel evaluation visualization saved as 'model_evaluation.png'")

    except Exception as e:
        print(f"Program error: {str(e)}")
        if 'df_test_clean' in locals():
            print("Cleaned analysis data sample:\n", df_test_clean[FEATURES].head())


if __name__ == "__main__":
    main()