# GPTFig

把 ChatGPT 回答中以 `// @plot` 开头的代码块原地替换成 Typst + CeTZ 静态 SVG。编译器、绘图库、依赖和中英文字体都随扩展提供，在浏览器本地运行；扩展不申请额外权限，也不会把代码发送到外部服务。

## 安装

1. 打开 `edge://extensions` 或 `chrome://extensions`。
2. 开启“开发人员模式”。
3. 选择“加载解压缩的扩展”，然后选中本文件夹。
4. 刷新 ChatGPT 页面。

首次渲染需要加载约几十 MB 的本地编译器和字体，之后同一浏览器会话内会明显更快。

## 用法

让 ChatGPT 输出如下 Typst 代码块：

```typst
// @plot
#import "@preview/cetz:0.5.2"

#cetz.canvas({
  import cetz.draw: *

  line((-2, 0), (2, 0), mark: (end: ">"))
  line((0, -1), (0, 3), mark: (end: ">"))
  circle((0, 1), radius: (1.5, 0.8), stroke: blue)
  content((0, 1), [共轭椭圆 $x^2 / a^2 + y^2 / b^2 = 1$])
})
```

只有首个非空行为 `// @plot` 的代码块会渲染。成功后整个代码框会被对应 SVG 图片替换，页面排版保持“文字 → 图 → 文字”。渲染失败时保留原代码块，并在浏览器控制台输出错误。

当前内置 Typst 0.14.2，以及以下完整离线绘图套件：

- CeTZ 0.5.2：基础矢量绘图、几何、坐标和变换。
- CeTZ-Plot 0.1.4：函数曲线、坐标轴、数据图和统计图。
- Simple-Plot 1.0.0：更简洁的数学函数图、参数曲线和面积图 API。
- Fletcher 0.5.8：流程图、网络图、状态图和交换图。
- CeTZ-Venn 0.2.0：二集合和三集合 Venn 图。

这些包的固定版本依赖也已一并内置；所有代码、包和字体都从扩展目录加载，不需要联网。

椭圆应使用 CeTZ 原生 `circle(center, radius: (rx, ry))`，不要用少量采样点和折线近似。函数曲线应按解析式计算，并保持坐标轴比例正确。

## 构建

仓库已经包含可直接加载的构建产物。修改 `src/typst-runtime.mjs` 或升级依赖后再运行：

```text
npm install
npm run build
```

构建脚本会把固定版本的 Typst WASM 和运行时代码写入 `vendor/typst/`。CeTZ 绘图套件、依赖和字体作为离线资源保留在仓库中。

## 安全说明

Typst 比执行任意 Python 更受限制，但复杂或恶意输入仍可能长时间占用 CPU 和内存。只渲染你信任的对话内容；扩展不会读取网络包或执行 `shell-escape`。

## 许可证

第三方组件及其许可证见 `THIRD_PARTY_NOTICES.md`。GPTFig 项目源代码目前未声明开源许可证。
