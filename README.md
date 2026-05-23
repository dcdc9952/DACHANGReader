# 大昌阅读器 (DACHANG Reader)

一个简洁美观的本地电子书阅读器，支持TXT、EPUB、PDF等多种格式。

## 功能特点

- **多格式支持**: TXT直接阅读（内置），EPUB、PDF可选支持
- **多彩圆角UI**: 所有按钮采用圆角设计，界面多彩时尚
- **四大主题模式**: 日光模式、羊皮纸模式、夜间模式、护眼模式
- **自定义阅读**: 字体大小(14-32px)、行间距(1.0-3.0倍)自由调节
- **书库管理**: 卡片网格展示、搜索过滤、阅读进度保存
- **快捷操作**: 
  - `Ctrl + O` 导入书籍
  - `方向键` 上下翻页
  - `Page Up/Down` 快速翻页
  - `F11` 全屏切换
  - `Esc` 退出全屏
  - `Ctrl + F` 搜索书籍
  - `+ / -` 调节字体大小
  - `Ctrl + Q` 退出程序

## 界面预览

- 左侧彩虹导航栏（红/橙/黄/绿/青/蓝/紫）
- 顶部多彩工具栏按钮
- 书库卡片网格展示（多彩渐变配色）
- 四套阅读主题任意切换

## 快速开始

### 方式一：直接运行（推荐）

1. 双击 `一键构建大昌阅读器.bat`
2. 等待自动下载Python并安装依赖（约10-15分钟）
3. 完成后自动运行程序

### 方式二：源码运行

```bash
# 安装依赖
pip install PyQt5

# 运行程序
python dachang_reader.py
```

### 方式三：从源码构建exe

```bash
# 安装构建工具
pip install pyinstaller

# 打包exe
pyinstaller --onefile --windowed --name DACHANGReader dachang_reader.py

# exe文件在 dist/ 目录
```

## 项目结构

```
DACHANGReader/
├── dachang_reader.py          # 主程序源码
├── 一键构建大昌阅读器.bat      # Windows一键构建脚本
├── requirements.txt           # Python依赖列表
├── README.md                 # 本说明文件
└── books/                    # 书籍存放文件夹（运行时自动创建）
```

## 运行环境

- Windows 10/11
- macOS（需安装PyQt5）
- Linux（需安装PyQt5）

## 版本历史

### v1.0.0 (2026-05-23)
- 首版发布
- 支持TXT阅读
- 多彩圆角UI界面
- 四套阅读主题
- 书库管理功能
- 阅读进度保存
- 快捷键支持

## 技术栈

- **GUI框架**: PyQt5
- **语言**: Python 3.8+
- **打包工具**: PyInstaller

## 后续计划

- [ ] EPUB格式内置支持
- [ ] PDF格式内置支持
- [ ] 书摘笔记功能
- [ ] 阅读统计
- [ ] 主题自定义颜色
- [ ] 多语言支持

## 许可证

MIT License

## 作者

大昌 | AI助手

---

*如果觉得好用，欢迎在GitHub上给个Star！*