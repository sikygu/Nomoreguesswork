import pandas as pd

file1_path = r"C:\Users\17958\Desktop\jfreechart-label.xlsx"
file2_path = r"C:\Users\17958\Desktop\jfreechart-metric.xlsx"

df1 = pd.read_excel(file1_path)
df2 = pd.read_excel(file2_path)

df2['class-1_last_part'] = df2['class-1'].str.split('.').str[-1]

target_col = "1适合LLM"
insert_pos = df1.columns.get_loc(target_col) + 1

max_matches = 0
match_records = []

for _, row in df1.iterrows():
    matches = df2[df2['class-1_last_part'] == row['testart']]
    match_records.append(matches.drop(columns='class-1_last_part').to_dict('records'))
    max_matches = max(max_matches, len(matches))

new_columns = []
for i in range(max_matches):
    for col in df2.columns.drop('class-1'):
        new_columns.append(f"Match{i+1}_{col}")

for col in reversed(new_columns):
    df1.insert(insert_pos, col, None)

for idx, matches in enumerate(match_records):
    for match_num, match_data in enumerate(matches, 1):
        for col_name, value in match_data.items():
            df1.at[idx, f"Match{match_num}_{col_name}"] = value

output_path = r"C:\Users\17958\Desktop\results.xlsx"
df1.to_excel(output_path, index=False)

print(f"Processing completed, maximum matches: {max_matches}, generated {len(new_columns)} new columns")