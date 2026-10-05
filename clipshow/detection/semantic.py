"""Semantic content detection via CLIP (ONNX Runtime, no PyTorch).

Lazy-loads onnx_clip on first use. Downloads CLIP ViT-B/32 model (~338MB)
to ~/.clipshow/models/ on first use. Samples frames at 2 FPS and scores
against user-configurable text prompts, with negative prompt contrast and
temporal smoothing.
"""

from __future__ import annotations

import importlib
import os
import shutil
import urllib.request
from pathlib import Path

import cv2
import numpy as np
from scipy.ndimage import uniform_filter1d

from clipshow.detection.base import Detector, DetectorResult

DEFAULT_PROMPTS = [
    "exciting moment",
    "people laughing",
    "beautiful scenery",
    "action scene",
]
DEFAULT_NEGATIVE_PROMPTS = [
    "boring static shot",
    "blank wall",
    "empty room",
    "black screen",
]
MODEL_DIR = Path.home() / ".clipshow" / "models"
SAMPLE_FPS = 2  # Sample 2 frames per second

_CLIP_MODEL_URLS = {
    "clip_image_model_vitb32.onnx": [
        "https://models.stimma.ai/clip/clip_image_model_vitb32.onnx",
        (
            "https://www.modelscope.cn/models/cix/ai_model_hub_25_Q3/"
            "resolve/master/models/Generative_AI/Image_to_Text/onnx_clip/"
            "model/clip_visual.onnx"
        ),
    ],
    "clip_text_model_vitb32.onnx": [
        "https://models.stimma.ai/clip/clip_text_model_vitb32.onnx",
        (
            "https://www.modelscope.cn/models/cix/ai_model_hub_25_Q3/"
            "resolve/master/models/Generative_AI/Image_to_Text/onnx_clip/"
            "model/clip_text_model_vitb32.onnx"
        ),
    ],
}


