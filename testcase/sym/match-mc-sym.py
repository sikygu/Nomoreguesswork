import os
import re
import shutil
from pathlib import Path

CONDITIONS ={
    "XYLineAnnotation": (2, 1),
    "WindDataItem": (2, 1),
    "StandardTickUnitSource": (2, 1),
    "WaferMapDataset": (2, 1),
    "NumberAxis": (2, 1),
    "SunJPEGEncoderAdapter": (2, 1),
    "DataPackageResources_ru": (2, 1),
    "PieSectionEntity": (2, 1),
    "ValueTick": (1, 0),
    "Title": (1, 0),
    "DefaultCategoryDataset": (2, 1),
    "CategoryLabelWidthType": (2, 1),
    "CenterTextMode": (1, 0),
    "DefaultPolarPlotEditor": (2, 1),
    "WaterfallBarRenderer": (2, 1),
    "ChartProgressEvent": (2, 1),
    "DefaultLogAxisEditor": (2, 1),
    "DateRange": (2, 1),
    "WaferMapRenderer": (2, 1),
    "StandardCategorySeriesLabelGenerator": (2, 1),
    "JFreeChartEntity": (1, 0),
    "DefaultHeatMapDataset": (2, 1),
    "DefaultFlowDataset": (2, 1),
    "IntervalMarker": (2, 1),
    "RendererUtils": (2, 1),
    "PieDatasetHandler": (2, 1),
    "StrokeSample": (2, 1),
    "AbstractXYAnnotation": (1, 0),
    "PeriodAxis": (2, 1),
    "FlowKey": (2, 1),
    "TextBlockAnchor": (2, 1),
    "AbstractSeriesDataset": (1, 0),
    "Series": (1, 0),
    "YIntervalDataItem": (2, 1),
    "PaintScaleLegend": (2, 1),
    "VectorDataItem": (2, 1),
    "TextLine": (2, 1),
    "GradientBarPainter": (2, 1),
    "XYCoordinateType": (2, 1),
    "ChartEntity": (2, 1),
    "IntervalCategoryToolTipGenerator": (2, 1),
    "BubbleXYItemLabelGenerator": (2, 1),
    "AreaRendererEndType": (2, 1),
    "HistogramDataset": (2, 1),
    "JDBCXYDataset": (2, 1),
    "FlowPlot": (2, 1),
    "XYInversePointerAnnotation": (2, 1),
    "StandardDialScale": (2, 1),
    "HMSNumberFormat": (2, 1),
    "StandardEntityCollection": (2, 1),
    "DefaultTableXYDataset": (2, 1),
    "PaintList": (2, 1),
    "KeyedObject": (2, 1),
    "PieLabelLinkStyle": (2, 1),
    "MeanAndStandardDeviation": (2, 1),
    "CombinedDomainXYPlot": (2, 1),
    "XYSeries": (2, 1),
    "DatasetChangeEvent": (2, 1),
    "AxisCollection": (2, 1),
    "NumberTickUnitSource": (2, 1),
    "CustomXYToolTipGenerator": (2, 1),
    "TickUnit": (1, 0),
    "ComparableObjectSeries": (2, 1),
    "FlowDatasetUtils": (2, 1),
    "LegendItemBlockContainer": (2, 1),
    "KeyedValueComparator": (2, 1),
    "PaintUtils": (2, 1),
    "TimeSeriesTableModel": (2, 1),
    "LineAndShapeRenderer": (2, 1),
    "DatasetGroup": (2, 1),
    "CategoryStepRenderer": (1, 0),
    "StandardXYSeriesLabelGenerator": (2, 1),
    "KeyedValueComparatorType": (2, 1),
    "LogAxis": (2, 1),
    "StrokeMap": (2, 1),
    "SymbolicXYItemLabelGenerator": (2, 1),
    "RendererChangeEvent": (2, 1),
    "SlidingCategoryDataset": (2, 1),
    "ItemLabelPosition": (2, 1),
    "G2TextMeasurer": (2, 1),
    "SimpleHistogramBin": (2, 1),
    "LogTick": (2, 1),
    "AnnotationChangeEvent": (2, 1),
    "ResourceBundleWrapper": (1, 0),
    "TaskSeriesCollection": (2, 1),
    "DefaultXYZDataset": (2, 1),
    "DefaultKeyedValues": (2, 1),
    "TimePeriodAnchor": (2, 1),
    "XYSeriesCollection": (2, 1),
    "StackedXYBarRenderer": (2, 1),
    "CustomCategoryURLGenerator": (2, 1),
    "VectorRenderer": (2, 1),
    "SubCategoryAxis": (2, 1),
    "StandardXYBarPainter": (2, 1),
    "QuarterDateFormat": (2, 1),
    "ItemLabelAnchor": (2, 1),
    "HistogramBin": (2, 1),
    "YIntervalRenderer": (2, 1),
    "ChartFactory": (1, 0),
    "CategoryMarker": (2, 1),
    "LabelBlock": (2, 1),
    "DefaultKeyedValues2DDataset": (1, 0),
    "XYItemRendererState": (2, 1),
    "StandardXYToolTipGenerator": (2, 1),
    "StackedXYAreaRenderer": (1, 0),
    "StandardXYItemRenderer": (2, 1),
    "ExportUtils": (2, 1),
    "DirectionalGradientPaintTransformer": (2, 1),
}


