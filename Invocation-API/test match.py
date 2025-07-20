import pandas as pd
from collections import defaultdict
import os


def read_first_file(file_path):
    """Read Excel file and build metrics index mapping"""
    try:
        df = pd.read_excel(file_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {os.path.abspath(file_path)}")

    required_columns = ['class', 'metrics', 'yes']
    if not all(col in df.columns for col in required_columns):
        missing = [col for col in required_columns if col not in df.columns]
        raise ValueError(f"Missing required columns: {missing}")

    metrics_columns = df.columns[3:].tolist()
    metrics_indices = list(range(3, len(df.columns)))  # Actual column indices

    return df, metrics_columns, metrics_indices


def find_unique_combination(matches):
    """Find unique class-metrics combination in matching results"""
    if not matches:
        return None

    counter = defaultdict(int)
    for match in matches:
        key = (match['class'], match['metrics'])
        counter[key] += 1

    # Find the most frequent combination
    max_count = max(counter.values())
    candidates = [k for k, v in counter.items() if v == max_count]

    if max_count == 1 or len(candidates) > 1:
        return None  # No unique combination

    key = candidates[0]
    yes_values = [m['yes'] for m in matches if (m['class'], m['metrics']) == key]
    return {
        'class': key[0],
        'metrics': key[1],
        'yes': yes_values[0] if len(set(yes_values)) == 1 else 'Ambiguous'
    }


def process_second_file(df_train, metrics_indices, test_file):
    """Process test file and output matching results"""
    try:
        df_test = pd.read_csv(test_file)
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {os.path.abspath(test_file)}")

    try:
        test_col_nums = [int(col) for col in df_test.columns]

        if any(num < 1 or num > len(metrics_columns) for num in test_col_nums):
            raise ValueError("Column number out of range of training data metrics")


        test_indices = [3 + (num - 1) for num in test_col_nums]


        if not all(3 <= idx < len(df_train.columns) for idx in test_indices):
            raise ValueError("Invalid column index")

        if len(test_indices) != len(metrics_columns):
            print(f"Warning: Number of metrics in test file ({len(test_indices)}) "
                  f"does not match training data ({len(metrics_columns)})")

    except ValueError as e:
        raise ValueError(f"Error processing test file column names: {str(e)}")

    results = []
    for _, row in df_test.iterrows():
        try:
            query_values = [str(row[idx]) for idx in test_indices]
        except KeyError as e:
            raise ValueError(f"Column index does not exist: {str(e)}")


        matches = []
        for _, train_row in df_train.iterrows():
            match = all(
                str(train_row[idx]) == qv
                for idx, qv in zip(test_indices, query_values)
            )
            if match:
                matches.append({
                    'class': train_row['class'],
                    'metrics': train_row['metrics'],
                    'yes': train_row['yes']
                })

        result = find_unique_combination(matches)
        results.append({
            'input_values': query_values,
            'result': result
        })

    return results


if __name__ == "__main__":

    excel_path = r"C:\Users\17958\Desktop\train_5.0.xlsx"
    csv_path = r"C:\Users\17958\Desktop\test_x.csv"

    try:
        print("Loading training data...")
        df_train, metrics_columns, metrics_indices = read_first_file(excel_path)
        print(f"Training data metric columns: {metrics_columns}")
        print(f"Total number of metric columns: {len(metrics_columns)}")

        print("Processing test data...")
        results = process_second_file(df_train, metrics_indices, csv_path)

        print("\nMatching Results:")
        for idx, res in enumerate(results, 1):
            if res['result']:
                print(f"Row {idx}:")
                print(f"  Class: {res['result']['class']}")
                print(f"  Metrics: {res['result']['metrics']}")
                print(f"  Yes: {res['result']['yes']}")
                print(f"  Input Metrics: {res['input_values']}\n")
            else:
                print(f"Row {idx}: No unique match found → Input Metrics: {res['input_values']}")

    except Exception as e:
        print(f"An error occurred during processing: {str(e)}")