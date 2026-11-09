from pathlib import Path
import csv

from src.analyzer import analyze_image

BASE_DIR = Path(__file__).resolve().parent.parent
TEST_DIR = BASE_DIR / "test_dataset"
RESULT_DIR = BASE_DIR / "results"

STYLES = ["Ghibli", "Disney", "Simpsons"]
EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp"}


def predict(scores):
    return max(STYLES, key=lambda style: scores[style])


def main():
    RESULT_DIR.mkdir(exist_ok=True)

    rows = []
    correct = {
        "Color": 0,
        "CLIP": 0,
        "LBP": 0,
        "Final": 0
    }

    for style in STYLES:
        folder = TEST_DIR / style.lower()

        for image_path in sorted(folder.iterdir()):
            if image_path.suffix.lower() not in EXTENSIONS:
                continue

            print(f"분석 중: {image_path.name}")

            result = analyze_image(str(image_path))

            predictions = {
                "Color": predict(result["color_scores"]),
                "CLIP": predict(result["clip_scores"]),
                "LBP": predict(result["lbp_scores"]),
                "Final": result["best_style"]
            }

            row = {
                "filename": image_path.name,
                "actual": style,
                **predictions
            }
            rows.append(row)

            for model, predicted in predictions.items():
                if predicted == style:
                    correct[model] += 1

    if not rows:
        print("테스트 이미지가 없습니다.")
        return

    with open(
        RESULT_DIR / "evaluation_results.csv",
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "filename", "actual",
                "Color", "CLIP", "LBP", "Final"
            ]
        )
        writer.writeheader()
        writer.writerows(rows)

    print("\n===== 정확도 결과 =====")

    for model, count in correct.items():
        accuracy = count / len(rows) * 100
        print(f"{model}: {accuracy:.2f}% ({count}/{len(rows)})")


if __name__ == "__main__":
    main()
