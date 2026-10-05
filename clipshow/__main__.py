"""Entry point for ClipShow - handles CLI arg parsing."""

import argparse
import sys

from clipshow import __version__


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="clipshow",
        description="从视频素材中自动生成高光集锦",
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="要处理的视频文件",
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="以自动模式运行（不打开完整界面）",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="完全不显示图形界面（用于脚本/批处理，自动启用 --auto）",
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="输出文件路径（默认：highlight_reel.mp4）",
    )
    parser.add_argument(
        "--workers", "-j",
        type=int,
        default=None,
        help="并行任务数量（默认：自动按 CPU 核心数）",
    )
    parser.add_argument(
        "--config", "-c",
        type=str,
        default=None,
        help="YAML 流程配置文件路径",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    args = parser.parse_args(argv)
    if args.headless:
        args.auto = True
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if args.auto:
        from clipshow.app import run_auto_mode

        # Load YAML config if provided
        config = None
        if args.config:
            from clipshow.yaml_config import load_pipeline_config

            config = load_pipeline_config(args.config)

        # Precedence: CLI positional args > YAML inputs
        files = args.files if args.files else (config.inputs if config else [])

        # Precedence: CLI --output > YAML output.path > default
        output = args.output or (config.output_path if config else None) or "highlight_reel.mp4"

        # Precedence: CLI --workers > YAML workers > default
        workers = args.workers if args.workers is not None else (
            config.workers if config and config.workers is not None else 0
        )

        return run_auto_mode(files, output, headless=args.headless, workers=workers, config=config)
    else:
        from clipshow.app import run_gui

        return run_gui(args.files)


if __name__ == "__main__":
    sys.exit(main())
