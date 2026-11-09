const STORAGE_KEY = "imprint-upload";

function showToast(message) {
  const toast = document.querySelector("#toast");
  if (!toast) return;
  toast.textContent = message;
  toast.classList.add("show");
  window.setTimeout(() => toast.classList.remove("show"), 2400);
}

function updateUploadPreview(source, name) {
  const dropzone = document.querySelector("#dropzone");
  const preview = document.querySelector("#selected-preview");
  const title = document.querySelector("#upload-title");
  const description = document.querySelector("#upload-description");
  const label = document.querySelector("#upload-button-label");
  const startButton = document.querySelector("#start-button");
  if (!dropzone || !preview) return;

  preview.src = source;
  dropzone.classList.add("has-image");
  title.textContent = "이미지가 준비되었습니다";
  description.textContent = name || "선택한 이미지";
  label.textContent = "이미지 변경하기";
  startButton.disabled = false;
}

function saveImage(file) {
  if (!file) return;
  if (!["image/jpeg", "image/png"].includes(file.type)) {
    showToast("JPG 또는 PNG 파일만 업로드할 수 있습니다.");
    return;
  }
  if (file.size > 10 * 1024 * 1024) {
    showToast("이미지 크기는 10MB 이하여야 합니다.");
    return;
  }

  const reader = new FileReader();
  reader.addEventListener("load", () => {
    const data = String(reader.result);
    try {
      sessionStorage.setItem(STORAGE_KEY, data);
    } catch {
      showToast("파일이 너무 커서 저장할 수 없습니다.");
      return;
    }
    updateUploadPreview(data, file.name);
  });
  reader.readAsDataURL(file);
}

function setupUpload() {
  const form = document.querySelector("#upload-form");
  const input = document.querySelector("#image-input");
  const dropzone = document.querySelector("#dropzone");
  if (!form || !input || !dropzone) return;

  sessionStorage.removeItem(STORAGE_KEY);

  input.addEventListener("change", () => saveImage(input.files[0]));
  ["dragenter", "dragover"].forEach((eventName) => {
    dropzone.addEventListener(eventName, (event) => {
      event.preventDefault();
      dropzone.classList.add("dragging");
    });
  });
  ["dragleave", "drop"].forEach((eventName) => {
    dropzone.addEventListener(eventName, (event) => {
      event.preventDefault();
      dropzone.classList.remove("dragging");
    });
  });
  dropzone.addEventListener("drop", (event) => {
    event.preventDefault();

    const file = event.dataTransfer.files[0];
    if (!file) return;

    // 실제 파일 입력창에도 반영
    const dataTransfer = new DataTransfer();
    dataTransfer.items.add(file);

    input.files = dataTransfer.files;

    // 미리보기 업데이트
    saveImage(file);
  });
  form.addEventListener("submit", (event) => {
    const file = input.files[0];

    if (!file) {
      event.preventDefault();
      showToast("먼저 분석할 이미지를 선택해주세요.");
      return;
    }

    if (!["image/jpeg", "image/png"].includes(file.type)) {
      event.preventDefault();
      showToast("JPG 또는 PNG 파일만 업로드할 수 있습니다.");
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      event.preventDefault();
      showToast("이미지 크기는 10MB 이하여야 합니다.");
    }
  });
}

function applyStoredImage() {
  const saved = sessionStorage.getItem(STORAGE_KEY);
  if (!saved) return;
  document.querySelectorAll(".stored-image").forEach((image) => {
    image.src = saved;
    image.classList.add("user-image");
  });
}

function setupAnalysis() {
  const progressValue = document.querySelector("#progress-value");
  const progressBar = document.querySelector("#progress-bar");
  const resultLink = document.querySelector("#result-link");
  const message = document.querySelector("#progress-message");
  const steps = [...document.querySelectorAll("[data-step]")];
  if (!progressValue || !progressBar || !steps.length) return;

  let progress = 0;
  const timer = window.setInterval(() => {
    progress = Math.min(100, progress + 1);
    progressValue.textContent = `${progress}%`;
    progressBar.style.width = `${progress}%`;

    const activeStep = progress < 34 ? 0 : progress < 68 ? 1 : 2;
    steps.forEach((step, index) => {
      step.classList.toggle("current", index === activeStep);
      step.classList.toggle("complete", index < activeStep || progress === 100);
      const heading = step.querySelector("strong");
      if (index < activeStep || progress === 100) {
        step.querySelector("b").textContent = "✓";
        heading.textContent = heading.textContent.replace("분석 중", "분석 완료").replace("대기 중", "완료");
      } else if (index === activeStep) {
        heading.textContent = heading.textContent.replace("대기 중", "분석 중");
      }
    });

    if (progress === 100) {
      window.clearInterval(timer);
      message.textContent = "분석이 완료되었습니다.";
      resultLink.classList.remove("is-hidden");
    }
  }, 45);
}

document.addEventListener("DOMContentLoaded", () => {
  setupUpload();
  applyStoredImage();
  setupAnalysis();
});
