import pandas as pd

def convert_to_float(value):
    if pd.isna(value):
        return None
    if isinstance(value, str):
        value_part = value.split('(')[0].strip()
        if '%' in value_part:
            return float(value_part.rstrip('%')) / 100
        else:
            return float(value_part)
    else:
        return float(value)

def get_llm_value(row):
    BC = row['BC']
    BC1 = row['BC-1']
    LC = row['LC']
    LC1 = row['LC-1']

    if pd.isna(BC) or pd.isna(BC1) or pd.isna(LC) or pd.isna(LC1):
        print(f"Warning: NaN found in row {row.name}: BC={BC}, BC-1={BC1}, LC={LC}, LC-1={LC1}")
        return 1  # 默认值

    if BC > BC1 and LC < LC1:
        return 2
    elif BC < BC1 and LC > LC1:
        return 2
    elif BC >= BC1 and LC >= LC1:
        return 1
    elif (BC == BC1 and LC < LC1) or (BC < BC1 and LC <= LC1):
        return 0
    else:
        return 3


file_path = r"C:\Users\17958\Desktop\coverage.xlsx"
df = pd.read_excel(file_path, sheet_name='sym', engine='openpyxl')

columns_to_convert = ['LC', 'BC', 'LC-1', 'BC-1']
for col in columns_to_convert:
    df[col] = df[col].apply(convert_to_float)


df['BC-1'] = df['BC-1'].fillna(1)


df['1-suite-LLM'] = df.apply(get_llm_value, axis=1)


df['1-suite-LLM'] = df['1-suite-LLM'].astype(int)


output_file_path = r"C:\Users\17958\Desktop\symlabel.xlsx"
df.to_excel(output_file_path, index=False)

print("Ready:", output_file_path)