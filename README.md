# ClipShow-CN

ClipShow-CN 是基于开源项目 **ClipShow** 制作的简体中文本地化版本，目标是在不改变核心检测与导出逻辑的前提下，把 Windows 桌面界面、状态提示、设置项和安装程序统一汉化。

## 当前状态

- 主界面：已汉化
- 导入 / 分析 / 审阅 / 导出：已汉化
- 偏好设置、提示词编辑器、动态分析状态：已汉化
- Windows 安装程序：已设置简体中文
- 默认语义提示词：界面显示中文，但内部仍保留原始英文提示词，避免影响 CLIP 语义检测效果
- CI：包含 Python 语法检查、Ruff 检查、中文界面残留扫描和 PySide6 GUI 冒烟启动检查

## 下载 Windows 中文版

最新稳定构建：**v0.4.0-cn-12**

- **Full 完整版（推荐）**：约 497 MB，已内置 CLIP 语义模型，安装后更省事。
- **Lite 精简版**：约 170 MB，不内置 CLIP 模型；首次启用语义分析时会自动下载并缓存模型。

Release 页面：
https://github.com/youzhi1701/ClipShow-CN/releases/tag/v0.4.0-cn-12

直接下载：
- Full：https://github.com/youzhi1701/ClipShow-CN/releases/download/v0.4.0-cn-12/ClipShow-CN-0.4.0-full-setup.exe
- Lite：https://github.com/youzhi1701/ClipShow-CN/releases/download/v0.4.0-cn-12/ClipShow-CN-0.4.0-lite-setup.exe

## SHA256 校验

- Full：`c9678b71be7b590f065d0a8152f9a087a69c17a96433e88d7628a41c34659490`
- Lite：`0056d240ae03151a735d643ffdc1fbec6990e0e557402ebb5137ab54da38f64a`

## Windows 使用

正式构建会生成两种 Windows 安装包：

- **Lite**：不内置大模型，体积较小，需要时再下载模型
- **Full**：内置相关模型，安装包较大，首次使用更省事

构建产物可在仓库的 **Actions / Release** 中下载。

## 源项目

上游项目：`borgel/clipshow`

本仓库保留原项目 MIT License。中文化仅针对界面与用户可见提示，不改变视频分析、检测器评分、编码与导出核心逻辑。

## 本地运行

```bash
python -m clipshow
```

检查中文界面：

```bash
python scripts/check_chinese_ui.py
```

## 说明

内部参数名、模型名、FFmpeg/编解码器名称、YAML 配置字段等技术标识保持英文，以保证兼容性；用户实际看到的界面标签、按钮、提示、状态和安装向导以中文为主。
