
import cv2
import numpy as np
from skimage.feature import local_binary_pattern


def extract_lbp_histogram(image, points=8, radius=1):
    """
    Uniform LBP 특징 추출 및 히스토그램 생성
    """

    # 이미지 불러오기
    if isinstance(image, str):
        image = cv2.imread(image)

    if image is None:
        raise ValueError("이미지를 불러올 수 없습니다.")

    # 그레이스케일 변환
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    gray = gray.astype(np.uint8)

    # Uniform LBP 연산
    lbp = local_binary_pattern(
        gray,
        P=points,
        R=radius,
        method="uniform"
    )

    # 히스토그램 생성
    bins = points + 2

    hist, _ = np.histogram(
        lbp.ravel(),
        bins=bins,
        range=(0, bins)
    )

    # 정규화
    hist = hist.astype(np.float32)
    hist /= (hist.sum() + 1e-7)

    return hist


def calculate_lbp_similarity(hist1, hist2):
    """
    Chi-square distance 기반 유사도
    """

    eps = 1e-10

    distance = 0.5 * np.sum(
        ((hist1 - hist2) ** 2) /
        (hist1 + hist2 + eps)
    )

    # 거리 기반 유사도 변환
    similarity = np.exp(-distance)

    return float(similarity * 100)
