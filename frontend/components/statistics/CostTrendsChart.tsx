import { useMemo } from 'react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';
import { DollarSign, ArrowUpRight } from 'lucide-react';

interface CostTrendsChartProps {
  data: Array<{ period: string; cost?: number }>;
}

function money(n: number | null | undefined): string {
  if (!n) return '0 ₫';
  return n.toLocaleString('vi-VN') + ' ₫';
}

function CustomTooltip({ active, payload, label }: any) {
  if (active && payload && payload.length) {
    const val = payload[0].value;
    return (
      <div className="bg-white/90 backdrop-blur-xl border border-white/90 shadow-[0_10px_30px_rgba(15,23,42,0.12)] rounded-2xl p-3 text-xs space-y-1">
        <div className="font-bold text-slate-800 border-b border-slate-100 pb-1">Kỳ {label}</div>
        <div className="flex items-center justify-between gap-3 pt-1">
          <span className="text-emerald-600 font-medium">Tổng chi phí:</span>
          <strong className="text-slate-900 font-extrabold text-sm">{money(val)}</strong>
        </div>
      </div>
    );
  }
  return null;
}

export function CostTrendsChart({ data }: CostTrendsChartProps) {
  const formattedData = useMemo(() => {
    return data.map(item => ({
      period: item.period,
      cost: item.cost ?? 0,
    }));
  }, [data]);

  return (
    <div className="bg-white/80 backdrop-blur-2xl border border-white/90 shadow-[0_10px_35px_rgba(15,23,42,0.04)] rounded-3xl p-6 mb-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl bg-emerald-50 border border-emerald-100 text-emerald-600 flex items-center justify-center shadow-inner">
            <DollarSign size={20} />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-900">Chi phí theo kỳ (VNĐ)</h3>
            <p className="text-xs text-slate-500 font-medium">Tổng số tiền hóa đơn phát sinh hàng tháng</p>
          </div>
        </div>

        <span className="inline-flex items-center gap-1 text-xs font-semibold px-3 py-1.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200/60">
          <ArrowUpRight size={14} /> Biến động hợp lý
        </span>
      </div>

      <div className="h-[260px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={formattedData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
            <defs>
              <linearGradient id="barCostGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#10b981" stopOpacity={0.9} />
                <stop offset="100%" stopColor="#059669" stopOpacity={0.7} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
            <XAxis dataKey="period" tickLine={false} axisLine={false} tick={{ fontSize: 12, fill: '#64748b' }} dy={10} />
            <YAxis tickLine={false} axisLine={false} tick={{ fontSize: 12, fill: '#64748b' }} dx={-5} tickFormatter={val => (val / 1000) + 'k'} />
            <Tooltip content={<CustomTooltip />} />
            <Bar dataKey="cost" fill="url(#barCostGrad)" radius={[8, 8, 0, 0]} maxBarSize={48} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
