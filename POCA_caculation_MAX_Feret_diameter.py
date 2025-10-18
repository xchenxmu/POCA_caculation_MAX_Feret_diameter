import os
import glob
import pandas as pd
import numpy as np
from scipy.spatial import ConvexHull

# ======== Set input and output path here =========
input_path = os.path.normpath(r"c:/Users/Administrator/Desktop/Test/1/HeLa ON-3FR3-TSZ-Flag+R1-003_sml_locsObjs.csv")
output_dir = os.path.normpath(r"c:/Users/Administrator/Desktop/Test/2")
# ================================================

def feret_diameter(points):
    if len(points) < 2:
        return 0.0
    if len(points) == 2:
        return np.linalg.norm(points[0] - points[1])
    try:
        hull = ConvexHull(points)
        hull_pts = points[hull.vertices]
    except Exception:
        hull_pts = points
    n = len(hull_pts)
    max_dist = 0.0
    j = 1
    for i in range(n):
        while True:
            d1 = np.linalg.norm(hull_pts[i] - hull_pts[j % n])
            d2 = np.linalg.norm(hull_pts[i] - hull_pts[(j + 1) % n])
            if d2 > d1:
                j += 1
            else:
                break
        max_dist = max(max_dist, np.linalg.norm(hull_pts[i] - hull_pts[j % n]))
    return max_dist

def analyze_file(input_file, output_dir):
    ext = os.path.splitext(input_file)[1].lower()
    if ext == '.csv':
        data = pd.read_csv(input_file)
    elif ext in ['.xls', '.xlsx']:
        data = pd.read_excel(input_file)
    else:
        print(f"Skipped unsupported file: {input_file}")
        return

    if "id object" not in data.columns or "x" not in data.columns or "y" not in data.columns:
        print(f"Missing required columns in file: {input_file}")
        return

    data = data[data["id object"] != 0]
    results = []
    for obj_id, group in data.groupby("id object"):
        points = group[["x", "y"]].values
        fd = feret_diameter(points)
        results.append({
            "id object": obj_id,
            "Feret diameter": fd,
            "n_points": len(points)
        })

    base_name = os.path.splitext(os.path.basename(input_file))[0]
    out_file = os.path.join(output_dir, f"{base_name}_feret.csv")
    pd.DataFrame(results).to_csv(out_file, index=False)
    print(f"Done: {input_file} --> {out_file}")

def main(input_path, output_dir):
    input_path = os.path.normpath(input_path)
    output_dir = os.path.normpath(output_dir)

    if not os.path.exists(input_path):
        print(f"[ERROR] Input path does not exist: {input_path}")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if os.path.isdir(input_path):
        file_types = ('*.csv', '*.xls', '*.xlsx')
        files = []
        for ft in file_types:
            files.extend(glob.glob(os.path.join(input_path, ft)))
        if not files:
            print("No Excel or CSV files found in the input folder.")
        for file in files:
            analyze_file(file, output_dir)
    elif os.path.isfile(input_path):
        analyze_file(input_path, output_dir)
    else:
        print(f"[ERROR] Input path is neither a file nor a directory: {input_path}")

if __name__ == '__main__':
    main(input_path, output_dir)
