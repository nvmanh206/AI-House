'use client';
import { motion } from 'framer-motion';
import { CostBreakdownDonut } from '../charts';

interface CostBreakdownProps {
  elecCost: number;
  waterCost: number;
}

export function CostBreakdown({ elecCost, waterCost }: CostBreakdownProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1], delay: 0.05 }}
      className="h-full rounded-3xl border border-slate-200/70 bg-white/85 p-5 backdrop-blur-xl shadow-[0_10px_30px_rgba(15,23,42,0.03)] transition-all hover:shadow-md"
    >
      <div className="mb-3">
        <h2 className="text-base font-bold text-slate-900">
          Phân bổ chi phí tháng này
        </h2>
        <p className="text-xs text-slate-500">
          Tỷ lệ giữa tiền điện và tiền nước
        </p>
      </div>

      <div className="pt-1 flex items-center justify-center">
        <CostBreakdownDonut electricityCost={elecCost} waterCost={waterCost} />
      </div>
    </motion.div>
  );
}
