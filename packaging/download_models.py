"""Download ONNX models for bundling in full release builds.

Downloads models to packaging/bundled_models/ where the PyInstaller specs
pick them up. Also downloads CLIP models into the onnx_clip package data
directory so collect_data_files() includes them.
"""

import os
import shutil
import urllib.request
from pathlib import Path

MODELS = {
    "emotion-ferplus-8.onnx": (
        "https://github.com/onnx/models/raw/main/validated/vision/"
        "body_analysis/emotion_ferplus/model/emotion-ferplus-8.onnx"
    ),
}

CLIP_MODELS = {
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


def download(urls: str | list[str], dest: Path) -> None:
    if dest.exists() and dest.stat().st_size > 0:
        print(f"  Already exists: {dest} ({dest.stat().st_size / 1024 / 1024:.1f}MB)")
        return

    if isinstance(urls, str):
        urls = [urls]

    print(f"  Downloading: {dest.name} ...")
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_name(f"{dest.name}.{os.getpid()}.part")
    errors: list[str] = []

    for url in urls:
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "ClipShow-CN/0.4"},
            )
            with urllib.request.urlopen(req, timeout=180) as response, open(
                tmp, "wb"
            ) as output:
                shutil.copyfileobj(response, output, length=1024 * 1024)
            if tmp.stat().st_size <= 0:
                raise RuntimeError("downloaded file is empty")
            os.replace(tmp, dest)
            print(f"  Done: {dest.stat().st_size / 1024 / 1024:.1f}MB")
            return
        except Exception as exc:
            tmp.unlink(missing_ok=True)
            errors.append(f"{url}: {exc}")

    raise RuntimeError(
        f"Failed to download {dest.name} from all mirrors:\n"
        + "\n".join(errors)
    )


def main():
    script_dir = Path(__file__).resolve().parent
    bundled_dir = script_dir / "bundled_models"

    print("Downloading models for full build...")

    # 1. Emotion model -> bundled_models/
    for filename, url in MODELS.items():
        download(url, bundled_dir / filename)

    # 2. CLIP models -> onnx_clip package data directory
    #    (so collect_data_files('onnx_clip') includes them)
    try:
        import onnx_clip
        onnx_clip_data = Path(onnx_clip.__file__).parent / "data"
    except ImportError:
        print("WARNING: onnx_clip not installed, skipping CLIP model download")
        return

    for filename, urls in CLIP_MODELS.items():
        download(urls, onnx_clip_data / filename)

    print("\nAll models downloaded successfully.")
    total = sum(
        f.stat().st_size
        for d in [bundled_dir, onnx_clip_data]
        if d.exists()
        for f in d.iterdir()
        if f.suffix == ".onnx"
    )
    print(f"Total ONNX model size: {total / 1024 / 1024:.0f}MB")


if __name__ == "__main__":
    main()
