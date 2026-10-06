# ClipShow-CN

> 基于 ClipShow 维护的简体中文桌面版，用于从视频素材中辅助筛选片段并生成高光集锦。

| 项目 | 信息 |
| --- | --- |
| 当前中文稳定版 | **v0.4.0-cn-12** |
| 上游应用版本 | **0.4.0** |
| 桌面框架 | PySide6 |
| 当前状态 | 正式发布 / 持续维护 |

---

## 项目概览

ClipShow-CN 的维护目标是：**尽量完整汉化用户实际看到的界面，同时不改变原项目检测、评分、编码和导出核心逻辑。**

中文维护覆盖主界面、导入、分析、审阅、导出、设置、动态状态、错误提示和 Windows 安装程序；内部技术字段、模型标识与可能影响模型效果的英文提示会按兼容性原则保留。

---

## 核心能力

项目保留 ClipShow 原有视频分析与导出能力，包括：

- 视频导入与素材管理
- 自动分析与片段检测
- 高光片段审阅
- 视频导出
- 设置与偏好项
- 提示词编辑
- 语义分析
- 可选模型能力

中文版本额外维护：

- 主界面中文化
- 导入 / 分析 / 审阅 / 导出流程中文化
- 偏好设置中文化
- 动态分析状态和错误提示中文化
- Windows 安装程序中文化
- 用户可见文本残留扫描
- GUI 冒烟启动检查

---

## 快速开始

### Windows 正式版

当前稳定版本：**v0.4.0-cn-12**

提供两类安装包：

**Full 完整版**
- 内置 CLIP 语义模型
- 适合希望安装后直接使用的用户

**Lite 精简版**
- 不内置 CLIP 模型
- 首次启用语义分析时按需下载并缓存模型

普通用户优先从 GitHub Releases 下载 Windows 安装包。

### 从源码运行

环境要求：

```text
Python >= 3.11, < 3.13
```

安装：

```bash
pip install -e .
```

安装全部可选能力：

```bash
pip install -e ".[all]"
```

启动：

```bash
python -m clipshow
```

或：

```bash
clipshow
```

---

## 可选依赖

- `semantic`：语义分析
- `emotion`：情绪相关模型能力
- `audiovisual`：音视频模型能力
- `all`：安装全部可选模型依赖
- `test`：测试与代码质量工具

---

## 构建与发布

仓库 GitHub Actions 包含：

- Python 语法与 Ruff 检查
- 中文界面残留扫描
- PySide6 GUI 冒烟启动
- Windows Lite / Full 安装包构建
- macOS 构建
- Linux Flatpak 构建
- GitHub Release 发布

正式 Windows 中文版由发布流水线构建，不以源码 ZIP 代替安装版。

---

## 项目结构

```text
ClipShow-CN/
├─ clipshow/
│  ├─ detection/
│  ├─ export/
│  ├─ model/
│  ├─ ui/
│  ├─ workers/
│  ├─ app.py
│  ├─ config.py
│  └─ __main__.py
├─ packaging/
├─ scripts/
├─ .github/
├─ pyproject.toml
├─ uv.lock
└─ README.md
```

---

## 汉化边界

以下内容原则上保持原始英文技术标识：

- 内部参数名
- 配置键
- 模型名
- FFmpeg / 编解码器名称
- YAML 字段
- API / 协议字段
- 可能影响模型语义的内部提示词

这样可以减少“为了汉化而破坏程序逻辑”的风险。

---

## 上游与许可证

- 上游项目：`borgel/clipshow`
- 中文维护：`youzhi1701/ClipShow-CN`
- 许可证：MIT

本仓库保留原项目许可证和版权信息。

---

## 发布与维护

当前正式版本：**v0.4.0-cn-12**

发布原则：
- 用户可见中文界面先验证再发布
- Lite / Full 安装包保持明确区分
- 安装产物与版本号一致
- 不为“测试变绿”而破坏原项目核心逻辑