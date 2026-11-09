from pathlib import Path
from src.analyzer import analyze_image

BASE_DIR = Path(__file__).resolve().parent.parent
TEST_DIR = BASE_DIR / "test_dataset"

STYLES = ["ghibli", "disney", "simpsons"]
EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp"}

for style in STYLES:
    folder = TEST_DIR / style

    for image_path in sorted(folder.iterdir()):
        if image_path.suffix.lower() not in EXTENSIONS:
            continue

        result = analyze_image(str(image_path))
        scores = result["lbp_scores"]

        print(f"\n이미지: {image_path.name}")
        print(f"실제 화풍: {style}")
        print(f"Ghibli: {scores['Ghibli']:.2f}")
        print(f"Disney: {scores['Disney']:.2f}")
        print(f"Simpsons: {scores['Simpsons']:.2f}")
        print(f"LBP 예측: {max(scores, key=scores.get)}")
