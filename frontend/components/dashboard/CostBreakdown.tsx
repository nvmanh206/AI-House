'use client';
import { motion } from 'framer-motion';
import { CostBreakdownDonut } from '../charts';

interface CostBreakdownProps {
  elecCost: number | null;
  waterCost: number | null;
  period?: string | null;
}

export function CostBreakdown({ elecCost, waterCost, period }: CostBreakdownProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1], delay: 0.05 }}
      className="h-full rounded-3xl border border-slate-200/70 bg-white/85 p-5 backdrop-blur-xl shadow-[0_10px_30px_rgba(15,23,42,0.03)] transition-all hover:shadow-md"
    >
      <div className="mb-3">
        <h2 className="text-base font-bold text-slate-900">
          Phân bổ chi phí
        </h2>
        <p className="text-xs text-slate-500">
          {period ? `Kỳ ${period} · Tiền điện và tiền nước đã ghi nhận` : 'Chưa có kỳ dữ liệu'}
        </p>
      </div>

      <div className="pt-1 flex items-center justify-center">
        {elecCost === null || waterCost === null ? (
          <div className="text-sm text-slate-600">
            {elecCost === null && <p>Chưa có tiền điện.</p>}
            {waterCost === null && <p>Chưa có tiền nước.</p>}
            <p>Cần dữ liệu cả hai loại tiện ích để tính tỷ lệ phân bổ.</p>
          </div>
        ) : elecCost + waterCost === 0 ? (
          <p className="text-sm text-slate-600">Chi phí đã ghi nhận bằng 0 ₫.</p>
        ) : <CostBreakdownDonut electricityCost={elecCost} waterCost={waterCost} />}
      </div>
    </motion.div>
  );
}
