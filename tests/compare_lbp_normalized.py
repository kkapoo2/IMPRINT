
from pathlib import Path
import csv
import numpy as np
import cv2

from src.lbp_uniform import (
    extract_lbp_histogram,
    calculate_lbp_similarity,
)

BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_DIR = BASE_DIR / "dataset"
TEST_DIR = BASE_DIR / "test_dataset"
RESULT_DIR = BASE_DIR / "results"

STYLES = ["Ghibli", "Disney", "Simpsons"]
EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp"}


def load_histogram(path):
    image = cv2.imread(str(path))

    if image is None:
        raise ValueError(f"이미지를 읽을 수 없습니다: {path}")

    image = cv2.resize(image, (128, 128))
    return extract_lbp_histogram(image)


def load_reference():
    reference = {}

    for style in STYLES:
        folder = DATASET_DIR / style.lower()

        histograms = []

        for path in sorted(folder.iterdir()):
            if path.suffix.lower() in EXTENSIONS:
                histograms.append(load_histogram(path))

        if not histograms:
            raise ValueError(f"참조 이미지가 없습니다: {folder}")

        reference[style] = np.stack(histograms)

    return reference


def similarity_scores(query_hist, reference):
    scores = {}

    for style in STYLES:
        similarities = [
            calculate_lbp_similarity(query_hist, hist)
            for hist in reference[style]
        ]

        scores[style] = float(np.mean(similarities))

    return scores


def calculate_baselines(reference):
    """
    다른 화풍의 참조 이미지들을 이용해
    각 화풍에 대한 기준 유사도를 계산한다.
    """
    baselines = {}

    for target_style in STYLES:
        other_histograms = []

        for source_style in STYLES:
            if source_style != target_style:
                other_histograms.extend(reference[source_style])

        scores = [
            float(np.mean([
                calculate_lbp_similarity(hist, ref_hist)
                for ref_hist in reference[target_style]
            ]))
            for hist in other_histograms
        ]

        baselines[target_style] = float(np.mean(scores))

    return baselines


def main():
    RESULT_DIR.mkdir(exist_ok=True)

    print("참조 데이터셋 분석 중...")
    reference = load_reference()

    baselines = calculate_baselines(reference)

    print("\n===== 화풍별 기준 유사도 =====")

    for style in STYLES:
        print(f"{style}: {baselines[style]:.2f}")

    rows = []
    original_correct = 0
    normalized_correct = 0

    for actual in STYLES:
        folder = TEST_DIR / actual.lower()

        for path in sorted(folder.iterdir()):
            if path.suffix.lower() not in EXTENSIONS:
                continue

            query_hist = load_histogram(path)

            original_scores = similarity_scores(
                query_hist, reference
            )

            normalized_scores = {
                style: original_scores[style] - baselines[style]
                for style in STYLES
            }

            original_pred = max(
                original_scores, key=original_scores.get
            )

            normalized_pred = max(
                normalized_scores, key=normalized_scores.get
            )

            original_correct += (original_pred == actual)
            normalized_correct += (normalized_pred == actual)

            rows.append({
                "filename": path.name,
                "actual": actual,
                "Original": original_pred,
                "Normalized": normalized_pred,
                "Norm_Ghibli": round(normalized_scores["Ghibli"], 2),
                "Norm_Disney": round(normalized_scores["Disney"], 2),
                "Norm_Simpsons": round(normalized_scores["Simpsons"], 2),
            })

            print(
                f"{path.name} | 실제: {actual} | "
                f"기존: {original_pred} | 보정: {normalized_pred}"
            )

    if not rows:
        print("테스트 이미지가 없습니다.")
        return

    output_path = RESULT_DIR / "lbp_normalized_comparison.csv"

    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    total = len(rows)

    print("\n===== 정규화 비교 결과 =====")
    print(
        f"기존 Uniform LBP: "
        f"{original_correct / total * 100:.2f}% "
        f"({original_correct}/{total})"
    )
    print(
        f"보정 Uniform LBP: "
        f"{normalized_correct / total * 100:.2f}% "
        f"({normalized_correct}/{total})"
    )
    print(f"\n상세 결과 저장: {output_path}")


if __name__ == "__main__":
    main()
