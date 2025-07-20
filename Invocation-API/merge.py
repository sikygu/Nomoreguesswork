import pandas as pd

def merge_excel_sheets(input_file, output_file):
    try:
        xls = pd.ExcelFile(input_file)
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found")
        return
    except Exception as e:
        print(f"Error: Unable to read file '{input_file}': {e}")
        return

    merged_data = pd.DataFrame()
    sheet_names = xls.sheet_names

    for sheet_name in sheet_names:
        try:
            df = xls.parse(sheet_name)
            df['project'] = sheet_name
            merged_data = pd.concat([merged_data, df], ignore_index=True)
        except Exception as e:
            print(f"Warning: Error processing sheet '{sheet_name}': {e}")
            continue

    if merged_data.empty:
        print("Error: No valid data found")
        return

    try:
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            merged_data.to_excel(writer, sheet_name='Merged Data', index=False)
        print(f"Successfully merged data and saved to '{output_file}'")
    except Exception as e:
        print(f"Error: Unable to save file '{output_file}': {e}")

if __name__ == "__main__":
    input_file = r"D:\project_py\file-work\api\gemini-14-classification_results.xlsx"
    output_file = r"D:\project_py\file-work\api\gemini-14-classification_results_all.xlsx"
    merge_excel_sheets(input_file, output_file)