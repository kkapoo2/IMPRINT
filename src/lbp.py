
import cv2
import numpy as np


def extract_lbp_histogram(image, points=8, radius=1):
    """
    LBP 특징 추출 및 히스토그램 생성

    Parameters:
        image: 이미지 경로 또는 OpenCV 이미지 배열
        points: 주변 픽셀 개수
        radius: 주변 픽셀 탐색 반경

    Returns:
        정규화된 LBP 히스토그램
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

    # LBP 연산
    height, width = gray.shape
    lbp = np.zeros((height, width), dtype=np.uint8)

    neighbors = [
        (-1, -1), (-1, 0), (-1, 1),
        (0, 1),
        (1, 1), (1, 0), (1, -1),
        (0, -1)
    ]

    for i, (dy, dx) in enumerate(neighbors):
        shifted = np.roll(
            gray,
            shift=(-dy * radius, -dx * radius),
            axis=(0, 1)
        )

        lbp |= ((shifted >= gray).astype(np.uint8) << i)

    # 히스토그램 생성
    hist, _ = np.histogram(
        lbp.ravel(),
        bins=256,
        range=(0, 256)
    )

    # 정규화
    hist = hist.astype(np.float32)
    hist /= (hist.sum() + 1e-7)

    return hist


def calculate_lbp_similarity(hist1, hist2):
    """
    두 LBP 히스토그램의 유사도 계산

    Returns:
        0~100 사이의 유사도
    """

    similarity = np.minimum(hist1, hist2).sum()

    return float(similarity * 100)
