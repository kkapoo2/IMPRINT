
from pathlib import Path
import csv
import cv2

from src.lbp import (
    extract_lbp_histogram as extract_original,
    calculate_lbp_similarity as compare_original,
)
from src.lbp_uniform import (
    extract_lbp_histogram as extract_uniform,
    calculate_lbp_similarity as compare_uniform,
)

BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_DIR = BASE_DIR / "dataset"
TEST_DIR = BASE_DIR / "test_dataset"
RESULT_DIR = BASE_DIR / "results"

STYLES = ["Ghibli", "Disney", "Simpsons"]
EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp"}


def load_image(path):
    image = cv2.imread(str(path))

    if image is None:
        raise ValueError(f"이미지를 읽을 수 없습니다: {path}")

    return cv2.resize(image, (128, 128))


def build_reference_histograms(extract_function):
    reference = {}

    for style in STYLES:
        folder = DATASET_DIR / style.lower()
        histograms = []

        for path in sorted(folder.iterdir()):
            if path.suffix.lower() not in EXTENSIONS:
                continue

            image = load_image(path)
            histograms.append(extract_function(image))

        if not histograms:
            raise ValueError(f"참조 이미지가 없습니다: {folder}")

        reference[style] = histograms

    return reference


def predict(image, reference, extract_function, compare_function):
    query_hist = extract_function(image)
    scores = {}

    for style in STYLES:
        similarities = [
            compare_function(query_hist, ref_hist)
            for ref_hist in reference[style]
        ]

        scores[style] = sum(similarities) / len(similarities)

    prediction = max(scores, key=scores.get)

    return prediction, scores


def main():
    RESULT_DIR.mkdir(exist_ok=True)

    print("참조 이미지 LBP 히스토그램 생성 중...")

    original_reference = build_reference_histograms(extract_original)
    uniform_reference = build_reference_histograms(extract_uniform)

    rows = []
    original_correct = 0
    uniform_correct = 0

    for actual in STYLES:
        folder = TEST_DIR / actual.lower()

        for path in sorted(folder.iterdir()):
            if path.suffix.lower() not in EXTENSIONS:
                continue

            image = load_image(path)

            original_pred, original_scores = predict(
                image,
                original_reference,
                extract_original,
                compare_original,
            )

            uniform_pred, uniform_scores = predict(
                image,
                uniform_reference,
                extract_uniform,
                compare_uniform,
            )

            original_correct += (original_pred == actual)
            uniform_correct += (uniform_pred == actual)

            rows.append({
                "filename": path.name,
                "actual": actual,
                "Original": original_pred,
                "Uniform": uniform_pred,
                "Original_Ghibli": round(original_scores["Ghibli"], 2),
                "Original_Disney": round(original_scores["Disney"], 2),
                "Original_Simpsons": round(original_scores["Simpsons"], 2),
                "Uniform_Ghibli": round(uniform_scores["Ghibli"], 2),
                "Uniform_Disney": round(uniform_scores["Disney"], 2),
                "Uniform_Simpsons": round(uniform_scores["Simpsons"], 2),
            })

            print(
                f"{path.name} | 실제: {actual} | "
                f"기존: {original_pred} | Uniform: {uniform_pred}"
            )

    if not rows:
        print("테스트 이미지가 없습니다.")
        return

    output_path = RESULT_DIR / "lbp_comparison.csv"

    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    total = len(rows)

    print("\n===== LBP 비교 결과 =====")
    print(f"기존 LBP: {original_correct / total * 100:.2f}% ({original_correct}/{total})")
    print(f"Uniform LBP: {uniform_correct / total * 100:.2f}% ({uniform_correct}/{total})")
    print(f"\n상세 결과 저장: {output_path}")


if __name__ == "__main__":
    main()
