# IMPRINT
# IMPRINT

IMPRINT는 이미지의 색상, 의미적 특징, 질감 패턴을 분석하여 입력 이미지와 가장 유사한 애니메이션 화풍을 분류하는 웹 애플리케이션입니다.

## 1. 프로젝트 소개

IMPRINT는 다음 세 가지 애니메이션 화풍을 분석합니다.

- Ghibli
- Disney
- Simpsons

이미지 분석에는 세 가지 기법을 사용합니다.

| 분석 기법 | 설명 | 가중치 |
|---|---|---|
| Color Histogram | 이미지의 색상 분포 비교 | 60% |
| CLIP | 이미지의 시각적·의미적 특징 비교 | 30% |
| LBP | 이미지의 국소 질감 패턴 비교 | 10% |

각 분석 결과를 결합하여 가장 유사한 화풍을 제시합니다.

## 2. 실행 환경

- Python 3.13
- Flask
- PyTorch (CPU)
- OpenCLIP
- OpenCV
- scikit-image
- Pillow

현재 로컬 개발 환경은 Windows 기준입니다.

## 3. 설치 방법

### 3.1 프로젝트 다운로드

GitHub에서 프로젝트를 Clone하거나 ZIP 파일로 다운로드합니다.

프로젝트 폴더로 이동합니다.

```powershell
cd IMPRINT
```

### 3.2 가상환경 생성

```powershell
python -m venv .venv
```

Windows PowerShell에서 가상환경을 활성화합니다.

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3.3 라이브러리 설치

```powershell
python -m pip install -r requirements.txt
```

설치 상태를 확인합니다.

```powershell
python -m pip check
```

## 4. 환경변수 설정

프로젝트 최상위 폴더에 `.env` 파일을 생성합니다.

```dotenv
SECRET_KEY=your_random_secret_key
```

비밀키는 다음 명령어로 생성할 수 있습니다.

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

출력된 값을 `SECRET_KEY`에 설정합니다.

`.env` 파일은 Git에 업로드하지 않습니다.

## 5. CLIP 캐시 생성

IMPRINT는 화풍별 데이터셋 이미지의 CLIP 임베딩을 미리 생성하여 사용합니다.

프로젝트의 `dataset/` 폴더에 Ghibli, Disney, Simpsons 이미지 데이터셋이 준비되어 있어야 합니다.

다음 명령어로 캐시를 생성합니다.

```powershell
python -m src.build_clip_cache
```

생성된 파일은 다음 위치에 저장됩니다.

```text
models/
└── clip_embeddings/
    ├── ghibli.pt
    ├── disney.pt
    └── simpsons.pt
```

최초 실행 시 CLIP 모델 가중치를 다운로드하기 위해 인터넷 연결이 필요할 수 있습니다.

## 6. 웹사이트 실행

프로젝트 최상위 폴더에서 다음 명령어를 실행합니다.

```powershell
python app.py
```

웹 브라우저에서 다음 주소로 접속합니다.

http://127.0.0.1:5000

## 7. 사용 방법

1. Home 화면에서 JPG, JPEG 또는 PNG 이미지를 업로드합니다.
2. Analysis 화면에서 이미지 분석이 진행됩니다.
3. Result 화면에서 가장 유사한 화풍과 분석 결과를 확인합니다.
4. 다른 이미지를 업로드하여 다시 분석할 수 있습니다.

업로드 가능한 파일의 최대 크기는 10MB입니다.

## 8. 학술제 현장 실행

학술제 현장에서는 인터넷 연결 없이 로컬 서버로 실행할 수 있도록 준비합니다.

사전에 다음 사항을 확인해야 합니다.

- Python 및 라이브러리 설치 완료
- CLIP 모델 가중치 다운로드 완료
- CLIP 임베딩 캐시 생성 완료
- 이미지 분석 기능 정상 작동
- 인터넷 연결을 해제한 상태에서 실행 테스트 완료

## 9. 주의사항

- 본 프로그램의 결과는 이미지 특징에 기반한 화풍 유사도 분석 결과입니다.
- 실제 제작사 또는 원작자를 확정하는 기능이 아닙니다.
- 분석 정확도는 데이터셋 구성과 입력 이미지에 따라 달라질 수 있습니다.
- 온라인 공개 배포에는 별도의 운영용 웹 서버 및 추가 보안 설정이 필요합니다.
