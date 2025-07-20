import os
import re
import shutil
from pathlib import Path

CONDITIONS = ['XYLineAnnotation', 'WindDataItem', 'StandardTickUnitSource', 'WaferMapDataset', 'NumberAxis', 'SunJPEGEncoderAdapter', 'DataPackageResources_ru', 'PieSectionEntity', 'ValueTick', 'Title', 'DefaultCategoryDataset', 'CategoryLabelWidthType', 'CenterTextMode', 'DefaultPolarPlotEditor', 'WaterfallBarRenderer', 'ChartProgressEvent', 'DefaultLogAxisEditor', 'DateRange', 'WaferMapRenderer', 'StandardCategorySeriesLabelGenerator', 'JFreeChartEntity', 'DefaultHeatMapDataset', 'DefaultFlowDataset', 'IntervalMarker', 'RendererUtils', 'PieDatasetHandler', 'StrokeSample', 'AbstractXYAnnotation', 'PeriodAxis', 'FlowKey', 'TextBlockAnchor', 'AbstractSeriesDataset', 'Series', 'YIntervalDataItem', 'PaintScaleLegend', 'VectorDataItem', 'TextLine', 'GradientBarPainter', 'XYCoordinateType', 'ChartEntity', 'IntervalCategoryToolTipGenerator', 'BubbleXYItemLabelGenerator', 'AreaRendererEndType', 'HistogramDataset', 'JDBCXYDataset', 'FlowPlot', 'XYInversePointerAnnotation', 'StandardDialScale', 'HMSNumberFormat', 'StandardEntityCollection', 'DefaultTableXYDataset', 'PaintList', 'KeyedObject', 'PieLabelLinkStyle', 'MeanAndStandardDeviation', 'CombinedDomainXYPlot', 'XYSeries', 'DatasetChangeEvent', 'AxisCollection', 'NumberTickUnitSource', 'CustomXYToolTipGenerator', 'TickUnit', 'ComparableObjectSeries', 'FlowDatasetUtils', 'LegendItemBlockContainer', 'KeyedValueComparator', 'PaintUtils', 'TimeSeriesTableModel', 'LineAndShapeRenderer', 'DatasetGroup', 'CategoryStepRenderer', 'StandardXYSeriesLabelGenerator', 'KeyedValueComparatorType', 'LogAxis', 'StrokeMap', 'SymbolicXYItemLabelGenerator', 'RendererChangeEvent', 'SlidingCategoryDataset', 'ItemLabelPosition', 'G2TextMeasurer', 'SimpleHistogramBin', 'LogTick', 'AnnotationChangeEvent', 'ResourceBundleWrapper', 'TaskSeriesCollection', 'DefaultXYZDataset', 'DefaultKeyedValues', 'TimePeriodAnchor', 'XYSeriesCollection', 'StackedXYBarRenderer', 'CustomCategoryURLGenerator', 'VectorRenderer', 'SubCategoryAxis', 'StandardXYBarPainter', 'QuarterDateFormat', 'ItemLabelAnchor', 'HistogramBin', 'YIntervalRenderer', 'ChartFactory', 'CategoryMarker', 'LabelBlock', 'DefaultKeyedValues2DDataset', 'XYItemRendererState', 'StandardXYToolTipGenerator', 'StackedXYAreaRenderer', 'StandardXYItemRenderer', 'ExportUtils', 'DirectionalGradientPaintTransformer']

def extract_class_name(filename):
    match = re.match(r'^([A-Z][a-zA-Z0-9]*)(?:_|\.|$)', filename)
    return match.group(1) if match else None

def should_include_file(filename):
    class_name = extract_class_name(filename)
    print(f"Checking file: {filename} -> Extracted class name: {class_name}")
    return class_name in CONDITIONS

