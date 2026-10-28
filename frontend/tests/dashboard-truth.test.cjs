const assert = require('node:assert/strict');
const { test } = require('node:test');
const fs = require('node:fs');
const ts = require('typescript');
const React = require('react');
const { renderToStaticMarkup } = require('react-dom/server');

// Reuse the installed TypeScript compiler and React renderer.
require.extensions['.tsx'] = (module, filename) => {
  const { outputText } = ts.transpileModule(fs.readFileSync(filename, 'utf8'), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, jsx: ts.JsxEmit.ReactJSX, esModuleInterop: true },
    fileName: filename,
  });
  module._compile(outputText, filename);
};

const { AIInsightPanel } = require('../components/dashboard/AIInsightPanel.tsx');
const { CostBreakdown } = require('../components/dashboard/CostBreakdown.tsx');
const { NotificationPanel } = require('../components/dashboard/NotificationPanel.tsx');
const { AppLayout } = require('../components/layout/AppLayout.tsx');
const { ExpenseTrendChart } = require('../components/dashboard/ExpenseTrendChart.tsx');
const { BillAnalysisCard } = require('../components/bill-analysis-card.tsx');

test('OCR unknown does not blame an unreadable image when a reading was extracted', () => {
  const html = renderToStaticMarkup(React.createElement(BillAnalysisCard, {result: {
    status: 'success', bill: {type: 'electricity', current_reading: 150},
    meter_verification: {status: 'UNKNOWN', ocr_reading: 150, database_reading: null, difference: null, unit: 'kWh'},
  }}));
  assert.match(html, /150 kWh/);
  assert.match(html, /tài khoản.*kỳ hóa đơn/);
  assert.doesNotMatch(html, /Không đọc được chỉ số công tơ hiện tại từ ảnh/);
  assert.doesNotMatch(html, /✓ Trùng chỉ số/);
});

test('consumption filters are not labelled as money', () => {
  const html = renderToStaticMarkup(React.createElement(ExpenseTrendChart, {series: []}));
  assert.match(html, /Lượng điện/);
  assert.match(html, /Lượng nước/);
});

test('layout does not show a fabricated fixed calendar date', () => {
  const html = renderToStaticMarkup(React.createElement(AppLayout, {screen: 'dashboard', user: {}, notifications: [], unreadCount: 0, onLogout() {}, children: null}));
  assert.doesNotMatch(html, /20 tháng 9, 2026/);
});

test('empty notifications do not invent bills or amounts', () => {
  const html = renderToStaticMarkup(React.createElement(NotificationPanel, {notifications: []}));
  assert.match(html, /Chưa có thông báo/);
  assert.doesNotMatch(html, /673\.200|300 kWh|2 giờ trước/);
});

test('cost breakdown explicitly distinguishes missing water from zero', () => {
  const html = renderToStaticMarkup(React.createElement(CostBreakdown, {elecCost: 0, waterCost: null, period: '2026-01'}));
  assert.match(html, /Chưa có tiền nước/);
  assert.match(html, /2026-01/);
  assert.doesNotMatch(html, /tháng này/);
});

test('both real zero bills are labelled as zero, not missing', () => {
  const html = renderToStaticMarkup(React.createElement(CostBreakdown, {elecCost: 0, waterCost: 0}));
  assert.match(html, /Chi phí đã ghi nhận bằng 0/);
});

test('guidance does not invent household trends, savings or peer comparisons', () => {
  const html = renderToStaticMarkup(React.createElement(AIInsightPanel));
  assert.doesNotMatch(html, /8\.2%|80\.000|120\.000|12%|hộ gia đình tương tự/);
});

test('general advice is labelled and links to the assistant', () => {
  const html = renderToStaticMarkup(React.createElement(AIInsightPanel));
  assert.match(html, /Gợi ý chung/);
  assert.match(html, /chưa phải phân tích dữ liệu của hộ/i);
  assert.match(html, /href="\/assistant"/);
});
