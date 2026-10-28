type SeriesRow = { period: string; [key: string]: unknown };

function numberOrNull(value: unknown): number | null {
  if (typeof value !== 'number' && typeof value !== 'string') return null;
  if (typeof value === 'string' && !value.trim()) return null;
  const result = Number(value);
  return Number.isFinite(result) ? result : null;
}

/** Read server aggregates without inventing costs or treating missing data as 0. */
export function dashboardSummary(series: SeriesRow[]) {
  const latest = [...series].sort((a, b) => a.period.localeCompare(b.period)).at(-1);
  return {
    period: latest?.period ?? null,
    electricityUsage: numberOrNull(latest?.ELECTRICITY),
    waterUsage: numberOrNull(latest?.WATER),
    electricityCost: numberOrNull(latest?.ELECTRICITY_COST),
    waterCost: numberOrNull(latest?.WATER_COST),
    totalCost: numberOrNull(latest?.cost),
  };
}
