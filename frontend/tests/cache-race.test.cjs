const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const ts = require('typescript');
for (const extension of ['.tsx', '.ts']) {
  require.extensions[extension] = (module, filename) => module._compile(
    ts.transpileModule(fs.readFileSync(filename, 'utf8'), {
      compilerOptions: { module: ts.ModuleKind.CommonJS, jsx: ts.JsxEmit.ReactJSX, esModuleInterop: true },
      fileName: filename,
    }).outputText, filename);
}
const { prefetchEndpoints, invalidateCache } = require('../components/application.tsx');
const settle = () => new Promise(resolve => setImmediate(resolve));

test('response started before invalidation cannot repopulate the cache', async () => {
  const originalFetch = global.fetch;
  const requests = [];
  global.fetch = () => new Promise(resolve => requests.push(resolve));
  try {
    invalidateCache();
    prefetchEndpoints(['/cache-race-regression']);
    assert.equal(requests.length, 1);
    invalidateCache();
    requests[0]({ok: true, status: 200, json: async () => ({household: 'old'})});
    await settle();
    prefetchEndpoints(['/cache-race-regression']);
    assert.equal(requests.length, 2, 'old response must not suppress the new household request');
    requests[1]({ok: true, status: 200, json: async () => ({household: 'new'})});
    await settle();
    prefetchEndpoints(['/cache-race-regression']);
    assert.equal(requests.length, 2, 'a current fresh response should still be cached');
  } finally {
    invalidateCache();
    global.fetch = originalFetch;
  }
});
