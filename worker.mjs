import { renderTypst } from "./vendor/typst/runtime.mjs";

let queue = Promise.resolve();
let warmup;

function enqueue(code) {
  const job = queue.then(() => renderTypst(code));
  queue = job.catch(() => {});
  return job;
}

chrome.runtime.onMessage.addListener((message, _sender, respond) => {
  if (message?.type === "warmup") {
    warmup ||= enqueue("[]");
    warmup.then(
      () => respond({ ok: true }),
      (error) => respond({ ok: false, error: String(error?.message || error) })
    );
    return true;
  }
  if (message?.type !== "render-typst" || typeof message.code !== "string") return;

  const job = enqueue(message.code);
  job.then(
    (svg) => respond({ ok: true, svg }),
    (error) => respond({ ok: false, error: String(error?.message || error) })
  );
  return true;
});
