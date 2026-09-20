'use client';
import { useState } from 'react';
import { motion } from 'framer-motion';
import { ExecutiveSpendingChart } from '../charts';

interface ExpenseTrendChartProps {
  series: any[];
}

export function ExpenseTrendChart({ series }: ExpenseTrendChartProps) {
  const [metric, setMetric] = useState<'cost' | 'ELECTRICITY' | 'WATER'>('cost');

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1] }}
      className="h-full rounded-3xl border border-slate-200/70 bg-white/85 p-5 backdrop-blur-xl shadow-[0_10px_30px_rgba(15,23,42,0.03)] transition-all hover:shadow-md"
    >
      <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
        <div>
          <h2 className="text-base font-bold text-slate-900">
            Xu hướng chi phí 6 tháng
          </h2>
          <p className="text-xs text-slate-500">
            Tổng chi phí tiện ích (điện + nước)
          </p>
        </div>

        {/* Filter Tabs */}
        <div className="inline-flex rounded-xl bg-slate-100/80 p-1 text-xs font-semibold text-slate-600 border border-slate-200/60">
          <button
            onClick={() => setMetric('cost')}
            className={`rounded-lg px-3 py-1.5 transition-all ${
              metric === 'cost'
                ? 'bg-white text-blue-600 shadow-xs font-bold'
                : 'hover:text-slate-900'
            }`}
          >
            Chi phí tổng
          </button>
          <button
            onClick={() => setMetric('ELECTRICITY')}
            className={`rounded-lg px-3 py-1.5 transition-all ${
              metric === 'ELECTRICITY'
                ? 'bg-white text-amber-600 shadow-xs font-bold'
                : 'hover:text-slate-900'
            }`}
          >
            Tiền điện
          </button>
          <button
            onClick={() => setMetric('WATER')}
            className={`rounded-lg px-3 py-1.5 transition-all ${
              metric === 'WATER'
                ? 'bg-white text-sky-600 shadow-xs font-bold'
                : 'hover:text-slate-900'
            }`}
          >
            Tiền nước
          </button>
        </div>
      </div>

      <div className="pt-2">
        <ExecutiveSpendingChart data={series} metric={metric} />
      </div>
    </motion.div>
  );
}
