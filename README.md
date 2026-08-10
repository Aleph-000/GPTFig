# GPTFig

把 ChatGPT 回答中首个非空行为 `# @plot` 的代码块原地替换成 Matplotlib 静态图。Python、NumPy、Matplotlib 和 Noto Sans CJK SC 都从扩展目录加载，在浏览器本地执行；扩展不申请任何权限，也不向外部服务发送代码。

## 安装

1. 打开 `edge://extensions` 或 `chrome://extensions`。
2. 开启“开发人员模式”。
3. 选择“加载解压缩的扩展”，然后选中本文件夹。
4. 刷新 ChatGPT 页面。

## 用法

让 ChatGPT 输出如下 Python 代码块：

```python
# @plot
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(-3, 3, 500)

plt.figure()
plt.plot(x, x**2)

plt.figure()
plt.plot(x, x**3)

plt.show()
```

只有带标记的代码块会执行；检测到标记后会在代码流式生成期间预热，成功后整个代码框（含语言栏和复制按钮）消失，每个 figure 按顺序显示为一张 PNG。

中文字体和负号显示已全局配置，无需在代码块里重复设置 `font.sans-serif`。普通图片自动适应消息宽度，超宽表格图片会限制在容器内并支持横向滚动。字体来自 Noto CJK Sans `Sans2.004`，使用 `vendor/fonts/OFL.txt` 中的 SIL Open Font License 1.1。

## 安全说明

GPTFig 只自动执行带 `# @plot` 标记的代码块，但这些代码仍是完整的 Python。请只在你信任的对话中使用，并留意高计算量代码可能占用较多浏览器内存。

## 许可证

第三方组件及其许可证见 `THIRD_PARTY_NOTICES.md`。GPTFig 项目源代码目前未声明开源许可证。
