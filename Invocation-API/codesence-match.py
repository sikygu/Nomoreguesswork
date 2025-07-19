import pandas as pd
import os


def match_and_filter_excel(symprompt_file, codersence_file, output_file=None):
    try:

        df_symprompt = pd.read_excel(symprompt_file)
        df_codersence = pd.read_excel(codersence_file)

        if 'symprompt' not in df_symprompt.columns:
            raise ValueError(f"文件 {symprompt_file} 中未找到 'symprompt' 列")

        if 'class_name' not in df_codersence.columns:
            raise ValueError(f"文件 {codersence_file} 中未找到 'class_name' 列")

        symprompt_list = df_symprompt['symprompt'].dropna().tolist()
        symprompt_set = set(symprompt_list)

        position_map = {value: index for index, value in enumerate(symprompt_list)}

        filtered_df = df_codersence[df_codersence['class_name'].isin(symprompt_set)].copy()

        if filtered_df.empty:
            print("警告: 未找到匹配的class_name值")
            return None

        filtered_df['sort_key'] = filtered_df['class_name'].map(position_map)
        filtered_df.sort_values('sort_key', inplace=True)
        filtered_df.drop('sort_key', axis=1, inplace=True)

        if not output_file:
            base_dir, filename = os.path.split(codersence_file)
            base_name, ext = os.path.splitext(filename)
            output_file = os.path.join(base_dir, f"{base_name}_filtered{ext}")

        filtered_df.to_excel(output_file, index=False)
        print(f"已成功筛选并保存结果到 {output_file}")
        print(f"共筛选出 {len(filtered_df)} 行数据")

        return output_file

    except Exception as e:
        print(f"处理过程中发生错误: {e}")
        return None


if __name__ == "__main__":

    symprompt_file = r"C:\Users\17958\Desktop\匹配.xlsx"
    codersence_file = r"D:\project_py\file-work\api\codersence-all.xlsx"

    output_file = match_and_filter_excel(symprompt_file, codersence_file)