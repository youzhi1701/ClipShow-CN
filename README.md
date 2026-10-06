# ClipShow-CN

ClipShow-CN 是基于开源项目 **ClipShow** 维护的简体中文版本，用于从视频素材中辅助筛选片段并生成高光集锦。

中文维护的原则是：**尽量完整汉化用户实际看到的界面，同时不改变原项目检测、评分、编码和导出核心逻辑。**

---

## 当前版本

- 上游应用版本：**0.4.0**
- 当前中文稳定构建：**v0.4.0-cn-12**
- Python：**3.11–3.12**
- 桌面框架：**PySide6**

---

## 主要能力

项目保留 ClipShow 原有的视频分析与导出能力，包括：

- 视频导入与素材管理
- 自动分析与片段检测
- 高光片段审阅
- 视频导出
- 设置与偏好项
- 提示词编辑
- 语义分析相关能力
- 可选模型能力

中文版本额外维护：
- 主界面中文化
- 导入 / 分析 / 审阅 / 导出流程中文化
- 偏好设置中文化
- 动态分析状态和错误提示中文化
- Windows 安装程序中文化
- 用户可见文本残留扫描
- GUI 冒烟启动检查

> 默认语义提示词在界面中可使用中文说明，但模型内部仍保留必要的原始英文提示，以避免改变 CLIP 语义检测效果。

---

## Windows 中文版

当前稳定版本：

**v0.4.0-cn-12**

提供两类安装包：

### Full 完整版
- 约 497 MB
- 内置 CLIP 语义模型
- 更适合希望安装后直接使用的用户

### Lite 精简版
- 约 170 MB
- 不内置 CLIP 模型
- 首次启用语义分析时按需要下载并缓存模型

Release：

https://github.com/youzhi1701/ClipShow-CN/releases/tag/v0.4.0-cn-12

---

## 从源码运行

### 1. 准备 Python

需要：

```text
Python >= 3.11, < 3.13
```

### 2. 安装项目

在仓库目录执行：

```bash
pip install -e .
```

如需全部可选分析能力：

```bash
pip install -e ".[all]"
```

### 3. 启动

```bash
python -m clipshow
```

安装后也可使用：

```bash
clipshow
```

---

## 可选依赖

项目按能力拆分了可选依赖：

- `semantic`：语义分析
- `emotion`：情绪相关模型能力
- `audiovisual`：音视频模型能力
- `all`：安装全部可选模型依赖
- `test`：测试与代码质量工具

---

## 项目结构

```text
ClipShow-CN/
├─ clipshow/
│  ├─ detection/      # 检测逻辑
│  ├─ export/         # 导出逻辑
│  ├─ model/          # 数据与模型层
│  ├─ ui/             # PySide6 界面
│  ├─ workers/        # 后台任务
│  ├─ app.py
│  ├─ config.py
│  └─ __main__.py
├─ packaging/         # Windows 打包相关
├─ scripts/           # 检查与维护脚本
├─ .github/           # CI / Actions
├─ pyproject.toml
├─ uv.lock
└─ README.md
```

---

## 检查与维护

检查中文界面：

```bash
python scripts/check_chinese_ui.py
```

仓库 CI 还会执行：
- Python 语法检查
- Ruff
- 中文界面残留扫描
- PySide6 GUI 冒烟启动检查

---

## 中文化边界

以下内容原则上保持原始英文技术标识，不强行翻译：

- 内部参数名
- 配置键
- 模型名
- FFmpeg / 编解码器名称
- YAML 字段
- API / 协议字段
- 可能影响模型语义的内部提示词

这样可以减少“为了汉化而破坏程序逻辑”的风险。

---

## 上游项目与许可证

- 上游项目：`borgel/clipshow`
- 本仓库：`youzhi1701/ClipShow-CN`
- 许可证：MIT

本仓库保留原项目许可证。中文维护主要聚焦用户界面、本地化体验、安装构建与验证流程。