def _download_model(urls: list[str], dest: Path) -> None:
    """Download one model atomically, trying mirrors in order."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.is_file() and dest.stat().st_size > 0:
        return

    errors: list[str] = []
    tmp = dest.with_name(f"{dest.name}.{os.getpid()}.part")
    for url in urls:
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "ClipShow-CN/0.4"},
            )
            with urllib.request.urlopen(req, timeout=120) as response, open(
                tmp, "wb"
            ) as output:
                shutil.copyfileobj(response, output, length=1024 * 1024)
            if tmp.stat().st_size <= 0:
                raise RuntimeError("下载结果为空")
            os.replace(tmp, dest)
            return
        except Exception as exc:
            tmp.unlink(missing_ok=True)
            errors.append(f"{url}: {exc}")

    raise RuntimeError(
        "CLIP 模型下载失败，请检查网络后重试。\n" + "\n".join(errors)
    )


def _ensure_clip_models(cache_dir: Path) -> None:
    for filename, urls in _CLIP_MODEL_URLS.items():
        _download_model(urls, cache_dir / filename)

# Sigmoid normalization parameters for CLIP cosine similarities.
# Raw scores are typically 0.15-0.35 for real matches; this sigmoid
# stretches that range to fill [0, 1] with good contrast.
_SIGMOID_CENTER = 0.25
_SIGMOID_SCALE = 20.0

# Temporal smoothing window size in score samples (not seconds).
# Reduces noise from single-frame outliers.
_SMOOTH_WINDOW = 5


class SemanticDetector(Detector):
    """CLIP-based semantic content scoring.

    Uses onnx_clip (ONNX Runtime) to score video frames against text prompts.
    Scores positive prompts against negative prompts for better contrast,
    applies sigmoid normalization, and smooths temporally.
    """

    name = "semantic"

    def __init__(
        self,
        prompts: list[str] | None = None,
        negative_prompts: list[str] | None = None,
        time_step: float = 0.1,
    ):
        self._prompts = prompts or DEFAULT_PROMPTS
        self._negative_prompts = negative_prompts or DEFAULT_NEGATIVE_PROMPTS
        self._time_step = time_step
        self._model = None

    def _load_model(self):
        """Lazy-load the CLIP model via onnx_clip."""
        try:
            onnx_clip = importlib.import_module("onnx_clip")
        except ImportError:
            raise RuntimeError(
                "onnx_clip is not installed. Install with: "
                "pip install onnx_clip onnxruntime"
            )
        # Suppress noisy CoreML warnings on macOS (CLIP only supports 30/889
        # nodes via CoreML, so ORT falls back to CPU anyway).
        import onnxruntime as ort

        ort.set_default_logger_severity(3)  # 3 = ERROR only
        MODEL_DIR.mkdir(parents=True, exist_ok=True)

        # Full builds bundle the CLIP weights inside onnx_clip/data. Lite builds
        # download them once to ~/.clipshow/models using maintained mirrors.
        try:
            onnx_clip_model = importlib.import_module("onnx_clip.model")
            package_data = Path(onnx_clip_model.__file__).resolve().parent / "data"
            bundled_files = [
                package_data / "clip_image_model_vitb32.onnx",
                package_data / "clip_text_model_vitb32.onnx",
            ]
            has_bundled_models = all(
                path.is_file() and path.stat().st_size > 0 for path in bundled_files
            )
        except (ImportError, OSError):
            has_bundled_models = False

        if has_bundled_models:
            self._model = onnx_clip.OnnxClip(batch_size=1, silent_download=True)
        else:
            _ensure_clip_models(MODEL_DIR)
            self._model = onnx_clip.OnnxClip(
                batch_size=1,
                silent_download=True,
                cache_dir=str(MODEL_DIR),
            )
        return self._model

    def detect(
        self,
        video_path: str,
        progress_callback: callable | None = None,
        cancel_flag: callable | None = None,
    ) -> DetectorResult:
        model = self._model or self._load_model()

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise RuntimeError(f"无法打开视频：{video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0.0
        frame_interval = max(1, int(fps / SAMPLE_FPS))

        num_samples = max(1, int(np.ceil(duration / self._time_step)))
        scores = np.zeros(num_samples, dtype=float)

        # Encode text prompts once
        from PIL import Image

        pos_embeddings = model.get_text_embeddings(self._prompts)
        neg_embeddings = model.get_text_embeddings(self._negative_prompts)

        frame_idx = 0
        while True:
            if cancel_flag and cancel_flag():
                break

            ret, frame = cap.read()
            if not ret:
                break

            if frame_idx % frame_interval == 0:
                # Convert BGR to RGB PIL Image
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(rgb)

                image_embeddings = model.get_image_embeddings([img])

                # Positive vs negative contrast: best positive minus best negative
                pos_sim = float(np.max(image_embeddings @ pos_embeddings.T))
                neg_sim = float(np.max(image_embeddings @ neg_embeddings.T))
                raw = pos_sim - neg_sim

                # Sigmoid normalization for better dynamic range
                score = 1.0 / (1.0 + np.exp(-_SIGMOID_SCALE * (raw - _SIGMOID_CENTER)))
                score = float(np.clip(score, 0.0, 1.0))

                t = frame_idx / fps
                idx = min(int(t / self._time_step), num_samples - 1)
                scores[idx] = max(scores[idx], score)

                if progress_callback:
                    progress_callback(frame_idx / max(total_frames, 1))

            frame_idx += 1

        cap.release()

        # Temporal smoothing to reduce single-frame noise
        if len(scores) >= _SMOOTH_WINDOW:
            scores = uniform_filter1d(scores, size=_SMOOTH_WINDOW)

        # Final normalization to [0, 1]
        max_val = scores.max()
        if max_val > 0:
            scores = scores / max_val

        if progress_callback:
            progress_callback(1.0)

        return DetectorResult(
            name=self.name,
            scores=scores,
            time_step=self._time_step,
            source_path=video_path,
        )
