"""ClipShow-CN localization and GUI smoke checks."""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from clipshow.ui.main_window import MainWindow

FORBIDDEN_UI_PHRASES = [
    "1. Import",
    "2. Analyze",
    "3. Review",
    "4. Export",
    "Back",
    "Next",
    "Preferences…",
    "Detector Weights",
    "Edit Prompts…",
    "Auto-balance weights",
    "Score threshold:",
    "Analyze All",
    "Clear All",
    "Remove Selected",
    "No segment selected",
    "No segments loaded",
    "Encoding Settings",
    "Save Highlight Reel",
    "Reset to Defaults",
    "Max workers:",
    "Play",
    "Pause",
]

def static_scan() -> None:
    root = Path(__file__).resolve().parents[1] / "clipshow" / "ui"
    failures: list[str] = []
    for path in sorted(root.glob("*.py")):
        text = path.read_text(encoding="utf-8")
        for phrase in FORBIDDEN_UI_PHRASES:
            if phrase in text:
                failures.append(f"{path.name}: {phrase}")
    if failures:
        raise SystemExit("发现未汉化的界面文本:\n" + "\n".join(failures))

def gui_smoke() -> None:
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    expected_tabs = ["1. 导入", "2. 分析", "3. 审阅", "4. 导出"]
    actual_tabs = [window.tabs.tabText(i) for i in range(window.tabs.count())]
    assert actual_tabs == expected_tabs, (actual_tabs, expected_tabs)
    assert window.back_button.text() == "上一步"
    assert window.next_button.text() == "下一步"
    assert "偏好设置" in window.preferences_action.text()
    window.close()
    app.processEvents()

if __name__ == "__main__":
    static_scan()
    gui_smoke()
    print("ClipShow-CN 中文界面检查通过")