def copy_matching_files(source_dir, target_dir, log_file):
    os.makedirs(target_dir, exist_ok=True)
    matched_classes = {}
    unmatched_classes = set(CONDITIONS.copy())

    print(f"Scanning source directory: {source_dir}")
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(f"Source directory: {source_dir}\n")
        f.write("Matching results:\n")

        for root, dirs, files in os.walk(source_dir):
            print(f"  Checking directory: {root}")
            f.write(f"\nChecking directory: {root}\n")
            relative_path = os.path.relpath(root, source_dir)
            target_subdir = os.path.join(target_dir, relative_path)
            os.makedirs(target_subdir, exist_ok=True)

            for file in files:
                if file.endswith('.java'):
                    class_name = extract_class_name(file)
                    if class_name in CONDITIONS:
                        source_file = os.path.join(root, file)
                        target_file = os.path.join(target_subdir, file)
                        shutil.copy2(source_file, target_file)

                        if class_name in matched_classes:
                            matched_classes[class_name] += 1
                        else:
                            matched_classes[class_name] = 1

                        if class_name in unmatched_classes:
                            unmatched_classes.remove(class_name)

                        log_msg = f"    Copied: {source_file} -> {target_file}"
                        print(log_msg)
                        f.write(log_msg + "\n")
                    else:
                        log_msg = f"    Skipped: {file} (Class name: {class_name} does not match conditions)"
                        print(log_msg)
                        f.write(log_msg + "\n")
                else:
                    log_msg = f"    Skipped non-Java file: {file}"
                    print(log_msg)
                    f.write(log_msg + "\n")

        f.write("\nMatching statistics:\n")
        for class_name, count in matched_classes.items():
            f.write(f"  - {class_name}: {count} files\n")

        f.write("\nUnmatched classes:\n")
        if unmatched_classes:
            for class_name in unmatched_classes:
                f.write(f"  - {class_name}\n")
        else:
            f.write("  None\n")

    return matched_classes, unmatched_classes

def main():
    source_dir1 = r"C:\Users\17958\Desktop\TestCases-defect4j\evo\jfree"
    source_dir2 = r"C:\Users\17958\Desktop\TestCases-defect4j\symprompt\jfree"

    target_dir1 = r"C:\Users\17958\Desktop\jfree\evo-sym"
    target_dir2 = r"C:\Users\17958\Desktop\jfree\sym"

    log_file1 = r"C:\Users\17958\Desktop\jfree\evo-sym-matches.txt"
    log_file2 = r"C:\Users\17958\Desktop\jfree\sym-matches.txt"

    if not os.path.exists(source_dir1):
        print(f"Error: Source directory 1 does not exist - {source_dir1}")
        return

    if not os.path.exists(source_dir2):
        print(f"Error: Source directory 2 does not exist - {source_dir2}")
        return

    print("Copying contents from folder 1...")
    folder1_matches, folder1_unmatched = copy_matching_files(source_dir1, target_dir1, log_file1)
    print(f"Folder 1 matched {len(folder1_matches)} classes with a total of {sum(folder1_matches.values())} files")
    for class_name, count in folder1_matches.items():
        print(f"  - {class_name}: {count} files")

    print("\nUnmatched classes in folder 1:")
    if folder1_unmatched:
        for class_name in folder1_unmatched:
            print(f"  - {class_name}")
    else:
        print("  None")

    print("\nCopying contents from folder 2...")
    folder2_matches, folder2_unmatched = copy_matching_files(source_dir2, target_dir2, log_file2)
    print(f"Folder 2 matched {len(folder2_matches)} classes with a total of {sum(folder2_matches.values())} files")
    for class_name, count in folder2_matches.items():
        print(f"  - {class_name}: {count} files")

    print("\nUnmatched classes in folder 2:")
    if folder2_unmatched:
        for class_name in folder2_unmatched:
            print(f"  - {class_name}")
    else:
        print("  None")

    print(f"\nMatching results saved to:\n- {log_file1}\n- {log_file2}")
    print("Operation completed!")

if __name__ == "__main__":
    main()