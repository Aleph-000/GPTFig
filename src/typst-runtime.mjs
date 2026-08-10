import { $typst, TypstSnippet } from "@myriaddreamin/typst.ts/dist/esm/contrib/snippet.mjs";
import { MemoryAccessModel } from "@myriaddreamin/typst.ts/dist/esm/fs/memory.mjs";

const asset = (path) => new URL(path, import.meta.url).href;
const bytes = async (path) => new Uint8Array(await (await fetch(asset(path))).arrayBuffer());
const PACKAGE_FILES = [
  ["preview/cetz/0.5.2", "packages/cetz-0.5.2.tar.gz"],
  ["preview/cetz/0.3.4", "packages/cetz-0.3.4.tar.gz"],
  ["preview/cetz-plot/0.1.4", "packages/cetz-plot-0.1.4.tar.gz"],
  ["preview/cetz-venn/0.2.0", "packages/cetz-venn-0.2.0.tar.gz"],
  ["preview/fletcher/0.5.8", "packages/fletcher-0.5.8.tar.gz"],
  ["preview/simple-plot/1.0.0", "packages/simple-plot-1.0.0.tar.gz"],
  ["preview/oxifmt/1.0.0", "packages/oxifmt-1.0.0.tar.gz"],
  ["preview/oxifmt/0.2.1", "packages/oxifmt-0.2.1.tar.gz"]
];
const loadLocalFonts = (fonts) => {
  const loader = async (_, { builder }) => {
    for (const font of fonts) await builder.add_raw_font(font);
  };
  loader._kind = "fontLoader";
  loader._preloadRemoteFontOptions = { assets: false };
  return loader;
};

class LocalPackages {
  constructor(files, access) {
    this.files = files;
    this.access = access;
    this.cache = new Map();
  }

  resolve(spec, context) {
    const key = `${spec.namespace}/${spec.name}/${spec.version}`;
    if (this.cache.has(key)) return this.cache.get(key);

    const archive = this.files.get(key);
    if (!archive) return undefined;

    const root = `/@memory/packages/${key}`;
    context.untar(archive, (path, data, mtime) => {
      this.access.insertFile(`${root}/${path}`, data, new Date(mtime));
    });
    this.cache.set(key, root);
    return root;
  }
}

$typst.setRendererInitOptions({ getModule: () => asset("renderer.wasm") });

const ready = Promise.all([
  ...PACKAGE_FILES.map(([, path]) => bytes(path)),
  bytes("../fonts/NewCM10-Regular.otf"),
  bytes("../fonts/NewCMMath-Regular.otf"),
  bytes("../fonts/NotoSansCJKsc-Regular.otf")
]).then((resources) => {
  const access = new MemoryAccessModel();
  const packages = new Map(
    PACKAGE_FILES.map(([key], index) => [key, resources[index]])
  );
  const fonts = resources.slice(PACKAGE_FILES.length);

  $typst.use(
    TypstSnippet.withAccessModel(access),
    TypstSnippet.withPackageRegistry(new LocalPackages(packages, access))
  );
  $typst.setCompilerInitOptions({
    getModule: () => asset("compiler.wasm"),
    beforeBuild: [loadLocalFonts(fonts)]
  });
});

const PREAMBLE = `
#set page(width: auto, height: auto, margin: 10pt, fill: white)
`;

export async function renderTypst(source) {
  await ready;
  let vector;
  try {
    vector = await $typst.vector({ mainContent: PREAMBLE + source });
  } catch (error) {
    throw new Error(`Typst compile failed: ${error?.stack || error}`);
  }
  try {
    return await $typst.svg({ vectorData: vector });
  } catch (error) {
    throw new Error(`Typst render failed: ${error?.stack || error}`);
  }
}
