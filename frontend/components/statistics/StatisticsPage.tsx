'use client';

import { useState } from 'react';
import { Calendar, Download, FileSpreadsheet, Sparkles, Filter } from 'lucide-react';
import { StatSummaryCards } from './StatSummaryCards';
import { UtilityTrendsChart } from './UtilityTrendsChart';
import { CostTrendsChart } from './CostTrendsChart';
import { StatisticsTable } from './StatisticsTable';
import { AISavingTips } from './AISavingTips';
import { useData } from '../application';

function LoadState({ error, loading }: { error: string; loading: boolean }) {
  if (error) return <div className="p-6 bg-red-50 text-red-600 rounded-2xl text-sm border border-red-200">{error}</div>;
  if (loading) return (
    <div className="space-y-4 animate-pulse">
      <div className="h-14 bg-slate-200/60 rounded-2xl w-full" />
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="h-40 bg-slate-200/60 rounded-3xl" />
        <div className="h-40 bg-slate-200/60 rounded-3xl" />
        <div className="h-40 bg-slate-200/60 rounded-3xl" />
      </div>
      <div className="h-80 bg-slate-200/60 rounded-3xl w-full" />
    </div>
  );
  return null;
}

export function StatisticsPage() {
  const [months, setMonths] = useState('6');
  const [start, setStart] = useState('');
  const [end, setEnd] = useState('');

  const custom = months === 'custom';
  const query = custom && start && end ? `start=${start}&end=${end}` : `months=${custom ? '6' : months}`;
  const { data, error, loading } = useData(['/statistics?' + query]);

  if (error || loading) return <LoadState error={error} loading={loading} />;

  const statData = data[0];
  const summary = statData?.summary || {
    ELECTRICITY: { average: 300, lowest: 280, highest: 320 },
    WATER: { average: 10, lowest: 8, highest: 14 },
    cost: { average: 673200, lowest: 520000, highest: 673200 },
  };
  const series = statData?.series || [];
  const note = statData?.note || 'Biểu đồ tính dựa trên chỉ số công tơ ghi nhận hàng tháng.';

  return (
    <div className="space-y-6 pb-12">
      {/* HEADER BAR & CONTROLS */}
      <div className="bg-white/80 backdrop-blur-2xl border border-white/90 shadow-[0_10px_35px_rgba(15,23,42,0.04)] rounded-3xl p-5 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold text-emerald-600 uppercase tracking-wider mb-0.5">
            <Sparkles size={14} /> Phân tích chuyên sâu
          </div>
          <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">Thống kê tiêu dùng & chi phí</h1>
          <p className="text-xs text-slate-500 font-medium">Theo dõi biến động điện, nước và xu hướng tài chính gia đình bạn</p>
        </div>

        {/* CONTROLS */}
        <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
          {/* TIME FILTER */}
          <div className="flex items-center gap-2 bg-slate-100/80 p-1.5 rounded-2xl border border-slate-200/60">
            <Filter size={14} className="text-slate-400 ml-2" />
            <select
              aria-label="Khoảng thời gian thống kê"
              value={months}
              onChange={e => setMonths(e.target.value)}
              className="bg-transparent text-xs font-bold text-slate-700 focus:outline-none pr-3 py-1 cursor-pointer"
            >
              <option value="3">3 tháng gần nhất</option>
              <option value="6">6 tháng gần nhất</option>
              <option value="12">12 tháng gần nhất</option>
              <option value="custom">Tùy chọn khoảng</option>
            </select>
          </div>

          {custom && (
            <div className="flex items-center gap-2 text-xs">
              <input
                type="date"
                aria-label="Từ ngày"
                value={start}
                onChange={e => setStart(e.target.value)}
                className="bg-slate-100/80 px-3 py-1.5 rounded-xl border border-slate-200/60 font-medium text-slate-700 focus:outline-none"
              />
              <span className="text-slate-400">-</span>
              <input
                type="date"
                aria-label="Đến ngày"
                value={end}
                onChange={e => setEnd(e.target.value)}
                className="bg-slate-100/80 px-3 py-1.5 rounded-xl border border-slate-200/60 font-medium text-slate-700 focus:outline-none"
              />
            </div>
          )}

          {/* EXPORT BUTTONS */}
          <button
            type="button"
            onClick={() => window.print()}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-2xl bg-white border border-slate-200/80 text-xs font-bold text-slate-700 hover:bg-slate-50 hover:shadow-md transition-all duration-200"
          >
            <Download size={14} className="text-slate-500" />
            <span>Xuất PDF</span>
          </button>
        </div>
      </div>

      {/* AI RECOMMENDATION TIP */}
      <AISavingTips />

      {/* 3 KPI CARDS */}
      <StatSummaryCards summary={summary} />

      {/* CHARTS GRID */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <UtilityTrendsChart data={series} />
        <CostTrendsChart data={series} />
      </div>

      {/* DATA BREAKDOWN TABLE */}
      <StatisticsTable series={series} note={note} />
    </div>
  );
}
