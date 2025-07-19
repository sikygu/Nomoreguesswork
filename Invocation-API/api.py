import os
import requests
import json
import pandas as pd
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from typing import List, Tuple

API_KEY = "xxx"
API_URL = "https://cn2us02.opapi.win/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
}


@dataclass
class ModelConfig:
    """模型配置类"""
    name: str
    provider: str
    max_tokens: int = 2048
    temperature: float = 0.7
    supports_json_mode: bool = False


# 支持的模型配置
SUPPORTED_MODELS = {
    # OpenAI
    "gpt-3.5-turbo": ModelConfig("gpt-3.5-turbo", "openai", 2048, 0.7, True),
    "gpt-4o-mini-2024-07-18": ModelConfig("gpt-4o-mini-2024-07-18", "openai", 12288, 0.5, True),

    # Anthropic Claude
    # "claude-3.7-sonnet": ModelConfig("claude-3-5-sonnet-20241022", "anthropic", 4096, 0.7, False),

    # Google Gemini
    "gemini-2.5-flash-lite-preview-06-17": ModelConfig("gemini-2.5-flash-lite-preview-06-17", "google", 12288, 0.5, False),

    # Qwen
    # "qwen-turbo": ModelConfig("qwen-turbo", "qwen", 2048, 0.7, False),
    # "qwen-plus": ModelConfig("qwen-plus", "qwen", 4096, 0.7, False),
    # "qwen-max": ModelConfig("qwen-max", "qwen", 4096, 0.7, False),
    # "qwen2-72b": ModelConfig("qwen2-72b-instruct", "qwen", 4096, 0.7, False),

    # else
}


def get_available_models() -> List[str]:

    return list(SUPPORTED_MODELS.keys())


def print_available_models():

    print("Model List:")
    for provider_group in ["openai", "anthropic", "google", "qwen"]:
        models = [name for name, config in SUPPORTED_MODELS.items() if config.provider == provider_group]
        if models:
            provider_name = {
                "openai": "OpenAI",
                "anthropic": "Anthropic Claude",
                "google": "Google Gemini",
                "qwen": "Qwen"
            }.get(provider_group, provider_group)
            print(f"\n{provider_name}:")
            for model in models:
                print(f"  - {model}")


def get_java_files(project_dir):
    java_files = []
    for root, dirs, files in os.walk(project_dir):
        for file in files:
            if file.endswith(".java"):
                java_files.append(os.path.join(root, file))
    return java_files


# 从文件路径提取类名
def get_class_name(file_path):
    return os.path.splitext(os.path.basename(file_path))[0]


