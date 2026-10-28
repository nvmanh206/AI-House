const assert = require('node:assert/strict');
const { test } = require('node:test');
const fs = require('node:fs');
const ts = require('typescript');
const React = require('react');
const { renderToStaticMarkup } = require('react-dom/server');

require.extensions['.tsx'] = (module, filename) => {
  const { outputText } = ts.transpileModule(fs.readFileSync(filename, 'utf8'), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, jsx: ts.JsxEmit.ReactJSX, esModuleInterop: true },
    fileName: filename,
  });
  module._compile(outputText, filename);
};

const { ChatAnswer } = require('../components/chat-answer.tsx');
const render = answer => renderToStaticMarkup(React.createElement(ChatAnswer, { answer }));

test('degraded answer is labeled as local data, not as missing knowledge', () => {
  const html = render({ message: 'Kỳ 2026-10 tiêu thụ 35 kWh.', metadata: { degraded: true, warnings: ['GEMINI_QUOTA'] } });
  assert.match(html, /dữ liệu nội bộ/);
  assert.match(html, /hết hạn mức/);
  assert.doesNotMatch(html, /Kho tri thức chưa có đủ căn cứ/);
});

test('timeout code explains slowness instead of quota', () => {
  const html = render({ message: 'x', metadata: { degraded: true, warnings: ['GEMINI_TIMEOUT'] } });
  assert.match(html, /phản hồi quá chậm/);
});

test('normal Gemini answer has no degraded label', () => {
  const html = render({ message: 'Câu trả lời.', metadata: { degraded: false, warnings: [] } });
  assert.doesNotMatch(html, /dữ liệu nội bộ/);
});

test('knowledge warnings still render alongside a degraded label', () => {
  const html = render({ message: 'x', metadata: { degraded: true, warnings: ['GEMINI_QUOTA', 'PRICE_SOURCE_STALE'] } });
  assert.match(html, /dữ liệu nội bộ/);
  assert.match(html, /chưa bảo đảm giá hiện hành/);
});
