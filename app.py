from flask import Flask, render_template, request, jsonify, session
from pathlib import Path
import uuid

from src.analyzer import analyze_image


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

# session 사용을 위한 키
app.secret_key = "imprint-secret-key"

# =========================
# 업로드 폴더
# =========================

UPLOAD_FOLDER = Path("static/uploads")

UPLOAD_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# =========================
# HOME
# =========================

@app.route("/")
def home():
    return render_template("index.html")


# =========================
# ABOUT
# =========================

@app.route("/about.html")
def about():
    return render_template("about.html")


# =========================
# ANALYSIS PAGE
# =========================

@app.route("/analysis.html")
def analysis_page():

    return render_template(
        "analysis.html"
    )


# =========================
# UPLOAD
# =========================

@app.route("/analyze", methods=["POST"])
def analyze():

    image = request.files.get("image")

    if image is None or image.filename == "":
        return "이미지를 선택해주세요."

    extension = Path(
        image.filename
    ).suffix.lower()

    allowed_extensions = {
        ".jpg",
        ".jpeg",
        ".png"
    }

    if extension not in allowed_extensions:
        return "JPG, JPEG, PNG 파일만 업로드할 수 있습니다."

    # UUID 파일명
    filename = f"{uuid.uuid4()}{extension}"

    image_path = UPLOAD_FOLDER / filename

    # 이미지 저장
    image.save(image_path)

    # 현재 세션에서 업로드한 파일명 저장
    session["uploaded_filename"] = filename 

    # 분석 페이지로 이동
    return render_template(
        "analysis.html",
        image_path=f"/static/uploads/{filename}"
    )


# =========================
# ACTUAL ANALYSIS
# =========================

@app.route("/run-analysis", methods=["POST"])
def run_analysis():

    image_path = request.form.get("image_path")

    if not image_path:
        return jsonify({
            "success": False,
            "message": "이미지 경로가 없습니다."
        })

    try:
        # 전달된 이미지 경로에서 파일명 추출
        filename = image_path.rsplit("/", 1)[-1]

        # 현재 세션에서 업로드한 파일인지 확인
        if filename != session.get("uploaded_filename"):
            raise ValueError("현재 업로드한 이미지가 아닙니다.")

        # UUID 파일명 확인
        try:
            uuid.UUID(Path(filename).stem)
        except ValueError:
            raise ValueError("올바르지 않은 이미지 경로입니다.")

        # 확장자 확인
        if Path(filename).suffix.lower() not in {".jpg", ".jpeg", ".png"}:
            raise ValueError("지원하지 않는 이미지 형식입니다.")

        # 업로드 폴더 안의 파일만 사용
        upload_dir = UPLOAD_FOLDER.resolve()
        safe_path = upload_dir / filename

        if not safe_path.is_file():
            raise FileNotFoundError("업로드한 이미지를 찾을 수 없습니다.")

        # 실제 이미지 분석
        result = analyze_image(str(safe_path))

        # 분석 결과 저장
        session["analysis_result"] = result
        session["image_path"] = f"/static/uploads/{filename}"

        return jsonify({
            "success": True
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        })


# =========================
# RESULT
# =========================

@app.route("/result")
def result_page():

    result = session.get("analysis_result")
    image_path = session.get("image_path")

    # 분석 없이 /result에 직접 접근한 경우
    if result is None:
        return "분석 결과가 없습니다. 이미지를 먼저 분석해주세요."

    return render_template(
        "result.html",
        result=result,
        image_path=image_path
    )


# =========================
# RUNpython app.py
# =========================

if __name__ == "__main__":

    app.run(
        debug=True
    )