def extract_class_name(filename):
    match = re.match(r'^([A-Z][a-zA-Z0-9]*)(?:_|\.|$)', filename)
    return match.group(1) if match else None


def copy_matching_files(source_dir, target_dir, class_whitelist=None):
    os.makedirs(target_dir, exist_ok=True)
    matched_classes = {}

    print(f"Scanning source directory: {source_dir}")
    for root, dirs, files in os.walk(source_dir):
        print(f"  Checking directory: {root}")
        relative_path = os.path.relpath(root, source_dir)
        target_subdir = os.path.join(target_dir, relative_path)

        os.makedirs(target_subdir, exist_ok=True)

        for file in files:
            if file.endswith('.java'):
                class_name = extract_class_name(file)
                if class_whitelist is None or class_name in class_whitelist:
                    source_file = os.path.join(root, file)
                    target_file = os.path.join(target_subdir, file)
                    shutil.copy2(source_file, target_file)

                    if class_name in matched_classes:
                        matched_classes[class_name] += 1
                    else:
                        matched_classes[class_name] = 1
                    print(f"    Copied: {source_file} -> {target_file}")
                else:
                    print(f"    Skipped: {file} (Class: {class_name} not in whitelist)")
            else:
                print(f"    Skipped non-Java file: {file}")

    return matched_classes


def write_matched_classes(all_matches, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("Matched classes statistics:\n")
        f.write("=" * 30 + "\n")
        for class_name, count in sorted(all_matches.items()):
            f.write(f"{class_name}: {count} files\n")


def main():
    source_dir1 = r"C:\Users\17958\Desktop\TestCases-defect4j\evo\jfree"
    source_dir2 = r"C:\Users\17958\Desktop\TestCases-defect4j\symprompt\jfree"

    target_dir_sym_rf = r"C:\Users\17958\Desktop\jfree\sym-rf"
    output_file = r"C:\Users\17958\Desktop\jfree\sym-rf.txt"

    source1_classes = [cls for cls, (src, cnt) in CONDITIONS.items() if src == 1 and cnt == 0]
    source2_classes = [cls for cls, (src, cnt) in CONDITIONS.items() if src == 2 and cnt == 1]

    print(f"Classes to extract from folder 1: {source1_classes}")
    print(f"Classes to extract from folder 2: {source2_classes}")

    if not os.path.exists(source_dir1):
        print(f"Error: Source directory 1 does not exist - {source_dir1}")
        return

    if not os.path.exists(source_dir2):
        print(f"Error: Source directory 2 does not exist - {source_dir2}")
        return

    print("\nCopying classes with count 0 from folder 1...")
    folder1_matches = copy_matching_files(source_dir1, target_dir_sym_rf, source1_classes)

    print("\nCopying classes with count 1 from folder 2...")
    folder2_matches = copy_matching_files(source_dir2, target_dir_sym_rf, source2_classes)

    all_matches = folder1_matches.copy()
    for cls, cnt in folder2_matches.items():
        if cls in all_matches:
            all_matches[cls] += cnt
        else:
            all_matches[cls] = cnt

    unmatched_classes = [cls for cls in CONDITIONS if cls not in all_matches or all_matches[cls] == 0]

    print("\nMatching statistics:")
    print(f"Matched {len(all_matches)} classes, total {sum(all_matches.values())} files")
    for class_name in CONDITIONS:
        count = all_matches.get(class_name, 0)
        source = CONDITIONS[class_name][0]
        status = "Successfully matched" if count > 0 else "No files matched"
        print(f"  - {class_name}: Copied {count} files from folder {source} ({status})")

    if unmatched_classes:
        print("\nClasses with no matching files:")
        for cls in unmatched_classes:
            print(f"  - {cls}")
    else:
        print("\nAll classes were successfully matched!")

    write_matched_classes(all_matches, output_file)
    print(f"\nMatching results saved to: {output_file}")

    print("\nOperation completed!")


if __name__ == "__main__":
    main()