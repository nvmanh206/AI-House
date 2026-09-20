'use client';

import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';
import { Zap, Droplets, Activity } from 'lucide-react';

interface UtilityTrendsChartProps {
  data: Array<{ period: string; ELECTRICITY?: number; WATER?: number; cost?: number }>;
}

function CustomTooltip({ active, payload, label }: any) {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white/90 backdrop-blur-xl border border-white/90 shadow-[0_10px_30px_rgba(15,23,42,0.12)] rounded-2xl p-3 text-xs space-y-1.5 min-w-[140px]">
        <div className="font-bold text-slate-800 border-b border-slate-100 pb-1 flex items-center justify-between">
          <span>Kỳ {label}</span>
          <Activity size={12} className="text-slate-400" />
        </div>
        {payload.map((entry: any, index: number) => (
          <div key={index} className="flex items-center justify-between gap-3">
            <span className="flex items-center gap-1.5 font-medium" style={{ color: entry.color }}>
              {entry.name === 'Điện' ? <Zap size={12} /> : <Droplets size={12} />}
              {entry.name}
            </span>
            <strong className="text-slate-900 font-bold">
              {entry.value?.toLocaleString('vi-VN')} {entry.name === 'Điện' ? 'kWh' : 'm³'}
            </strong>
          </div>
        ))}
      </div>
    );
  }
  return null;
}

export function UtilityTrendsChart({ data }: UtilityTrendsChartProps) {
  const formattedData = data.map(item => ({
    period: item.period,
    Điện: item.ELECTRICITY ?? 300,
    Nước: item.WATER ?? 10,
  }));

  return (
    <div className="bg-white/80 backdrop-blur-2xl border border-white/90 shadow-[0_10px_35px_rgba(15,23,42,0.04)] rounded-3xl p-6 mb-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl bg-indigo-50 border border-indigo-100 text-indigo-600 flex items-center justify-center shadow-inner">
            <Activity size={20} />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-900">Điện & Nước tiêu thụ theo kỳ</h3>
            <p className="text-xs text-slate-500 font-medium">So sánh lượng sản lượng sản xuất & sinh hoạt (kWh vs m³)</p>
          </div>
        </div>

        <div className="flex items-center gap-4 text-xs font-semibold">
          <span className="flex items-center gap-1.5 text-amber-600">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500" /> Điện (kWh)
          </span>
          <span className="flex items-center gap-1.5 text-cyan-600">
            <span className="w-2.5 h-2.5 rounded-full bg-cyan-500" /> Nước (m³)
          </span>
        </div>
      </div>

      <div className="h-[280px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={formattedData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="elecGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.35} />
                <stop offset="95%" stopColor="#f59e0b" stopOpacity={0.0} />
              </linearGradient>
              <linearGradient id="waterGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.35} />
                <stop offset="95%" stopColor="#06b6d4" stopOpacity={0.0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
            <XAxis dataKey="period" tickLine={false} axisLine={false} tick={{ fontSize: 12, fill: '#64748b' }} dy={10} />
            <YAxis tickLine={false} axisLine={false} tick={{ fontSize: 12, fill: '#64748b' }} dx={-5} />
            <Tooltip content={<CustomTooltip />} />
            <Area type="monotone" dataKey="Điện" stroke="#f59e0b" strokeWidth={2.5} fillOpacity={1} fill="url(#elecGrad)" />
            <Area type="monotone" dataKey="Nước" stroke="#06b6d4" strokeWidth={2.5} fillOpacity={1} fill="url(#waterGrad)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
