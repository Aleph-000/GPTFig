# GPTFig

[中文](#中文) · [English](#english)

## 中文

GPTFig 是一个 Chrome/Edge 扩展，把 ChatGPT 回答中以 `// @plot` 开头的 Typst + CeTZ 代码块原地渲染成静态 SVG。编译器、绘图库、字体和依赖均随扩展提供，在浏览器本地运行。

### 安装

1. 打开 `edge://extensions` 或 `chrome://extensions`。
2. 开启“开发人员模式”。
3. 选择“加载解压缩的扩展”，选中本项目文件夹。
4. 刷新 ChatGPT 页面。

### 使用

让 ChatGPT 输出以下形式的 `typst` 代码块：

```typst
// @plot
#import "@preview/cetz:0.5.2"

#cetz.canvas({
  import cetz.draw: *
  line((-2, 0), (2, 0), mark: (end: ">"))
  line((0, -1), (0, 3), mark: (end: ">"))
  circle((0, 1), radius: (1.5, 0.8), stroke: blue)
  content((0, 1), [椭圆])
})
```

只有首个非空行为 `// @plot` 的代码块会渲染。成功后代码框被居中的白底 SVG 替换；失败时保留原代码块。可把 [GPTFig 绘图规范](GPTFIG_DRAWING_GUIDELINES.md) 交给 ChatGPT，并让它保存为长期记忆。

### 内置组件

Typst 0.14.2、CeTZ 0.5.2、CeTZ-Plot 0.1.4、Simple-Plot 1.0.0、Fletcher 0.5.8、CeTZ-Venn 0.2.0，以及中英文字体和固定版本依赖。全部离线加载。

### 构建

仓库已包含可直接加载的构建产物。修改源码或升级依赖后运行：

```text
npm install
npm run build
```

### 安全与许可

扩展不申请额外权限，也不会把绘图代码发送给外部服务。只渲染你信任的内容。第三方许可见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。项目源代码目前未声明开源许可证。

## English

GPTFig is a Chrome/Edge extension that replaces ChatGPT `// @plot` Typst + CeTZ code blocks with inline static SVG images. The compiler, drawing packages, fonts, and dependencies are bundled and run locally in the browser.

### Installation

1. Open `edge://extensions` or `chrome://extensions`.
2. Enable **Developer mode**.
3. Choose **Load unpacked** and select this project folder.
4. Refresh the ChatGPT page.

### Usage

Ask ChatGPT to output a `typst` code block in this form:

```typst
// @plot
#import "@preview/cetz:0.5.2"

#cetz.canvas({
  import cetz.draw: *
  line((-2, 0), (2, 0), mark: (end: ">"))
  line((0, -1), (0, 3), mark: (end: ">"))
  circle((0, 1), radius: (1.5, 0.8), stroke: blue)
  content((0, 1), [Ellipse])
})
```

Only code blocks whose first non-empty line is `// @plot` are rendered. On success, the code block is replaced by a centered SVG with a white background; on failure, the original code remains. You can give the [GPTFig drawing guidelines](GPTFIG_DRAWING_GUIDELINES.md) to ChatGPT and ask it to save the instructions to memory.

### Bundled components

Typst 0.14.2, CeTZ 0.5.2, CeTZ-Plot 0.1.4, Simple-Plot 1.0.0, Fletcher 0.5.8, CeTZ-Venn 0.2.0, Chinese/Latin fonts, and pinned dependencies. Everything is loaded offline.

### Build

Ready-to-load build artifacts are included. After changing the source or dependencies, run:

```text
npm install
npm run build
```

### Security and licenses

The extension requests no extra permissions and does not send plot code to external services. Render only content you trust. Third-party notices are in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). The project source currently has no declared open-source license.
