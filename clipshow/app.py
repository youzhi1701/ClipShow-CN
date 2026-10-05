"""QApplication setup and auto-mode runner."""

from __future__ import annotations

import sys


def run_gui(files: list[str] | None = None) -> int:
    """Launch the full ClipShow GUI."""
    from PySide6.QtWidgets import QApplication

    from clipshow.ui.main_window import MainWindow

    app = QApplication(sys.argv)
    app.setApplicationName("ClipShow 中文版")
    app.setOrganizationName("ClipShow")

    window = MainWindow()
    if files:
        window.import_panel.add_files(files)
    window.show()

    return app.exec()


def run_auto_mode(
    files: list[str],
    output_path: str,
    headless: bool = False,
    workers: int = 0,
    config: object | None = None,
) -> int:
    """Run automatic highlight reel generation.

    Loads files, runs ffprobe for metadata, runs the detection pipeline
    with default settings, takes all segments above threshold sorted
    chronologically, assembles via MoviePy, and writes output.

    Returns 0 on success, 1 on failure.
    """
    if not files:
        print("错误：未指定输入视频文件", file=sys.stderr)
        return 1

    from clipshow.config import Settings
    from clipshow.detection.pipeline import DetectionPipeline
    from clipshow.export.assembler import assemble_highlights
    from clipshow.export.ffprobe import extract_metadata
    from clipshow.model.moments import HighlightSegment

    if config is not None:
        from clipshow.yaml_config import apply_config_to_settings

        settings = apply_config_to_settings(config)
    else:
        settings = Settings()

    # CLI auto mode uses sensible defaults when no detectors are configured
    if not settings.enabled_detectors:
        settings.scene_weight = 0.3
        settings.audio_weight = 0.25
        settings.motion_weight = 0.25
        settings.emotion_weight = 0.2
    if workers:
        settings.max_workers = workers
    pipeline = DetectionPipeline(settings)

    # Step 1: Extract metadata
    sources = []
    for path in files:
        try:
            source = extract_metadata(path)
            sources.append(source)
            if not headless:
                print(
                    f"  已加载：{path}（{source.duration:.1f} 秒，"
                    f"{source.width}x{source.height}）"
                )
        except (FileNotFoundError, RuntimeError) as e:
            print(f"错误：读取 {path} 失败：{e}", file=sys.stderr)
            return 1

    # Step 2: Run detection pipeline
    if not headless:
        print("正在分析视频...")

    video_paths = [(s.path, s.duration) for s in sources]

    def on_progress(p: float) -> None:
        if not headless:
            print(f"  进度：{p:.0%}", end="\r")

    moments = pipeline.analyze_all(video_paths, progress_callback=on_progress)

    if not headless:
        print(f"\n  找到 {len(moments)} 个候选高光时刻")

    if not moments:
        print("未检测到高光时刻，请尝试降低评分阈值。", file=sys.stderr)
        return 1

    # Step 3: Convert to segments, sorted chronologically
    segments = [
        HighlightSegment.from_moment(m, order=i) for i, m in enumerate(moments)
    ]
    segments.sort(key=lambda s: (s.source_path, s.start_time))

    # Step 4: Assemble output
    if not headless:
        total_dur = sum(s.duration for s in segments)
        print(f"正在合成 {len(segments)} 个片段（总时长 {total_dur:.1f} 秒）...")

    try:
        assemble_highlights(
            segments,
            output_path=output_path,
            codec=settings.output_codec,
            fps=settings.output_fps,
            bitrate=settings.output_bitrate,
        )
    except (ValueError, RuntimeError) as e:
        print(f"错误：导出失败：{e}", file=sys.stderr)
        return 1

    if not headless:
        print(f"完成！文件已保存到：{output_path}")

    return 0
