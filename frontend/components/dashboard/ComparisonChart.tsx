'use client';
import { motion } from 'framer-motion';
import { MonthlyComparisonBar } from '../charts';

interface ComparisonChartProps {
  series: any[];
}

export function ComparisonChart({ series }: ComparisonChartProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1], delay: 0.1 }}
      className="h-full rounded-3xl border border-slate-200/70 bg-white/85 p-5 backdrop-blur-xl shadow-[0_10px_30px_rgba(15,23,42,0.03)] transition-all hover:shadow-md"
    >
      <div className="mb-3">
        <h2 className="text-base font-bold text-slate-900">
          So sánh chi phí qua các kỳ
        </h2>
        <p className="text-xs text-slate-500">
          Đơn vị: nghìn đồng (tiền điện vs tiền nước)
        </p>
      </div>

      <div className="pt-1">
        <MonthlyComparisonBar data={series} />
      </div>
    </motion.div>
  );
}
