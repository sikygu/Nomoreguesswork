import pandas as pd
import os


def match_and_filter_excel(symprompt_file, codersence_file, output_file=None):
    try:
        df_symprompt = pd.read_excel(symprompt_file)
        df_codersence = pd.read_excel(codersence_file)

        if 'symprompt' not in df_symprompt.columns:
            raise ValueError(f"'symprompt' column not found in {symprompt_file}")

        if 'class_name' not in df_codersence.columns:
            raise ValueError(f"'class_name' column not found in {codersence_file}")

        symprompt_list = df_symprompt['symprompt'].dropna().tolist()
        symprompt_set = set(symprompt_list)

        position_map = {value: index for index, value in enumerate(symprompt_list)}

        filtered_df = df_codersence[df_codersence['class_name'].isin(symprompt_set)].copy()

        if filtered_df.empty:
            print("Warning: No matching class_name values found")
            return None

        filtered_df['sort_key'] = filtered_df['class_name'].map(position_map)
        filtered_df.sort_values('sort_key', inplace=True)
        filtered_df.drop('sort_key', axis=1, inplace=True)

        if not output_file:
            base_dir, filename = os.path.split(codersence_file)
            base_name, ext = os.path.splitext(filename)
            output_file = os.path.join(base_dir, f"{base_name}_filtered{ext}")

        filtered_df.to_excel(output_file, index=False)
        print(f"Successfully filtered and saved results to {output_file}")
        print(f"{len(filtered_df)} rows of data were filtered")

        return output_file

    except Exception as e:
        print(f"An error occurred during processing: {e}")
        return None


if __name__ == "__main__":
    symprompt_file = r"C:\Users\17958\Desktop\match.xlsx"
    codersence_file = r"D:\project_py\file-work\api\codersence-all.xlsx"

    output_file = match_and_filter_excel(symprompt_file, codersence_file)