import os
import requests
import json
import pandas as pd

API_KEY = "xxx"
API_URL = "https://c-z0-api-01.hash070.com/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
}


def get_java_files(project_dir):
    java_files = []
    for root, dirs, files in os.walk(project_dir):
        for file in files:
            if file.endswith(".java"):
                java_files.append(os.path.join(root, file))
    return java_files


def get_class_name(file_path):
    return os.path.splitext(os.path.basename(file_path))[0]


def read_file_content(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def read_prompt_template():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(current_dir, "prompt.txt")

    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Prompt file not found. Please create prompt.txt in current directory: {prompt_path}")
    except Exception as e:
        raise Exception(f"Failed to read prompt file: {str(e)}")


def construct_prompt(class_name, class_code):
    prompt_template = read_prompt_template()
    return prompt_template.format(class_name=class_name, class_code=class_code)


def call_api(prompt, model="gemini-2.5-flash"):
    params = {
        "messages": [{"role": "user", "content": prompt}],
        "model": model,
        "stream": False
    }

    try:
        print("[DEBUG] Sending request...")
        response = requests.post(
            API_URL,
            headers=HEADERS,
            json=params,
            timeout=30
        )
        response.raise_for_status()

        print("[DEBUG] Request successful!")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API call failed: {e}")
        return None


def main(project_dir, output_excel, model="gemini-2.5-flash"):
    java_files = get_java_files(project_dir)

    columns = ["class_name", "String processing", "File operations", "Network communication",
               "Database operations", "Mathematical calculation", "User Interface (UI)",
               "Business Logic", "Data Structures and Algorithms", "Systems and Tools",
               "Concurrency and Multithreading", "Exception handling"]

    results = []

    for file_path in java_files:
        class_name = get_class_name(file_path)
        class_code = read_file_content(file_path)
        prompt = construct_prompt(class_name, class_code)
        response = call_api(prompt, model)

        if response:
            try:
                res_content = response["choices"][0]["message"]["content"]
                res_content = res_content.strip()
                if res_content.startswith('```json') and res_content.endswith('```'):
                    res_content = res_content[8:-3].strip()

                tool_dict = json.loads(res_content)

                result_row = [
                    tool_dict["class_name"],
                    tool_dict["String processing"],
                    tool_dict["File operations"],
                    tool_dict["Network communication"],
                    tool_dict["Database operations"],
                    tool_dict["Mathematical calculation"],
                    tool_dict["User Interface (UI)"],
                    tool_dict["Business Logic"],
                    tool_dict["Data Structures and Algorithms"],
                    tool_dict["Systems and Tools"],
                    tool_dict["Concurrency and Multithreading"],
                    tool_dict["Exception handling"]
                ]
                results.append(result_row)
            except Exception as e:
                print(f"Error parsing response for {class_name}: {e}")
                results.append([class_name] + ["N/A"] * 11)
        else:
            print(f"Failed to get response for {class_name}")
            results.append([class_name] + ["Failed"] * 11)

    if results:
        df = pd.DataFrame(results, columns=columns)
        df.to_excel(output_excel, index=False)
        print(f"Results saved to {output_excel}")
        print("Preview:")
        print(df.head())
    else:
        print("No results to save")


if __name__ == "__main__":
    project_dir = "E:\\unit-generate\\jfreechart154\\src\\main\\java\\org\\jfree"
    output_excel = "codersence.xlsx"
    model = "gemini-2.5-flash"
    main(project_dir, output_excel, model)