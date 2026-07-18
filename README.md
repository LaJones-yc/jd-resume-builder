# JD Resume Builder

[English](#english) · [中文](#中文)

## English

`jd-resume-builder` is a reusable Codex Skill for creating truthful, evidence-backed, JD-tailored Chinese and English one-page resumes.

### What it does

- Maintains a user-controlled experience library outside the Skill directory.
- Extracts verified resume evidence from existing resumes, PDFs, reports, presentations, repositories, and user statements.
- Maps experience to a job description without inventing responsibilities, tools, metrics, or outcomes.
- Adds supported JD keywords naturally for ATS and AI screening.
- Produces structurally aligned Chinese and English Markdown resumes.
- Renders readable one-page A4 PDFs with adaptive typography and visual review.

### Typical workflow

1. Choose where to store the experience library and resume outputs.
2. Provide existing resumes or supporting project materials.
3. Confirm ownership, dates, methods, metrics, and uncertain facts.
4. Provide the target job description.
5. Review the proposed experience selection and keyword coverage.
6. Generate, validate, render, visually inspect, and revise both language versions.

### Installation

Place this repository at:

```text
$CODEX_HOME/skills/jd-resume-builder
```

Restart Codex or begin a new task, then invoke it with a prompt such as:

```text
Use $jd-resume-builder to maintain my experience library and tailor a bilingual one-page resume to this JD.
```

### Requirements

- Python 3.11+
- `reportlab`, `pypdf`, and `pdfplumber`
- Poppler for PDF-to-image visual verification
- An embeddable CJK font for Chinese output, such as Microsoft YaHei, PingFang, or Noto CJK

### Privacy and truthfulness

Keep personal source documents, experience libraries, portraits, JDs, and generated resumes outside the installed Skill directory. The Skill treats verified evidence as the source of truth and must never fabricate experience.

---

## 中文

`jd-resume-builder` 是一个可复用的 Codex Skill，用于生成真实、基于证据、针对 JD 优化且中英文对应的一页简历。

### 核心能力

- 在 Skill 目录之外维护由用户控制的动态经历库。
- 从既有简历、PDF、报告、PPT、代码仓库和用户陈述中提取可验证信息。
- 根据 JD 匹配经历，但不编造职责、工具、指标或成果。
- 为 ATS 和 AI 筛选自然加入有事实支持的 JD 关键词。
- 生成结构、日期、数字和事实相互对应的中英文 Markdown 简历。
- 使用自适应字号生成可读的一页 A4 PDF，并进行视觉复查和迭代。

### 典型流程

1. 选择经历库和简历输出的保存位置。
2. 提供既有简历或项目证明材料。
3. 确认个人贡献、日期、方法、指标和不确定事实。
4. 提供目标岗位 JD。
5. 检查经历选择方案和关键词覆盖情况。
6. 生成、校验、渲染、视觉复查并同步修改中英文版本。

### 安装方式

将本仓库放置到：

```text
$CODEX_HOME/skills/jd-resume-builder
```

重启 Codex 或开始一个新任务，然后使用类似提示词调用：

```text
使用 $jd-resume-builder 维护我的经历库，并根据这份 JD 生成中英文一页简历。
```

### 环境要求

- Python 3.11+
- `reportlab`、`pypdf` 和 `pdfplumber`
- 用于 PDF 图片化复查的 Poppler
- 可嵌入的中文字体，例如微软雅黑、苹方或 Noto CJK

### 隐私与真实性

个人源文件、经历库、头像、JD 和生成的简历应保存在已安装 Skill 目录之外。Skill 必须以经过验证的证据为事实来源，任何情况下都不得编造经历。
