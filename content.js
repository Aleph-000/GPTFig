const MARKER = "// @plot";
const pending = new Map();
const seen = new WeakMap();
const warmed = new WeakSet();

function imageSvg(source) {
  const parsed = new DOMParser().parseFromString(source, "text/html");
  const svg = parsed.querySelector("svg");
  if (!svg) throw new Error("Typst did not return an SVG");
  svg.querySelectorAll("script").forEach((node) => node.remove());
  svg.querySelectorAll("*").forEach((node) => {
    for (const attribute of [...node.attributes]) {
      if (/^on/i.test(attribute.name)) node.removeAttribute(attribute.name);
      if (/^(?:href|xlink:href)$/i.test(attribute.name) && !attribute.value.startsWith("#")) {
        node.removeAttribute(attribute.name);
      }
    }
  });
  return new XMLSerializer().serializeToString(svg);
}

function prewarm(code) {
  if (warmed.has(code)) return;
  const first = code.textContent
    .replace(/\r\n?/g, "\n")
    .split("\n")
    .find((line) => line.trim() !== "");
  if (first?.trim() !== MARKER) return;

  warmed.add(code);
  chrome.runtime.sendMessage({ type: "warmup" }).catch(() => warmed.delete(code));
}

function schedule(code) {
  if (!code) return;
  const pre = code.closest("pre");
  if (!pre || pre.querySelector("code") !== code) return;

  prewarm(code);
  clearTimeout(pending.get(code));
  pending.set(code, setTimeout(() => render(pre, code), 800));
}

function frameFor(pre) {
  const boundary = "article,[data-message-id],[data-message-author-role],[role='main']";
  const prose = "p,h1,h2,h3,h4,h5,h6,ul,ol,li,table,blockquote";
  const codeLength = pre.textContent.replace(/\s+/g, " ").trim().length;
  let best = pre;

  for (let frame = pre.parentElement; frame && !frame.matches(boundary); frame = frame.parentElement) {
    if (frame.querySelectorAll("pre").length !== 1) break;
    if ([...frame.querySelectorAll(prose)].some((node) => !pre.contains(node))) break;
    if (frame.textContent.replace(/\s+/g, " ").trim().length - codeLength > 200) break;
    best = frame;
  }
  return best;
}

async function render(pre, code) {
  pending.delete(code);

  const source = code.textContent.replace(/\r\n?/g, "\n");
  const lines = source.split("\n");
  const marker = lines.findIndex((line) => line.trim() !== "");
  if (marker < 0 || lines[marker].trim() !== MARKER || seen.get(code) === source) return;

  seen.set(code, source);
  try {
    const result = await chrome.runtime.sendMessage({
      type: "render-typst",
      code: lines.slice(marker + 1).join("\n")
    });
    if (!result?.ok || !result.svg) throw new Error(result?.error);
    if (!pre.isConnected || code.textContent.replace(/\r\n?/g, "\n") !== source) return;

    const output = document.createElement("div");
    output.className = "gptfig-inline-plot";
    const image = document.createElement("img");
    image.src = `data:image/svg+xml;charset=utf-8,${encodeURIComponent(imageSvg(result.svg))}`;
    image.alt = "Typst diagram";
    output.append(image);
    frameFor(pre).replaceWith(output);
  } catch (error) {
    console.error("GPTFig:", error);
  }
}

function scan(root) {
  if (root.nodeType === Node.TEXT_NODE) return schedule(root.parentElement?.closest("code"));
  if (!(root instanceof Element)) return;
  if (root.matches("code")) schedule(root);
  root.querySelectorAll("code").forEach(schedule);
}

new MutationObserver((mutations) => {
  for (const mutation of mutations) {
    if (mutation.type === "characterData") scan(mutation.target);
    else mutation.addedNodes.forEach(scan);
  }
}).observe(document, { subtree: true, childList: true, characterData: true });

scan(document.documentElement);
