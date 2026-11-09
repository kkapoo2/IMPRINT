
from pathlib import Path
import csv

from src.analyzer import analyze_image

BASE_DIR = Path(__file__).resolve().parent.parent
TEST_DIR = BASE_DIR / "test_dataset"
RESULT_DIR = BASE_DIR / "results"

STYLES = ["Ghibli", "Disney", "Simpsons"]
EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp"}

# Color, CLIP, LBP 순서
WEIGHTS = {
    "Original": (0.2, 0.6, 0.2),
    "A": (0.4, 0.6, 0.0),
    "B": (0.5, 0.5, 0.0),
    "C": (0.6, 0.4, 0.0),
    "D": (0.3, 0.7, 0.0),
    "E": (0.5, 0.4, 0.1),

    # LBP를 포함한 추가 실험
    "F": (0.55, 0.40, 0.05),
    "G": (0.55, 0.35, 0.10),
    "H": (0.50, 0.45, 0.05),
    "I": (0.60, 0.35, 0.05),
    "J": (0.60, 0.30, 0.10),
    "K": (0.65, 0.30, 0.05),
}


def calculate_scores(result, weights):
    color_weight, clip_weight, lbp_weight = weights

    scores = {}

    for style in STYLES:
        color = result["color_scores"][style]
        clip = result["clip_scores"][style] * 100
        lbp = result["lbp_scores"][style]

        scores[style] = (
            color * color_weight
            + clip * clip_weight
            + lbp * lbp_weight
        )

    return scores


def main():
    RESULT_DIR.mkdir(exist_ok=True)

    correct = {name: 0 for name in WEIGHTS}
    rows = []

    for actual in STYLES:
        folder = TEST_DIR / actual.lower()

        for image_path in sorted(folder.iterdir()):
            if image_path.suffix.lower() not in EXTENSIONS:
                continue

            print(f"분석 중: {image_path.name}")

            result = analyze_image(str(image_path))

            row = {
                "filename": image_path.name,
                "actual": actual,
            }

            # 각 알고리즘의 화풍별 원시 점수 저장
            for style in STYLES:
                row[f"Color_{style}"] = round(
                    result["color_scores"][style], 4
                )
                row[f"CLIP_{style}"] = round(
                    result["clip_scores"][style] * 100, 4
                )
                row[f"LBP_{style}"] = round(
                    result["lbp_scores"][style], 4
                )

            # 가중치 조합별 예측
            for name, weights in WEIGHTS.items():
                scores = calculate_scores(result, weights)
                prediction = max(scores, key=scores.get)

                row[name] = prediction

                if prediction == actual:
                    correct[name] += 1

            rows.append(row)

    if not rows:
        print("테스트 이미지가 없습니다.")
        return

    output_path = RESULT_DIR / "weight_comparison.csv"

    fieldnames = [
        "filename",
        "actual",
    ]

    for style in STYLES:
        fieldnames.extend([
            f"Color_{style}",
            f"CLIP_{style}",
            f"LBP_{style}",
        ])

    fieldnames.extend(WEIGHTS.keys())

    with open(
        output_path,
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    total = len(rows)

    print("\n===== 가중치 비교 결과 =====")

    for name, weights in WEIGHTS.items():
        count = correct[name]
        accuracy = count / total * 100

        print(
            f"{name} {weights}: "
            f"{accuracy:.2f}% ({count}/{total})"
        )

    print(f"\n상세 결과 저장: {output_path}")


if __name__ == "__main__":
    main()
