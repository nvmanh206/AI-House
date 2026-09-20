'use client';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { ChevronRight, Star } from 'lucide-react';

interface BudgetProgressProps {
  budgetPercent: number;
  budgetSpent: number;
  budgetRemaining: number;
  monthlyBudget: number;
}

export function BudgetProgress({
  budgetPercent,
  budgetSpent,
  budgetRemaining,
  monthlyBudget
}: BudgetProgressProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1], delay: 0.15 }}
      className="h-full rounded-3xl border border-slate-200/70 bg-white/85 p-5 backdrop-blur-xl shadow-[0_10px_30px_rgba(15,23,42,0.03)] transition-all hover:shadow-md"
    >
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-base font-bold text-slate-900">
            Tiến độ ngân sách tháng 9
          </h2>
          <p className="text-xs text-slate-500">
            Hạn mức tối đa: {monthlyBudget.toLocaleString('vi-VN')} ₫
          </p>
        </div>
        <Link
          href="/statistics"
          className="inline-flex items-center gap-1 text-xs font-semibold text-blue-600 hover:text-blue-700 hover:underline"
        >
          Chi tiết ngân sách <ChevronRight className="h-4 w-4" />
        </Link>
      </div>

      {/* Progress Track & Numbers */}
      <div className="mb-4">
        <div className="flex items-baseline justify-between mb-2">
          <div>
            <span className="text-xs font-medium text-slate-500">Đã sử dụng: </span>
            <span className="text-lg font-extrabold text-slate-900">{budgetPercent}%</span>
          </div>
          <div className="text-right">
            <span className="text-xs font-medium text-slate-500">Còn lại: </span>
            <span className="text-sm font-bold text-emerald-600">
              {budgetRemaining.toLocaleString('vi-VN')} ₫
            </span>
            <span className="text-xs text-slate-400"> / {monthlyBudget.toLocaleString('vi-VN')} ₫</span>
          </div>
        </div>

        {/* Animated Progress Bar */}
        <div className="h-3 w-full overflow-hidden rounded-full bg-slate-100 p-0.5 border border-slate-200/50">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${budgetPercent}%` }}
            transition={{ duration: 1.2, ease: [0.22, 1, 0.36, 1] }}
            className="h-full rounded-full bg-gradient-to-r from-emerald-500 to-teal-400 shadow-xs"
          />
        </div>
      </div>

      {/* Star Status Card */}
      <div className="flex items-start gap-3 rounded-2xl border border-amber-200/70 bg-gradient-to-r from-amber-50/80 to-yellow-50/80 p-3.5 text-xs text-amber-900">
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-amber-400 text-white shadow-xs">
          <Star className="h-4 w-4 fill-current" />
        </div>
        <div>
          <strong className="block font-bold text-amber-950 mb-0.5">
            Bạn đang kiểm soát chi tiêu tốt!
          </strong>
          <p className="text-amber-800/90 leading-relaxed">
            Tiếp tục duy trì thói quen này để đạt mục tiêu tiết kiệm của gia đình trong tháng này.
          </p>
        </div>
      </div>
    </motion.div>
  );
}
