import os
import requests
import json
import pandas as pd
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

API_KEY = "xxx"
API_URL = "https://cn2us02.opapi.win/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
}


@dataclass
class ModelConfig:
    """Model configuration class"""
    name: str
    provider: str
    max_tokens: int = 2048
    temperature: float = 0.7
    supports_json_mode: bool = False


# Supported model configurations
SUPPORTED_MODELS = {
    # OpenAI
    "gpt-3.5-turbo": ModelConfig("gpt-3.5-turbo", "openai", 2048, 0.7, True),
    "gpt-4o-mini-2024-07-18": ModelConfig("gpt-4o-mini-2024-07-18", "openai", 12288, 0.5, True),

    # Google Gemini
    "gemini-2.5-flash-lite-preview-06-17": ModelConfig("gemini-2.5-flash-lite-preview-06-17", "google", 12288, 0.5, False),
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


# Extract class name from file path
def get_class_name(file_path):
    return os.path.splitext(os.path.basename(file_path))[0]


# Read file content
def read_file_content(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


# Read prompt template from local file
def read_prompt_template() -> str:
    try:
        with open("prompt.txt", "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        print("Error: prompt.txt file not found in the current directory")
        exit(1)
    except Exception as e:
        print(f"Error reading prompt.txt: {e}")
        exit(1)


# Construct prompt using template
def construct_prompt(class_name: str, class_code: str) -> str:
    template = read_prompt_template()
    return template.format(class_name=class_name, class_code=class_code)


def construct_api_params(prompt: str, model_name: str) -> Dict[str, Any]:
    if model_name not in SUPPORTED_MODELS:
        raise ValueError(f"Model not supported: {model_name}")

    config = SUPPORTED_MODELS[model_name]

    # Base parameters
    params = {
        "model": config.name,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": config.max_tokens,
        "temperature": config.temperature,
        "stream": False
    }

    # Add response format if model supports JSON mode
    if config.supports_json_mode:
        params["response_format"] = {"type": "json_object"}

    return params


def parse_response(response_json: Dict[str, Any], model_name: str) -> Optional[Dict[str, Any]]:
    try:
        config = SUPPORTED_MODELS[model_name]

        # Get response content based on provider
        if config.provider in ["openai", "qwen"]:
            content = response_json["choices"][0]["message"]["content"]
        elif config.provider == "anthropic":
            content = response_json["content"][0]["text"] if "content" in response_json else \
            response_json["choices"][0]["message"]["content"]
        elif config.provider == "google":
            content = response_json["candidates"][0]["content"]["parts"][0]["text"] if "candidates" in response_json else \
            response_json["choices"][0]["message"]["content"]
        else:
            content = response_json["choices"][0]["message"]["content"]

        # Parse JSON content
        if content.strip().startswith("{"):
            return json.loads(content)
        else:
            import re
            json_match = re.search(r'\{.*?\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                print(f"Response content cannot be parsed as JSON: {content}")
                return None

    except Exception as e:
        print(f"Error parsing response: {e}")
        return None


def call_api(prompt: str, model: str = "gpt-3.5-turbo", max_retries: int = 4) -> Optional[Dict[str, Any]]:
    """Call API with multiple model support"""
    if model not in SUPPORTED_MODELS:
        print(f"Error: Model '{model}' is not supported")
        print_available_models()
        return None

    for attempt in range(max_retries):
        try:
            params = construct_api_params(prompt, model)
            print(f"[DEBUG] Sending request to {model} (attempt {attempt + 1}/{max_retries})...")

            response = requests.post(
                API_URL,
                headers=HEADERS,
                json=params,
                timeout=30
            )
            response.raise_for_status()
            print("[DEBUG] Request successful!")

            res_json = response.json()
            tool_dict = parse_response(res_json, model)

            if tool_dict:
                return tool_dict
            else:
                print(f"Failed to extract valid JSON from response")

        except requests.exceptions.RequestException as e:
            print(f"Network request failed (attempt {attempt + 1}/{max_retries}): {e}")
        except json.JSONDecodeError as e:
            print(f"JSON parsing failed (attempt {attempt + 1}/{max_retries}): {e}")
        except Exception as e:
            print(f"API call failed (attempt {attempt + 1}/{max_retries}): {e}")

        if attempt < max_retries - 1:
            time.sleep(2)

    print(f"All retries exhausted. Skipping this request")
    return None


# Process a single project
def process_project(project_dir: str, model: str = "gpt-3.5-turbo") -> Tuple[List[List[str]], str]:
    java_files = get_java_files(project_dir)
    results = []

    print(f"Found {len(java_files)} Java files in project directory")

    for i, file_path in enumerate(java_files, 1):
        class_name = get_class_name(file_path)
        print(f"Processing file {i}/{len(java_files)}: {class_name}")

        try:
            class_code = read_file_content(file_path)
            prompt = construct_prompt(class_name, class_code)
            response = call_api(prompt, model)

            if response:
                try:
                    results.append([response["class_name"], response["tool"]])
                    print(f"  Successfully parsed {class_name} -> {response['tool']}")
                except KeyError as e:
                    print(f"  Failed to parse {class_name}: Response missing required field: {e}")
                except Exception as e:
                    print(f"  Error parsing {class_name}: {e}")
            else:
                print(f"  Skipping {class_name} due to empty or invalid response")
        except Exception as e:
            print(f"  Error processing file {class_name}: {e}")

    # Return results and project name
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
        print("🧪 Running in test mode...")
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
                # Excel sheet names have a 31-character limit
                sheet_name = project_name[:31]
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                print(f"\n✅ Results for project {project_name} saved to sheet: {sheet_name} in {output_excel}")
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
    # Operation options
    # 1. Test a single model: Set TEST_MODE = True
    # 2. Batch test multiple models: Set RUN_BATCH_TEST = True
    # 3. Normal operation: Set both to False
    TEST_MODE = False
    RUN_BATCH_TEST = False

    if RUN_BATCH_TEST:
        run_model_tests()
    else:
        main(project_dirs, output_excel, model, TEST_MODE)