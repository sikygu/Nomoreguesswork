import pandas as pd
from pathlib import Path

def process_and_save_excel(input_path):
    original_file = Path(input_path)
    df = pd.read_excel(original_file)
    required_cols = ['LC', 'BC', 'LC-1', 'BC-1']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise KeyError(f"Missing required columns: {', '.join(missing_cols)}")
    delete_condition = (
            (df['LC'] == 0) &
            (df['BC'] == 0) &
            (df['LC-1'] == 0) &
            (df['BC-1'] == 0)
    )
    deleted_rows = df[delete_condition].index
    excel_row_numbers = [i + 2 for i in deleted_rows]
    cleaned_df = df[~delete_condition].reset_index(drop=True)
    output_path = original_file.parent / f"{original_file.stem}_processed{original_file.suffix}"
    cleaned_df.to_excel(output_path, index=False)
    return {
        "total_deleted": len(deleted_rows),
        "deleted_rows": excel_row_numbers,
        "original_size": len(df),
        "new_size": len(cleaned_df),
        "output_path": str(output_path)
    }

if __name__ == "__main__":
    file_path = r"C:\Users\17958\Desktop\coverage-metric-train.xlsx"
    try:
        result = process_and_save_excel(file_path)
        print(f"[Processing Report]")
        print(f"Original data rows: {result['original_size']}")
        print(f"Rows deleted: {result['total_deleted']}")
        print(f"Remaining data rows: {result['new_size']}")
        print(f"List of deleted Excel row numbers: {result['deleted_rows']}")
        print(f"New file saved to: {result['output_path']}")
    except Exception as e:
        print(f"[Processing Failed] Error: {str(e)}")
        print("Suggestions: 1) Check if the file path is correct 2) Verify Excel column names match")