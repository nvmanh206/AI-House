const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const ts = require('typescript');
require.extensions['.ts'] = (module, filename) => {
  module._compile(ts.transpileModule(fs.readFileSync(filename, 'utf8'), {
    compilerOptions: { module: ts.ModuleKind.CommonJS }, fileName: filename,
  }).outputText, filename);
};
const { dashboardSummary } = require('../components/dashboard/dashboard-data.ts');

test('empty data is unknown, not zero or the current calendar month', () => {
  assert.deepEqual(dashboardSummary([]), { period: null, electricityUsage: null,
    waterUsage: null, electricityCost: null, waterCost: null, totalCost: null });
});
test('real zeros survive and missing water remains unknown', () => {
  const result = dashboardSummary([{ period: '2026-01', ELECTRICITY: 0, WATER: null,
    ELECTRICITY_COST: 0, WATER_COST: null, cost: 0 }]);
  assert.equal(result.electricityCost, 0);
  assert.equal(result.electricityUsage, 0);
  assert.equal(result.waterCost, null);
  assert.equal(result.waterUsage, null);
});
test('latest recorded period uses server aggregate, not a single account bill', () => {
  const result = dashboardSummary([
    { period: '2026-02', ELECTRICITY_COST: 300.3, WATER_COST: 0, cost: 300.3 },
    { period: '2026-01', ELECTRICITY_COST: 50, cost: 50 },
  ]);
  assert.equal(result.period, '2026-02');
  assert.equal(result.electricityCost, 300.3);
  assert.equal(result.totalCost, 300.3);
  assert.equal(result.waterCost, 0);
});
test('invalid or absent numeric fields are not displayed as NaN or zero', () => {
  const result = dashboardSummary([{period: '2026-01', cost: 'bad', WATER_COST: '', ELECTRICITY: Infinity}]);
  assert.equal(result.totalCost, null);
  assert.equal(result.waterCost, null);
  assert.equal(result.electricityUsage, null);
});
