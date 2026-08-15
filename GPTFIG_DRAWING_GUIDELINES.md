# GPTFig 绘图规范

用户做了一个将 Typst + CeTZ 代码块实时渲染成图片的脚本，以后说插图等就是如下的意思。

用户希望以后回答中，只要插图能明显帮助直观理解、比较、展示结构或变化过程，就在对应正文位置插入 Typst + CeTZ 代码块，不集中放在开头或结尾。固定使用用户脚本支持的形式，让图原地渲染为静态图。

图可用于函数/参数曲线、几何示意图、向量场、概率分布、数据图表、算法过程、网络/树/图结构、物理轨迹、金融时间序列、热力图、散点图、直方图等。

对于 `xj`、`js`、`jj` 回答尤其优先采用“解释 → 图 → 继续解释”的结构。不要为了有图而强行加图；只有图能提升理解或展示效果时才加入。

不要解释插件或提示用户运行代码，直接插入代码块等待浏览器渲染。上下文如果必要的话可以解释插图，但是不要解释插图的代码，正常进行上下文，就像插图自然而然作为文章的附图一样。

生成插图时直接输出 Typst + CeTZ 代码，不要检查系统是否安装 Typst，不要调用或安装 Typst CLI， 不要下载 Typst 原生二进制文件；实际编译和渲染全部交给 GPTFig。

## 代码块格式

绘图代码必须放在 `typst` 代码块中，首个非空行严格为 `// @plot`，开头严格导入如下五个绘图库：

```typst
// @plot
#import "@preview/cetz:0.5.2"
#import "@preview/cetz-plot:0.1.4"
#import "@preview/simple-plot:1.0.0"
#import "@preview/fletcher:0.5.8"
#import "@preview/cetz-venn:0.2.0"

#cetz.canvas({
  import cetz.draw: *
  // 绘图代码
})
```

对应包的函数/API 文档：

- [CeTZ 函数 API](https://cetz-package.github.io/docs/api/overview/)
- [CeTZ-Plot 函数手册](https://github.com/cetz-package/cetz-plot/blob/master/manual.pdf)
- [Simple-Plot 函数与参数](https://typst.app/universe/package/simple-plot/)
- [Fletcher 函数手册](https://github.com/Jollywatt/typst-fletcher/blob/main/docs/manual.pdf)
- [CeTZ-Venn 函数手册](https://github.com/cetz-package/cetz-venn/blob/stable/manual.pdf)

## 规则

- 函数图优先使用 `@preview/simple-plot:1.0.0`；复杂坐标图和统计图使用 `@preview/cetz-plot:0.1.4`，不要手写少量折线点近似曲线。
- 每次插图之前先查阅 [CeTZ 官方文档](https://cetz-package.github.io/docs/)和上方对应绘图库的函数/API 文档，看 API、函数怎么使用。
- 图内公式使用 Typst 数学语法 `$...$`，不要使用 LaTeX 命令。
- 数学模式中的英文单词、缩写和特殊文本一律用双引号包裹，如 `$"VWAP" = 0.331$`、`$"mid" = ("bid" + "ask") / 2$`、`$"Buy@0.43"$`；只有单字母变量可以不加引号。
- `content()` 中的普通文字必须用 `[...]` 包裹，例如 `content((0, 0), [说明文字])`；数学公式使用 `$...$`，例如 `content((0, 0), $x^2$)`，禁止直接传入未包裹的中文文字。
- `pt` 不是禁用单位：仅在 API 参数类型允许 `length` 时使用，如线宽 `stroke: 0.8pt`、字号和内边距；若参数要求 `number`、`ratio`、数组或字典，则按文档类型传值，不能附加 `pt`。
- CeTZ 几何尺寸通常使用画布坐标单位：[`circle.radius`](https://cetz-package.github.io/docs/api/draw-functions/shapes/circle/) 使用数字或二元数组，如 `radius: 0.07`、`radius: (2, 1)`；[`rect.radius`](https://cetz-package.github.io/docs/api/draw-functions/shapes/rect/) 使用数字、百分比或字典，如 `radius: 0.1`、`radius: 5%`。其他函数必须查对应 API，不能根据参数名猜测单位。
- Typst 数学双向箭头使用 `arrow.l.r`，不要写 `arrows.quad`。
- 可以直接使用中文；避免 Emoji 和罕见字符。图中非必要不写中文解释，只保留数学符号和点名。
- 默认采用简洁教材风格：标签不重叠，主体用实线，辅助线用虚线，颜色用于突出重点，如果利于展示则标出点的字母。可以用彩色，让视觉风格简洁美观。
- 尽量不用灰色；如果要画虚线，画成 `dashed` 的样子。
- 控制图形尺寸和采样数量；复杂内容拆成多张图，分别放在对应正文位置。
- 函数与几何坐标必须按公式计算，注意计算一定要正确精确！！！一些复杂的计算如切线等可能出错需要额外注意。
- 保持横纵坐标比例正确。
- Typst 赋值时禁止在 `=` 后直接换行。多行计算必须写成 `let x = (...)`，用括号包住完整表达式；简单计算保持单行。每个 `// @plot` 代码块必须独立检查语法。
- 如果涉及到具体长度、坐标轴、原点等，则将坐标轴画出，使用 `cetz-plot.plot.plot()` 画坐标轴。
- 使用 `import cetz.draw: *` 后，禁止写 `stroke: stroke(...)`；虚线统一写成 `stroke: (paint: color, thickness: 0.8pt, dash: "dashed")`。
- 如果需要坐标轴，使用穿过原点的十字坐标轴，有正向实心箭头和标签，不要边框、刻度、数字或网格。坐标轴按图中全部图形的实际边界自动取值覆盖最值，只保留少量留白，并保持横纵坐标等比例。
- 曲线、圆和椭圆等禁止用少量线段近似，必须使用API、函数画图。如果是函数图必须显示十字坐标轴。
- 涉及多个点时，如多个点共线或某个点为交点，应完整连接所有相关点，不能遗漏或留下孤立点。
- 箭头必须带箭头标记，不能用普通线代替。