# 读取文件内容
def read_file_content(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


# 构造提示
def construct_prompt(class_name: str, class_code: str) -> str:
    prompt = f"""
Here is a Java class named {class_name}:

{class_code}
You are a senior professor of software engineering. Please classify each class based on your professional knowledge and the following 25 indicators that describe code characteristics. Read the code, combine the characteristics of test case generation by Evo and LLM, calculate the 25 indicators that describe code characteristics to determine whether it is more appropriate to use LLM or Evosuite to generate test cases.

Evosuite is a tool that automatically generates Java-like test cases using evolutionary algorithms, with the goal of achieving high code coverage. LLM can generate test cases based on its understanding of the code and behavior.

The 15 metrics are as follows:

1. **Number of Transitive Dependencies (Dcy*)** : Derived from Dcy, it refers to the number of other classes that a class directly or indirectly depends on, including the number of directly dependent classes and indirectly dependent classes, which can reflect the deep coupling state of the class in the dependency network.
2. **Number of Transitive Dependents (DPT*)** : It is an object-oriented coupling feature, referring to the number of classes that indirectly depend on the current class through the dependency chain. It is obtained by constructing a dependency graph and using a graph traversal algorithm to find all transitive dependencies and then statistically analyzing them.
3. **Cyclic Dependencies ** : It is an object-oriented coupling feature, referring to the number of other classes that a class directly or indirectly depends on, and these dependencies also directly or indirectly depend on that class. It is obtained by constructing a dependency graph, collecting direct dependencies, calculating transitive dependencies, identifying strongly connected components, and then subtracting 1 after statistics, representing the number of other classes involved in circular dependencies.
4. **Level (Level)** : It is an object-oriented theoretical complexity feature that measures the "number of levels" of the classes a class depends on. When it does not depend on other classes, its value is 0; when it does depend, its value is the maximum Level value among the dependent classes plus 1 (excluding classes that are mutually dependent or cyclically dependent).
5. Adjusted Level (Level*) : It is a theoretical complexity feature of object-oriented programming. Based on the "number of layers" of the classes that a class depends on, it considers the number of classes in circular dependencies. When it does not depend on other classes, the value is 0. When there is a dependency, the value is the maximum Level* value in the dependent class (non-circular dependency) plus the number of classes that are interdependent with or form a circular dependency with that class.
6.**Package Dependents (PDpt)** : It is the dependency feature corresponding to PDcy, referring to the number of packages that directly or indirectly depend on the current class. It is obtained by counting the number of packages that directly or indirectly depend on the class.
7.Lack of Cohesion of Methods (LCOM) : It is an object-oriented cohesion feature, referring to the degree of lack of cohesion among the methods of a class. It is obtained by constructing an inter-method relationship graph (where nodes represent methods and edges represent inter-method relationships) and calculating the number of connected components in the graph, and is related to the cohesion and responsibility of the class.
8.**Comment Lines of Code (CLOC)** : It is an extension of the concept of source code lines of code (SLOC) proposed by Lazic. It refers to the total number of lines containing comment content in the code file, calculated by strict syntax parsing, reflecting the physical density of comments in the code and its relationship with the interpretability of the code.
9. **Javadoc Lines of Code (JLOC)** : It is a refined metric of CLOC, specifically counting the number of lines of comments that comply with the Javadoc specification, measuring the density of code comments that follow the conventions of the standard API documentation, and is closely related to the completeness of the API documentation.
10. **Javadoc Field Coverage (JF)** : It is a coverage feature based on JLOC, referring to the percentage of the number of fields with Javadoc comments to the total number of fields in the class, quantifying the documentation level of fields in the class.
11. **Javadoc Method Coverage (JM)** : Derived from JLOC, it refers to the percentage of the number of methods with Javadoc annotations to the total number of methods in the class, and is closely related to the integrity of the method-level documentation.
12. **Comment Ratio (COM_RAT)** : It is a code comment feature, referring to the ratio of the number of comment lines in the code to the total number of code lines (excluding blank lines), reflecting the relative density of comments in the code. It is a classic feature for evaluating code readability.
13.**Number of Implemented Interfaces (INNER)** : Defined considering the need to describe the size of a class from the perspective of interface implementation, it refers to the total number of interfaces implemented by a class, including all different interfaces implemented directly and inherited from the parent class.
14.String Processing** : This scenario involves the creation, manipulation, parsing, formatting or transformation of strings, such as processing text data, generating reports, cleaning input, as well as methods like string splitting, concatenation, and regular expression matching.
15.*Business Logic** : This scenario mainly implements specific business rules or domain logic, which is specific to the application context, such as user permission verification, workflow engine, etc.


Please respond in the following JSON format:

{{"class_name": "{class_name}", "tool": "LLM" 或 "Evosuite"}}
"""
    return prompt


def construct_api_params(prompt: str, model_name: str) -> Dict[str, Any]:

    if model_name not in SUPPORTED_MODELS:
        raise ValueError(f"no model: {model_name}")

    config = SUPPORTED_MODELS[model_name]

    # 基础参数
    params = {
        "model": config.name,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": config.max_tokens,
        "temperature": config.temperature,
        "stream": False
    }

    # 如果模型支持JSON模式，添加响应格式
    if config.supports_json_mode:
        params["response_format"] = {"type": "json_object"}

    return params


def parse_response(response_json: Dict[str, Any], model_name: str) -> Optional[Dict[str, Any]]:

    try:
        config = SUPPORTED_MODELS[model_name]

        # 获取响应内容
        if config.provider in ["openai", "qwen"]:
            content = response_json["choices"][0]["message"]["content"]
        elif config.provider == "anthropic":
            content = response_json["content"][0]["text"] if "content" in response_json else \
            response_json["choices"][0]["message"]["content"]
        elif config.provider == "google":
            content = response_json["candidates"][0]["content"]["parts"][0][
                "text"] if "candidates" in response_json else response_json["choices"][0]["message"]["content"]
        else:

            content = response_json["choices"][0]["message"]["content"]


        if content.strip().startswith("{"):
            return json.loads(content)
        else:
            import re
            json_match = re.search(r'\{.*?\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                print(f"The response content cannot be parsed: {content}")
                return None

    except Exception as e:
        print(f"error: {e}")
        return None


def call_api(prompt: str, model: str = "gpt-3.5-turbo", max_retries: int = 4) -> Optional[Dict[str, Any]]:
    """调用API，支持多种模型"""
    if model not in SUPPORTED_MODELS:
        print(f"error: '{model}'")
        print_available_models()
        return None

    for attempt in range(max_retries):
        try:
            params = construct_api_params(prompt, model)
            print(f"[DEBUG]  {model} request (attempt {attempt + 1}/{max_retries})...")

            response = requests.post(
                API_URL,
                headers=HEADERS,
                json=params,
                timeout=30
            )
            response.raise_for_status()
            print("[DEBUG] OK！")

            res_json = response.json()
            tool_dict = parse_response(res_json, model)

            if tool_dict:
                return tool_dict
            else:
                print(f"Failure")

        except requests.exceptions.RequestException as e:
            print(f"Network request failed ( {attempt + 1}/{max_retries}): {e}")
        except json.JSONDecodeError as e:
            print(f"JSON parsing failed ( {attempt + 1}/{max_retries}): {e}")
        except Exception as e:
            print(f"API failed ( {attempt + 1}/{max_retries}): {e}")

        if attempt < max_retries - 1:
            time.sleep(2)

    print(f"All retries failed. Skip this request")
    return None


# 处理单个项目
def process_project(project_dir: str, model: str = "gpt-3.5-turbo") -> Tuple[List[List[str]], str]:
    java_files = get_java_files(project_dir)
    results = []

    print(f"find {len(java_files)} Java")

    for i, file_path in enumerate(java_files, 1):
        class_name = get_class_name(file_path)
        print(f"process  {i}/{len(java_files)}: {class_name}")

        try:
            class_code = read_file_content(file_path)
            prompt = construct_prompt(class_name, class_code)
            response = call_api(prompt, model)

            if response:
                try:
                    results.append([response["class_name"], response["tool"]])
                    print(f"  parsing✓ {class_name} -> {response['tool']}")
                except KeyError as e:
                    print(f"  ✗ parsing {class_name}  response was missing a field: {e}")
                except Exception as e:
                    print(f"  ✗ parsing {class_name} error: {e}")
            else:
                print(f"  ✗ 跳过 {class_name}，继续处理下一个文件")
        except Exception as e:
            print(f"  ✗ 处理文件 {class_name} 时出错: {e}")

    # 返回结果和项目名
    project_name = os.path.basename(os.path.normpath(project_dir))
    return results, project_name


def test_model_call(model_name: str = "gpt-3.5-turbo") -> bool:
    print(f"\n{'=' * 50}")
    print(f"🧪 Testing model: {model_name}")
    print(f"{'=' * 50}")

    if model_name not in SUPPORTED_MODELS:
        print(f"❌ Error: Unsupported model '{model_name}'")
        print_available_models()
        return False

    test_class_name = "TestClass"
    test_class_code = """
public class TestClass {
    private int value;

    public TestClass(int value) {
        this.value = value;
    }

    public int getValue() {
        return value;
    }

    public void setValue(int value) {
        this.value = value;
    }

    public int add(int num) {
        return value + num;
    }
}
"""

    test_prompt = construct_prompt(test_class_name, test_class_code)

    print(f"📤 Sending test request...")
    print(f"   Model: {model_name}")
    print(f"   Configuration: {SUPPORTED_MODELS[model_name]}")

    try:
        response = call_api(test_prompt, model_name, max_retries=2)

        if response is None:
            print(f"❌ Test failed: API call returned None")
            return False

        if not isinstance(response, dict):
            print(f"❌ Test failed: Response is not a dictionary")
            return False

        if "class_name" not in response:
            print(f"❌ Test failed: Response missing 'class_name' field")
            print(f"   Actual response: {response}")
            return False

        if "tool" not in response:
            print(f"❌ Test failed: Response missing 'tool' field")
            print(f"   Actual response: {response}")
            return False

        if response["class_name"] != test_class_name:
            print(f"⚠️  Warning: class_name mismatch")
            print(f"   Expected: {test_class_name}")
            print(f"   Actual: {response['class_name']}")

        if response["tool"] not in ["LLM", "Evosuite"]:
            print(f"⚠️  Warning: tool value not in expected range")
            print(f"   Expected: 'LLM' or 'Evosuite'")
            print(f"   Actual: {response['tool']}")

        print(f"✅ Test successful!")
        print(f"   📋 Response content:")
        print(f"      Class name: {response['class_name']}")
        print(f"      Recommended tool: {response['tool']}")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def run_model_tests(models_to_test: List[str] = None) -> Dict[str, bool]:
    if models_to_test is None:
        models_to_test = list(SUPPORTED_MODELS.keys())
        print(f"📋 Auto-detected available models:")
        for model in models_to_test:
            print(f"   - {model}")

    print(f"\n🚀 Starting batch model testing...")
    print(f"   Number of models to test: {len(models_to_test)}")

    results = {}
    success_count = 0

    for i, model in enumerate(models_to_test, 1):
        print(f"\n📊 Progress: {i}/{len(models_to_test)}")

        if model not in SUPPORTED_MODELS:
            print(f"⏭️  Skipping unsupported model: {model}")
            results[model] = False
            continue

        try:
            success = test_model_call(model)
            results[model] = success
            if success:
                success_count += 1

            if i < len(models_to_test):
                time.sleep(1)

        except KeyboardInterrupt:
            print(f"\n⏹️  User interrupted testing")
            break
        except Exception as e:
            print(f"❌ Exception occurred while testing model {model}: {e}")
            results[model] = False

    print(f"\n{'=' * 60}")
    print(f"📊 Test Summary")
    print(f"{'=' * 60}")
    print(f"Total tests: {len(results)}")
    print(f"Successful: {success_count}")
    print(f"Failed: {len(results) - success_count}")
    print(f"Success rate: {success_count / len(results) * 100:.1f}%")

    print(f"\n📋 Detailed results:")
    for model, success in results.items():
        status = "✅ Success" if success else "❌ Failed"
        print(f"   {model:<30} {status}")

    return results

def main(project_dirs: List[str], output_excel: str, model: str = "gpt-3.5-turbo", test_mode: bool = False):
    if test_mode:
        print("🧪 Running test mode...")
        success = test_model_call(model)
        if success:
            print(f"\n✅ Model {model} passed the test and is ready for use!")
        else:
            print(f"\n❌ Model {model} failed the test, please check configuration!")
        return

    if model not in SUPPORTED_MODELS:
        print(f"Error: Unsupported model '{model}'")
        print_available_models()
        return

    print(f"🔍 First testing if model {model} is available...")
    if not test_model_call(model):
        print(f"❌ Model test failed, program terminated")
        return

    print(f"\n✅ Model test passed, starting project processing...")
    print(f"Using model: {model}")
    print(f"Output file: {output_excel}")

    with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
        for project_dir in project_dirs:
            print(f"\n{'=' * 60}")
            print(f"Starting project: {project_dir}")
            print(f"{'=' * 60}")

            results, project_name = process_project(project_dir, model)

            if results:
                df = pd.DataFrame(results, columns=["Class Name", "Suitable Tool"])
                df.to_excel(writer, sheet_name=project_name[:31], index=False)
                print(f"\n✅ Results for project {project_name} saved to sheet: {project_name} in {output_excel}")
                print(f"  Processed {len(results)} classes")
            else:
                print(f"\n❌ No results to save for project {project_name}")

if __name__ == "__main__":
    print_available_models()

    project_dirs = [
        "E:\\unit-generate\\commons-csv\\src\\main\\java\\org\\apache\\commons\\csv",
        "E:\\unit-generate\\commons-lang\\src\\main\\java\\org\\apache\\commons\\lang3",
        "E:\\unit-generate\\google-json\\src\\main\\java\\com\\google\\gson",
        "E:\\unit-generate\\commons-cli-evo\\src\\main\\java\\org\\apache\\commons\\cli",
        "E:\\unit-generate\\ruler\\src\\main\\software\\amazon\\event\\ruler",
        "D:\\restful-demo-1\\dat\\src\\main\\java\\net\\datafaker",
        "E:\\unit-generate\\jfreechart154\\src\\main\\java\\org\\jfree"
    ]

    output_excel = "gemini-14-classification_results.xlsx"

    model = "gemini-2.5-flash-lite-preview-06-17"
    # Use Options
    # 1. Test a single model: Set TEST_MODE = True
    # 2. Batch testing multiple models: Set RUN_BATCH_TEST = True
    # 3. Normal operation: Both are set to False
    TEST_MODE = False
    RUN_BATCH_TEST = False

    if RUN_BATCH_TEST:
        run_model_tests()
    else:
        main(project_dirs, output_excel, model, TEST_MODE)