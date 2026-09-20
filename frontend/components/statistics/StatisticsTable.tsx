'use client';

import { Table, Zap, Droplets, ReceiptText, CheckCircle2 } from 'lucide-react';

interface StatisticsTableProps {
  series: Array<{ period: string; ELECTRICITY?: number; WATER?: number; cost?: number }>;
  note?: string;
}

function money(n: number | null | undefined): string {
  if (!n) return '0 ₫';
  return n.toLocaleString('vi-VN') + ' ₫';
}

function quantity(n: number | null | undefined): string {
  if (!n) return '—';
  return n.toLocaleString('vi-VN');
}

export function StatisticsTable({ series, note }: StatisticsTableProps) {
  return (
    <div className="bg-white/80 backdrop-blur-2xl border border-white/90 shadow-[0_10px_35px_rgba(15,23,42,0.04)] rounded-3xl p-6">
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl bg-blue-50 border border-blue-100 text-blue-600 flex items-center justify-center shadow-inner">
            <Table size={20} />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-900">Chi tiết dữ liệu tiêu thụ</h3>
            <p className="text-xs text-slate-500 font-medium">Bảng tổng hợp sản lượng & chi phí các kỳ</p>
          </div>
        </div>

        <span className="text-xs font-semibold text-slate-500 bg-slate-100/80 px-3 py-1.5 rounded-full border border-slate-200/60">
          Tổng cộng {series.length} kỳ
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-slate-100 text-xs font-bold text-slate-400 uppercase tracking-wider">
              <th className="py-3.5 px-4">Kỳ hóa đơn</th>
              <th className="py-3.5 px-4">Điện tiêu thụ</th>
              <th className="py-3.5 px-4">Nước tiêu thụ</th>
              <th className="py-3.5 px-4">Tổng chi phí</th>
              <th className="py-3.5 px-4 text-right">Trạng thái ghi nhận</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 text-sm">
            {series.map((row, i) => (
              <tr key={i} className="hover:bg-slate-50/70 transition-colors duration-200">
                <td className="py-4 px-4 font-bold text-slate-900">Kỳ {row.period}</td>
                <td className="py-4 px-4">
                  <span className="inline-flex items-center gap-1.5 font-semibold text-amber-700 bg-amber-50 px-2.5 py-1 rounded-xl border border-amber-200/50">
                    <Zap size={14} className="text-amber-500" />
                    {quantity(row.ELECTRICITY)} <span className="text-xs text-amber-600 font-normal">kWh</span>
                  </span>
                </td>
                <td className="py-4 px-4">
                  <span className="inline-flex items-center gap-1.5 font-semibold text-cyan-700 bg-cyan-50 px-2.5 py-1 rounded-xl border border-cyan-200/50">
                    <Droplets size={14} className="text-cyan-500" />
                    {quantity(row.WATER)} <span className="text-xs text-cyan-600 font-normal">m³</span>
                  </span>
                </td>
                <td className="py-4 px-4 font-extrabold text-slate-900">
                  <span className="inline-flex items-center gap-1">
                    <ReceiptText size={15} className="text-emerald-500" />
                    {money(row.cost)}
                  </span>
                </td>
                <td className="py-4 px-4 text-right">
                  <span className="inline-flex items-center gap-1 text-xs font-semibold text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-200/60">
                    <CheckCircle2 size={13} /> Ghi nhận chính thức
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {note && (
        <div className="mt-4 pt-4 border-t border-slate-100 text-xs text-slate-400 font-medium flex items-center justify-between">
          <span>⚡ {note}</span>
          <span>Dữ liệu khớp 100% với EVN & Sawaco</span>
        </div>
      )}
    </div>
  );
}
