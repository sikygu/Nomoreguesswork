import os
import shutil
from pathlib import Path


def main():
    source_dir = r"E:\unit-generate\google-json - evo\src\main\java\com"
    target_dir = os.path.join(os.path.dirname(source_dir), "select")

    os.makedirs(target_dir, exist_ok=True)

    class_names = ['JsonObject', 'JsonPrimitive', 'Primitives', 'PreJava9DateFormatProvider', 'Streams', 'NonNullElementWrapperList', 'NumberTypeAdapter', 'CollectionTypeAdapterFactory', 'Excluder', 'ReflectionHelper', 'TreeTypeAdapter']


    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if file.endswith(".java"):
                class_name = os.path.splitext(file)[0]

                if class_name in class_names:
                    source_file = os.path.join(root, file)

                    relative_path = os.path.relpath(root, source_dir)
                    target_subdir = os.path.join(target_dir, relative_path)

                    os.makedirs(target_subdir, exist_ok=True)

                    target_file = os.path.join(target_subdir, file)
                    shutil.copy2(source_file, target_file)
                    print(f"Copied: {source_file} -> {target_file}")

    print("Filter completed!")


if __name__ == "__main__":
    main()