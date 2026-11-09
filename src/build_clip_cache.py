from pathlib import Path

import torch

from src.clip import (
    load_clip_model,
    get_image_embedding,
    ALLOWED_EXTENSIONS,
)


# 프로젝트 최상위 폴더
BASE_DIR = Path(__file__).resolve().parent.parent

# 데이터셋 경로
DATASET_DIR = BASE_DIR / "dataset"

# CLIP embedding 저장 경로
CACHE_DIR = BASE_DIR / "models" / "clip_embeddings"

# 화풍별 데이터셋
STYLE_DATASETS = {
    "ghibli": DATASET_DIR / "ghibli",
    "disney": DATASET_DIR / "disney",
    "simpsons": DATASET_DIR / "simpsons",
}


def build_clip_cache():
    """
    데이터셋 이미지를 CLIP embedding으로 변환하여
    화풍별 .pt 파일로 저장한다.
    """

    # 캐시 폴더 생성
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    # CLIP 모델 불러오기
    model, preprocess = load_clip_model()

    # 화풍별로 처리
    for style, dataset_path in STYLE_DATASETS.items():

        if not dataset_path.is_dir():
            raise FileNotFoundError(
                f"데이터셋 폴더를 찾을 수 없습니다: {dataset_path}"
            )

        embeddings = []
        filenames = []

        # 이미지 파일 목록
        image_files = sorted(
            path for path in dataset_path.iterdir()
            if path.is_file()
            and path.suffix.lower() in ALLOWED_EXTENSIONS
        )

        print(f"\n[{style}] {len(image_files)}장 처리 시작")

        for index, image_path in enumerate(image_files, start=1):

            # 이미지 embedding 생성
            embedding = get_image_embedding(
                str(image_path),
                model,
                preprocess
            )

            embeddings.append(embedding.cpu())
            filenames.append(image_path.name)

            print(
                f"\r[{style}] {index}/{len(image_files)} 완료",
                end="",
                flush=True
            )

        if not embeddings:
            raise ValueError(
                f"분석 가능한 이미지가 없습니다: {dataset_path}"
            )

        # 이미지별 embedding을 하나의 텐서로 합치기
        embedding_tensor = torch.cat(
            embeddings,
            dim=0
        )

        # 저장 파일 경로
        cache_path = CACHE_DIR / f"{style}.pt"

        # embedding 저장
        torch.save(
            {
                "model_name": "ViT-B-32",
                "pretrained": "openai",
                "embeddings": embedding_tensor,
                "filenames": filenames,
            },
            cache_path
        )

        print(f"\n[{style}] 저장 완료: {cache_path.name}")

    print("\n모든 CLIP 캐시 생성 완료!")


if __name__ == "__main__":
    build_clip_cache()
