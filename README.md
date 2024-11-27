# Pandoc HTML to PDF Converter

一个专业的 HTML 到 PDF 文档转换工具，基于 Pandoc 构建，支持中英文排版，提供灵活的配置选项和完整的 LaTeX 模板系统。

## 功能特点

- ✨ 支持中英文文档转换
- 📚 专业的 LaTeX 模板系统
- 🎨 灵活的样式定制
- 🔧 可配置的转换选项
- 📝 完整的页眉页脚支持
- 📑 自动目录生成
- 🔢 自动添加生成日期

## 系统要求

- Python 3.8+
- Pandoc 2.0+
- TeX Live 2021+（完整版）
- Make（可选）
- macOS 系统字体要求：
  - 中文字体：
    - 宋体-简 (Songti SC) - 正文
    - 苹方 (PingFang SC) - 标题和等宽字体
  - 英文字体：
    - Times New Roman - 正文
    - Helvetica - 标题
    - Menlo - 代码

## 安装

1. **克隆仓库**

```bash
git clone https://github.com/yourusername/pandoc-converter
cd pandoc-converter
```

2. **安装字体**

macOS:
```bash
# 安装思源字体
brew install --cask font-noto-serif-cjk font-noto-sans-cjk

# 安装代码字体
brew install --cask font-source-code-pro
```

Ubuntu/Debian:
```bash
# 安装思源字体
sudo apt-get install fonts-noto-cjk fonts-noto-cjk-extra

# 安装代码字体
sudo apt-get install fonts-source-code-pro
```

Windows:
- 下载 [Noto Serif CJK SC](https://github.com/googlefonts/noto-cjk/releases) (思源宋体)
- 下载 [Noto Sans CJK SC](https://github.com/googlefonts/noto-cjk/releases) (思源黑体)
- 下载 [Source Code Pro](https://github.com/adobe-fonts/source-code-pro/releases)
- 双击字体文件安装

3. **创建虚拟环境**

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Linux/macOS:
source venv/bin/activate
# Windows:
.\venv\Scripts\activate
```

4. **安装 Python 依赖**

```bash
pip install -r requirements.txt
```

5. **安装系统依赖**

Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install pandoc texlive-full fonts-noto-cjk
```

macOS:
```bash
brew install pandoc
brew install --cask mactex
# macOS 默认已安装所需字体
```

Windows:
- 下载并安装 [Pandoc](https://pandoc.org/installing.html)
- 下载并安装 [MiKTeX](https://miktex.org/download)
- 安装宋体和黑体字体

## 使用方法

### 基本使用

1. **合并 HTML 文件并转换为 PDF**

```bash
# 使用 make 命令一键转换
make

# 默认会生成类似 go语言圣经-20240126.pdf 的输出文件
```

2. **直接使用 Python 脚本**

```bash
# 合并 HTML 文件
python scripts/merge.py --input data/input/book --output data/input/book/merged.html

# 转换为 PDF
python scripts/convert.py --config config/default.yaml data/input/book/merged.html data/output/document.pdf
```

### 使用不同配置

```bash
# 使用中文配置
make convert CONFIG=config/chinese.yaml

# 使用英文配置
make convert CONFIG=config/english.yaml
```

### 开启详细输出

```bash
python scripts/convert.py --verbose --config config/default.yaml input.html output.pdf
```

## 配置说明

### 配置文件结构

配置文件使用 YAML 格式，位于 `config/` 目录下：

```yaml
# 文档基本信息
document:
  title: "文档标题"
  author: "作者"
  date: \today
  lang: zh-CN

# PDF 输出设置
pdf:
  engine: xelatex
  template: templates/latex/main.tex

# 目录设置
toc:
  enabled: true
  depth: 3
```

### 自定义配置

1. **修改页面布局**

编辑 `templates/latex/includes/layout.tex`:
```tex
\geometry{
    top=2.5cm,
    bottom=2.5cm,
    left=2.5cm,
    right=2.5cm
}
```

2. **修改字体设置**

编辑 `templates/latex/includes/fonts.tex`:
```tex
\setCJKmainfont[BoldFont={SimHei}]{SimSun}
\setmainfont{Times New Roman}
```

### LaTeX 排版特性

- 支持自动代码高亮，包含多种编程语言
- 图片自动缩放至页面宽度的 90%
- 中英文混排字体智能处理：
  - 中文正文：宋体-简 (Songti SC)
  - 中文标题：苹方 (PingFang SC)
  - 英文正文：Times New Roman
  - 英文标题：Helvetica
  - 代码：Menlo
- 支持代码块自动换行
- 完整的超链接支持（包含目录、交叉引用）

## 项目结构

```
.
├── data/                      # 数据目录
│   ├── input/                 # 输入文件
│   └── output/               # 输出文件
├── templates/                 # 模板目录
│   └── latex/                # LaTeX 模板
├── config/                   # 配置目录
├── scripts/                  # 脚本目录
└── ...
```

## 常见问题解决

### 1. 字体问题

如果遇到字体相关错误，请确保已正确安装所需字体：

**检查字体是否安装成功**：
```bash
# macOS
fc-list | grep -i "songti"
fc-list | grep -i "pingfang"

# Linux
fc-list | grep -i "noto"

# Windows
dir C:\Windows\Fonts | findstr "SimSun"
dir C:\Windows\Fonts | findstr "SimHei"
```

**手动安装字体**：
- macOS 默认已安装所需字体
- Linux 用户安装 Noto CJK 字体
- Windows 用户确保安装宋体(SimSun)和黑体(SimHei)

### 2. PDF 引擎错误

确保已正确安装 XeLaTeX：

Ubuntu/Debian:
```bash
sudo apt-get install texlive-xetex
```

### 3. 模板不存在

检查模板路径是否正确，确保配置文件中的模板路径与实际路径一致。

## 开发指南

### 添加新功能

1. 在 `scripts/utils/` 中添加新的功能模块
2. 更新配置文件以支持新功能
3. 在主转换脚本中集成新功能

### 测试

运行单个测试：
```bash
python -m pytest tests/test_convert.py
```

## 贡献指南

1. Fork 项目
2. 创建功能分支：`git checkout -b feature/AmazingFeature`
3. 提交更改：`git commit -m 'Add some AmazingFeature'`
4. 推送分支：`git push origin feature/AmazingFeature`
5. 提交 Pull Request

## 版本历史

- 1.0.0
  - 初始发布
  - 基本转换功能
  - 中英文支持

## 许可证

该项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 作者

作者名称 - [@yourusername](https://github.com/yourusername)

## 致谢

- Pandoc 项目
- LaTeX 项目
- 所有贡献者

## 支持

如果您遇到任何问题，请：

1. 查看 [常见问题解决](#常见问题解决) 部分
2. 提交 [Issue](https://github.com/yourusername/pandoc-converter/issues)
3. 联系维护者