import { copyFile, mkdir, readFile } from "node:fs/promises";
import { build } from "esbuild";

const cspSafeTypst = {
  name: "csp-safe-typst",
  setup(context) {
    // wasm-bindgen emits a few constant Function constructors, which MV3 blocks.
    context.onLoad({ filter: /@myriaddreamin[\\/].*\.mjs$/ }, async ({ path }) => {
      let contents = await readFile(path, "utf8");
      const original = contents;
      contents = contents
        .replaceAll(
          "new Function('m', 'return import(m)')",
          "((m) => import(m))"
        )
        .replaceAll(
          'new Function("m", "return import(m)")',
          "((m) => import(m))"
        )
        .replaceAll(
          "const ret = new Function(getStringFromWasm0(arg0, arg1));",
          "const source = getStringFromWasm0(arg0, arg1);\n        let ret;\n        if (source === 'return 0') ret = () => 0;\n        else if (source === 'return true') ret = () => true;\n        else if (source === 'return this') ret = function () { return this; };\n        else if (source === \"throw new Error('Dummy AccessModel, please initialize compiler with withAccessModel()')\") ret = () => { throw new Error('Dummy AccessModel, please initialize compiler with withAccessModel()'); };\n        else if (source === \"throw new Error('Dummy Registry, please initialize compiler with withPackageRegistry()')\") ret = () => { throw new Error('Dummy Registry, please initialize compiler with withPackageRegistry()'); };\n        else throw new Error('Blocked dynamic function: ' + source);"
        )
        .replaceAll(
          "const ret = new Function(getStringFromWasm0(arg0, arg1), getStringFromWasm0(arg2, arg3));",
          "const args = getStringFromWasm0(arg0, arg1);\n        const source = getStringFromWasm0(arg2, arg3);\n        let ret;\n        if (args === 'path' && source === 'return path') ret = path => path;\n        else if (source === \"throw new Error('Dummy AccessModel, please initialize compiler with withAccessModel()')\") ret = () => { throw new Error('Dummy AccessModel, please initialize compiler with withAccessModel()'); };\n        else if (source === \"throw new Error('Dummy Registry, please initialize compiler with withPackageRegistry()')\") ret = () => { throw new Error('Dummy Registry, please initialize compiler with withPackageRegistry()'); };\n        else throw new Error('Blocked dynamic function (' + args + '): ' + source);"
        );
      if (contents !== original) return { contents, loader: "js" };
    });
  }
};

const output = new URL("./vendor/typst/", import.meta.url);
await mkdir(output, { recursive: true });

await Promise.all([
  copyFile(
    new URL("./node_modules/@myriaddreamin/typst-ts-web-compiler/pkg/typst_ts_web_compiler_bg.wasm", import.meta.url),
    new URL("compiler.wasm", output)
  ),
  copyFile(
    new URL("./node_modules/@myriaddreamin/typst-ts-renderer/pkg/typst_ts_renderer_bg.wasm", import.meta.url),
    new URL("renderer.wasm", output)
  ),
  copyFile(
    new URL("./node_modules/@myriaddreamin/typst.ts/LICENSE", import.meta.url),
    new URL("LICENSE-typst-ts.txt", output)
  )
]);

await build({
  entryPoints: ["src/typst-runtime.mjs"],
  bundle: true,
  format: "esm",
  platform: "browser",
  target: "chrome120",
  minify: true,
  plugins: [cspSafeTypst],
  outfile: "vendor/typst/runtime.mjs"
});

const runtime = await readFile(new URL("runtime.mjs", output), "utf8");
if (/new Function|\beval\s*\(/.test(runtime)) throw new Error("Typst bundle violates the MV3 CSP");
