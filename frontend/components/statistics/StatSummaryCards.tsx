'use client';

import { motion } from 'framer-motion';
import { Zap, Droplets, ReceiptText, TrendingUp, TrendingDown, Sparkles } from 'lucide-react';
import { useCountUp } from '../dashboard/useCountUp';

interface StatSummaryCardsProps {
  summary: {
    ELECTRICITY?: { average: number | null; lowest: number | null; highest: number | null };
    WATER?: { average: number | null; lowest: number | null; highest: number | null };
    cost?: { average: number | null; lowest: number | null; highest: number | null };
  };
}

function money(n: number | null | undefined): string {
  if (n === null || n === undefined) return '— ₫';
  return n.toLocaleString('vi-VN') + ' ₫';
}

function quantity(n: number | null | undefined): string {
  if (n === null || n === undefined) return '—';
  return n.toLocaleString('vi-VN');
}

export function StatSummaryCards({ summary }: StatSummaryCardsProps) {
  const elecAvg = summary.ELECTRICITY?.average ?? null;
  const elecLow = summary.ELECTRICITY?.lowest ?? null;
  const elecHigh = summary.ELECTRICITY?.highest ?? null;

  const waterAvg = summary.WATER?.average ?? null;
  const waterLow = summary.WATER?.lowest ?? null;
  const waterHigh = summary.WATER?.highest ?? null;

  const costAvg = summary.cost?.average ?? null;
  const costLow = summary.cost?.lowest ?? null;
  const costHigh = summary.cost?.highest ?? null;

  const animatedElec = useCountUp(typeof elecAvg === 'number' ? elecAvg : 0);
  const animatedWater = useCountUp(typeof waterAvg === 'number' ? waterAvg : 0);
  const animatedCost = useCountUp(typeof costAvg === 'number' ? costAvg : 0);

  const containerVariants = {
    hidden: {},
    visible: { transition: { staggerChildren: 0.08 } },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 16 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.4 } },
  };

  return (
    <motion.div
      className="grid grid-cols-1 md:grid-cols-3 gap-5 mb-6"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {/* ELECTRICITY KPI CARD */}
      <motion.div
        variants={itemVariants}
        whileHover={{ y: -4, transition: { duration: 0.2 } }}
        className="relative overflow-hidden rounded-3xl bg-white/80 backdrop-blur-2xl border border-white/90 shadow-[0_10px_35px_rgba(15,23,42,0.04)] p-6 group hover:shadow-[0_20px_45px_rgba(245,158,11,0.12)] transition-all duration-300"
      >
        <div className="absolute top-0 right-0 w-32 h-32 bg-amber-200/30 rounded-full blur-2xl group-hover:scale-125 transition-transform duration-500 pointer-events-none" />
        
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-amber-600 flex items-center justify-center shadow-inner group-hover:scale-110 transition-transform duration-300">
              <Zap size={22} className="fill-amber-400/30" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wider">Điện sinh hoạt</h3>
              <span className="text-xs text-slate-400 font-medium">Trung bình kỳ nhập</span>
            </div>
          </div>
          <span className="inline-flex items-center gap-1 text-xs font-semibold px-2.5 py-1 rounded-full bg-amber-50 text-amber-700 border border-amber-200/60">
            <TrendingUp size={12} /> +8.2%
          </span>
        </div>

        <div className="mb-4">
          <div className="text-3xl font-extrabold text-slate-900 tracking-tight flex items-baseline gap-1.5">
            <span>{animatedElec.toLocaleString('vi-VN')}</span>
            <span className="text-base font-medium text-slate-400">kWh</span>
          </div>
        </div>

        <div className="pt-3 border-t border-slate-100/80 flex items-center justify-between text-xs text-slate-500">
          <div>Thấp nhất: <strong className="text-slate-700 font-semibold">{quantity(elecLow)} kWh</strong></div>
          <div>Cao nhất: <strong className="text-slate-700 font-semibold">{quantity(elecHigh)} kWh</strong></div>
        </div>
      </motion.div>

      {/* WATER KPI CARD */}
      <motion.div
        variants={itemVariants}
        whileHover={{ y: -4, transition: { duration: 0.2 } }}
        className="relative overflow-hidden rounded-3xl bg-white/80 backdrop-blur-2xl border border-white/90 shadow-[0_10px_35px_rgba(15,23,42,0.04)] p-6 group hover:shadow-[0_20px_45px_rgba(6,182,212,0.12)] transition-all duration-300"
      >
        <div className="absolute top-0 right-0 w-32 h-32 bg-cyan-200/30 rounded-full blur-2xl group-hover:scale-125 transition-transform duration-500 pointer-events-none" />

        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-600 flex items-center justify-center shadow-inner group-hover:scale-110 transition-transform duration-300">
              <Droplets size={22} className="fill-cyan-400/30" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wider">Nước sinh hoạt</h3>
              <span className="text-xs text-slate-400 font-medium">Trung bình kỳ nhập</span>
            </div>
          </div>
          <span className="inline-flex items-center gap-1 text-xs font-semibold px-2.5 py-1 rounded-full bg-cyan-50 text-cyan-700 border border-cyan-200/60">
            <TrendingDown size={12} /> -100%
          </span>
        </div>

        <div className="mb-4">
          <div className="text-3xl font-extrabold text-slate-900 tracking-tight flex items-baseline gap-1.5">
            <span>{animatedWater.toLocaleString('vi-VN')}</span>
            <span className="text-base font-medium text-slate-400">m³</span>
          </div>
        </div>

        <div className="pt-3 border-t border-slate-100/80 flex items-center justify-between text-xs text-slate-500">
          <div>Thấp nhất: <strong className="text-slate-700 font-semibold">{quantity(waterLow)} m³</strong></div>
          <div>Cao nhất: <strong className="text-slate-700 font-semibold">{quantity(waterHigh)} m³</strong></div>
        </div>
      </motion.div>

      {/* TOTAL COST KPI CARD */}
      <motion.div
        variants={itemVariants}
        whileHover={{ y: -4, transition: { duration: 0.2 } }}
        className="relative overflow-hidden rounded-3xl bg-white/80 backdrop-blur-2xl border border-white/90 shadow-[0_10px_35px_rgba(15,23,42,0.04)] p-6 group hover:shadow-[0_20px_45px_rgba(16,185,129,0.12)] transition-all duration-300"
      >
        <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-200/30 rounded-full blur-2xl group-hover:scale-125 transition-transform duration-500 pointer-events-none" />

        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-600 flex items-center justify-center shadow-inner group-hover:scale-110 transition-transform duration-300">
              <ReceiptText size={22} />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wider">Tổng chi phí</h3>
              <span className="text-xs text-slate-400 font-medium">Trung bình các kỳ</span>
            </div>
          </div>
          <span className="inline-flex items-center gap-1 text-xs font-semibold px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200/60">
            <Sparkles size={12} /> Tiết kiệm tốt
          </span>
        </div>

        <div className="mb-4">
          <div className="text-3xl font-extrabold text-slate-900 tracking-tight flex items-baseline gap-1.5">
            <span>{animatedCost.toLocaleString('vi-VN')}</span>
            <span className="text-base font-medium text-slate-400">₫</span>
          </div>
        </div>

        <div className="pt-3 border-t border-slate-100/80 flex items-center justify-between text-xs text-slate-500">
          <div>Thấp nhất: <strong className="text-slate-700 font-semibold">{money(costLow)}</strong></div>
          <div>Cao nhất: <strong className="text-slate-700 font-semibold">{money(costHigh)}</strong></div>
        </div>
      </motion.div>
    </motion.div>
  );
}
