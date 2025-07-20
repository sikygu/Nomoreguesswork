import pandas as pd

prefixes = ['cli', 'csv', 'gson', 'lang', 'ruler', 'dat', 'jfreechart']
df = pd.read_excel(r"C:\Users\17958\Desktop\nom-llm.xlsx")

output_path = r"C:\Users\17958\Desktop\aligned_all.xlsx"
with pd.ExcelWriter(output_path) as writer:
    for prefix in prefixes:

        class_col = f"{prefix}class"
        tool_col = f"{prefix}tool"
        class_1_col = f"{prefix}class-1"
        tool_1_col = f"{prefix}tool-1"
        benchmark = df[[class_1_col, tool_1_col]].copy()


        class_tool_mapping = (
            df.dropna(subset=[class_col])
            .set_index(class_col)[tool_col]
            .to_dict()
        )

        merged = pd.merge(
            left=benchmark,
            right=df[[class_col, tool_col]],
            left_on=class_1_col,
            right_on=class_col,
            how='left',
            suffixes=('_benchmark', '_original')
        )

        def align_row(row, class_col=class_col, tool_col=tool_col,
                      class_1_col=class_1_col, mapping=class_tool_mapping,
                      benchmark=benchmark):
            if not pd.isna(row[class_col]):

                if row[class_col] in benchmark[class_1_col].values:
                    row[tool_col] = mapping.get(row[class_col], pd.NA)
                else:
                    row[class_col] = pd.NA
                    row[tool_col] = pd.NA
            return row

        processed = merged.apply(align_row, axis=1)

        final_df = processed[
            processed[class_col].isin(benchmark[class_1_col]) |
            processed[class_col].isna()
            ]

        final_df = final_df[
            [class_col, tool_col, class_1_col, tool_1_col]
        ].reset_index(drop=True)

        final_df.to_excel(
            writer,
            sheet_name=f"{prefix}_aligned",
            index=False
        )

        print(f"{prefix} project processing completed. Results saved to {prefix}_aligned sheet in {output_path}")