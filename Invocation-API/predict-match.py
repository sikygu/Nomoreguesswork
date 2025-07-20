import pandas as pd

def match_and_filter_excel(file_a_path, file_b_path, output_path):
    try:
        df_a = pd.read_excel(file_a_path)
        df_b = pd.read_excel(file_b_path)

        required_columns_a = ['class', 'project', 'yes']
        required_columns_b = ['Class Name', 'project']

        for col in required_columns_a:
            if col not in df_a.columns:
                raise ValueError(f"Column {col} not found in File A")

        for col in required_columns_b:
            if col not in df_b.columns:
                raise ValueError(f"Column {col} not found in File B")

        a_key_to_yes = {(row['class'], row['project']): row['yes']
                        for _, row in df_a.iterrows()}

        filtered_rows = []
        for _, row in df_b.iterrows():
            key = (row['Class Name'], row['project'])
            if key in a_key_to_yes:
                new_row = row.copy()
                new_row['yes'] = a_key_to_yes[key]
                filtered_rows.append(new_row)

        df_b_filtered = pd.DataFrame(filtered_rows)

        if not df_b_filtered.empty:
            cols = df_b_filtered.columns.tolist()
            project_idx = cols.index('project')
            cols.insert(project_idx + 1, 'yes')
            df_b_filtered = df_b_filtered[cols]

        df_b_filtered.to_excel(output_path, index=False)
        print(f"Filtering completed. Results saved to: {output_path}")

        return df_b_filtered

    except Exception as e:
        print(f"An error occurred during processing: {e}")
        return None

if __name__ == "__main__":
    file_a_path = r"C:\Users\17958\Desktop\sym-pre.xlsx"
    file_b_path = r"C:\Users\17958\Desktop\gemini-14-classification_results_all.xlsx"
    output_path = r"C:\Users\17958\Desktop\all-res.xlsx"

    match_and_filter_excel(file_a_path, file_b_path, output_path)