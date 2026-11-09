from functools import lru_cache
import os
from pathlib import Path

import open_clip
import torch
torch.set_num_threads(1)
from PIL import Image

STYLE_DATASETS = {
    "ghibli": "dataset/ghibli",
    "disney": "dataset/disney",
    "simpsons": "dataset/simpsons",
}

BASE_DIR = Path(__file__).resolve().parent.parent

CACHE_DIR = BASE_DIR / "models" / "clip_embeddings"

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}


@lru_cache(maxsize=1)
def load_clip_model():
    """
    CLIP 모델을 CPU에서 한 번 로드하고,
    메모리 사용량을 줄이기 위해 FP16으로 변환한다.
    """
    torch.set_num_threads(1)

    model, _, preprocess = open_clip.create_model_and_transforms(
        "ViT-B-32",
        pretrained="openai",
        device="cpu",
    )

    model = model.eval().half()

    return model, preprocess


def get_image_embedding(image_path, model, preprocess):
    """
    이미지를 CLIP embedding으로 변환한다.
    """
    with Image.open(image_path) as img:
        image = preprocess(img.convert("RGB")).unsqueeze(0)

    image = image.half()

    with torch.inference_mode():
        embedding = model.encode_image(image)

        # 유사도 계산과 기존 캐시 호환성을 위해 FP32로 변환
        embedding = embedding.float()
        embedding = embedding / embedding.norm(
            dim=-1,
            keepdim=True
        )

    return embedding


def calculate_clip_similarity(embedding1, embedding2):
    """
    두 CLIP embedding 사이의 cosine similarity를 계산하는 함수.

    Args:
        embedding1 (torch.Tensor): 첫 번째 이미지 embedding
        embedding2 (torch.Tensor): 두 번째 이미지 embedding

    Returns:
        float: 두 이미지의 CLIP 유사도
    """
    similarity = (embedding1 @ embedding2.T).item()

    return similarity

@lru_cache(maxsize=3)
def load_clip_cache(style):
    """
    저장된 CLIP embedding 캐시를 불러온다.

    Args:
        style (str): 화풍 이름 (ghibli, disney, simpsons)

    Returns:
        torch.Tensor: 데이터셋 이미지들의 embedding
    """
    cache_path = CACHE_DIR / f"{style}.pt"

    if not cache_path.exists():
        raise FileNotFoundError(
            f"CLIP 캐시가 없습니다: {cache_path}\n"
            "python -m src.build_clip_cache를 먼저 실행하세요."
        )

    cache = torch.load(
        cache_path,
        map_location="cpu",
        weights_only=True
    )

    if (
        cache["model_name"] != "ViT-B-32"
        or cache["pretrained"] != "openai"
    ):
        raise ValueError(
            f"CLIP 모델과 캐시 정보가 일치하지 않습니다: {style}"
        )

    return cache["embeddings"]

def compare_with_clip_cache(input_embedding, style):
    """
    입력 이미지와 저장된 화풍별 embedding을 비교해
    평균 cosine similarity를 반환한다.
    """

    dataset_embeddings = load_clip_cache(style)

    # 입력 벡터 [1, 512]
    # 데이터셋 벡터 [N, 512]
    # 결과 [1, N]
    similarities = input_embedding.cpu() @ dataset_embeddings.T

    # 기존과 동일하게 전체 평균 사용
    return similarities.mean().item()


def compare_with_dataset(
    input_embedding,
    dataset_path,
    model,
    preprocess
):
    """
    입력 이미지와 특정 화풍 데이터셋의 모든 이미지를 비교하고
    평균 CLIP 유사도를 계산하는 함수.

    Args:
        input_embedding (torch.Tensor): 입력 이미지 embedding
        dataset_path (str): 데이터셋 폴더 경로
        model: CLIP 이미지 인코더
        preprocess: CLIP 전용 이미지 전처리기

    Returns:
        float: 데이터셋의 평균 CLIP cosine similarity
    """
    similarities = []

    for filename in os.listdir(dataset_path):

        extension = os.path.splitext(filename)[1].lower()

        if extension not in ALLOWED_EXTENSIONS:
            continue

        image_path = os.path.join(
            dataset_path,
            filename
        )

        dataset_embedding = get_image_embedding(
            image_path,
            model,
            preprocess
        )

        similarity = calculate_clip_similarity(
            input_embedding,
            dataset_embedding
        )

        similarities.append(similarity)

    if not similarities:
        raise ValueError(
            f"분석 가능한 이미지가 없습니다: {dataset_path}"
        )

    average_similarity = (
        sum(similarities) / len(similarities)
    )

    return average_similarity

def compare_all_styles(
    input_embedding,
    model,
    preprocess
):
    """
    저장된 CLIP 캐시를 사용해
    화풍별 평균 cosine similarity를 계산한다.
    """
    results = {}

    for style in STYLE_DATASETS:
        score = compare_with_clip_cache(
            input_embedding,
            style
        )

        results[style] = score

    return results


def analyze_clip_image(image_path):
    model, preprocess = load_clip_model()

    input_embedding = get_image_embedding(
        image_path,
        model,
        preprocess
    )

    results = compare_all_styles(
        input_embedding,
        model,
        preprocess
    )

    return {
        "Ghibli": results["ghibli"],
        "Disney": results["disney"],
        "Simpsons": results["simpsons"]
    }
