import createPyodideModule from "./vendor/pyodide/pyodide.asm.mjs";
import { loadPyodide } from "./vendor/pyodide/pyodide.mjs";

const runtimeURL = new URL("./vendor/pyodide/", import.meta.url);
const indexURL = runtimeURL.protocol === "file:"
  ? decodeURIComponent(runtimeURL.pathname.slice(1))
  : runtimeURL.href;
const geometerResource = new URL(
  "./vendor/pyodide/geometer-0.4.2-py3-none-any.whl",
  import.meta.url
);
const geometerURL = geometerResource.protocol === "file:"
  ? decodeURIComponent(geometerResource.pathname.slice(1))
  : geometerResource.href;
const fontReady = fetch(new URL("./vendor/fonts/NotoSansCJKsc-Regular.otf", import.meta.url))
  .then((response) => {
    if (!response.ok) throw new Error("Failed to load Noto Sans CJK SC");
    return response.arrayBuffer();
  });

const SETUP = `
import base64, io, json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager, rcParams

FONT_PATH = "/fonts/NotoSansCJKsc-Regular.otf"
font_manager.fontManager.addfont(FONT_PATH)
CJK_FONT = font_manager.FontProperties(fname=FONT_PATH).get_name()

plt.show = lambda *args, **kwargs: None

def _render_plot(source):
    plt.close("all")
    try:
        rcParams["font.family"] = "sans-serif"
        rcParams["font.sans-serif"] = [CJK_FONT, "DejaVu Sans"]
        rcParams["axes.unicode_minus"] = False
        rcParams["text.usetex"] = False
        rcParams["mathtext.fontset"] = "stix"
        rcParams["mathtext.default"] = "it"
        exec(compile(source, "<inline-plot>", "exec"), {"__name__": "__main__"})
        images = []
        for number in plt.get_fignums():
            buffer = io.BytesIO()
            figure = plt.figure(number)
            width, height = figure.get_size_inches()
            dpi = min(120, 2400 / max(width, 1), 2400 / max(height, 1))
            figure.savefig(buffer, format="png", dpi=dpi)
            images.append(base64.b64encode(buffer.getvalue()).decode("ascii"))
        if not images:
            raise RuntimeError("No Matplotlib figure was created")
        return json.dumps(images)
    finally:
        plt.close("all")
`;

const ready = loadPyodide({
  indexURL,
  createPyodideModule,
  packages: ["matplotlib", "typing-extensions"]
});

const renderer = Promise.all([ready, fontReady]).then(async ([pyodide, font]) => {
  await pyodide.loadPackage(geometerURL);
  pyodide.FS.mkdirTree("/fonts");
  pyodide.FS.writeFile("/fonts/NotoSansCJKsc-Regular.otf", new Uint8Array(font));
  await pyodide.runPythonAsync(SETUP);
  return pyodide.globals.get("_render_plot");
});

let queue = Promise.resolve();

export async function render(code) {
  return JSON.parse((await renderer)(code));
}

chrome.runtime.onMessage.addListener((message, _sender, respond) => {
  if (message?.type === "warmup") {
    renderer.then(
      () => respond({ ok: true }),
      (error) => respond({ ok: false, error: String(error?.message || error) })
    );
    return true;
  }
  if (message?.type !== "render-plot" || typeof message.code !== "string") return;

  const job = queue.then(() => render(message.code));
  queue = job.catch(() => {});
  job.then(
    (images) => respond({ ok: true, images }),
    (error) => respond({ ok: false, error: String(error?.message || error) })
  );
  return true;
});
