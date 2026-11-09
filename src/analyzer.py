
from pathlib import Path

from src.preprocessing import preprocess_image
from src.color.colorhistogram import compare_with_dataset
from src.clip import analyze_clip_image
from src.lbp import (
    extract_lbp_histogram,
    calculate_lbp_similarity
)

import cv2


# 프로젝트 루트
BASE_DIR = Path(__file__).resolve().parent.parent

# 데이터셋 폴더
DATASET_DIR = BASE_DIR / "dataset"


# 분석할 화풍과 데이터셋 폴더
STYLE_DATASETS = {
    "Ghibli": DATASET_DIR / "ghibli",
    "Disney": DATASET_DIR / "disney",
    "Simpsons": DATASET_DIR / "simpsons",
}


# 최종 가중치
COLOR_WEIGHT = 0.6
CLIP_WEIGHT = 0.3
LBP_WEIGHT = 0.1


def analyze_image(image_path):

    # -------------------------
    # 1. Color Histogram
    # -------------------------

    query_image = preprocess_image(image_path)

    color_scores = {}

    for style, dataset_path in STYLE_DATASETS.items():

        if not dataset_path.exists():
            raise FileNotFoundError(
                f"데이터셋 폴더를 찾을 수 없습니다: {dataset_path}"
            )

        score = compare_with_dataset(
            query_image,
            str(dataset_path)
        )

        color_scores[style] = score


    # -------------------------
    # 2. CLIP
    # -------------------------

    clip_scores = analyze_clip_image(image_path)


    # -------------------------
    # 3. LBP
    # -------------------------

    query_lbp_image = cv2.imread(str(image_path))

    if query_lbp_image is None:
        raise ValueError("입력 이미지를 불러올 수 없습니다.")

    query_lbp_image = cv2.resize(
    query_lbp_image,
    (128, 128)
    )

    query_lbp = extract_lbp_histogram(query_lbp_image)

    lbp_scores = {}

    for style, dataset_path in STYLE_DATASETS.items():

        similarities = []

        for image_file in dataset_path.iterdir():

            if image_file.suffix.lower() not in [
                ".jpg", ".jpeg", ".png", ".bmp"
            ]:
                continue

            dataset_image = cv2.imread(str(image_file))

            if dataset_image is None:
                continue

            dataset_image = cv2.resize(
                dataset_image,
                (128, 128)
            )

            dataset_lbp = extract_lbp_histogram(dataset_image)
            similarity = calculate_lbp_similarity(
                query_lbp,
                dataset_lbp
            )

            similarities.append(similarity)

        lbp_scores[style] = (
            sum(similarities) / len(similarities)
            if similarities else 0
        )


    # -------------------------
    # 4. 최종 점수 계산
    # -------------------------

    final_scores = {}

    for style in STYLE_DATASETS:

        color_score = color_scores[style]

        clip_score = clip_scores[style] * 100

        lbp_score = lbp_scores[style]

        final_score = (
            color_score * COLOR_WEIGHT
            + clip_score * CLIP_WEIGHT
            + lbp_score * LBP_WEIGHT
        )

        final_scores[style] = round(final_score, 2)


    # -------------------------
    # 5. 가장 유사한 화풍
    # -------------------------

    best_style = max(
        final_scores,
        key=final_scores.get
    )

    return {
        "color_scores": color_scores,
        "clip_scores": clip_scores,
        "lbp_scores": lbp_scores,
        "final_scores": final_scores,
        "best_style": best_style
    }
