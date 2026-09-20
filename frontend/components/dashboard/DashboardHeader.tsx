'use client';
import { motion } from 'framer-motion';
import { Sparkles, Leaf } from 'lucide-react';

interface DashboardHeaderProps {
  userName?: string;
}

export function DashboardHeader({ userName }: DashboardHeaderProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: -12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
      className="relative mb-6 overflow-hidden rounded-3xl border border-emerald-200/70 bg-gradient-to-r from-emerald-500/10 via-sky-500/10 to-indigo-500/10 p-6 backdrop-blur-2xl shadow-[0_10px_30px_rgba(15,23,42,0.03)]"
    >
      {/* Decorative Light Wave Effect */}
      <div className="pointer-events-none absolute -right-16 -top-16 h-64 w-64 rounded-full bg-emerald-400/20 blur-3xl" />
      <div className="pointer-events-none absolute -bottom-16 left-1/3 h-64 w-64 rounded-full bg-sky-400/20 blur-3xl" />

      <div className="row align-items-center g-4">
        {/* Left Side Greeting */}
        <div className="col-12 col-lg-7">
          <div className="flex items-center gap-2 mb-2">
            <span className="inline-flex items-center gap-1.5 rounded-full border border-emerald-300/60 bg-emerald-100/70 px-3 py-1 text-xs font-bold text-emerald-800 shadow-xs">
              <Leaf className="h-3.5 w-3.5 text-emerald-600" /> HỆ THỐNG GIA ĐÌNH THÔNG MINH
            </span>
          </div>
          <h1 className="text-2xl font-extrabold tracking-tight text-slate-900 sm:text-3xl">
            Tổng quan chi tiêu gia đình 👋
          </h1>
          <p className="mt-1.5 text-sm font-medium text-slate-600 max-w-xl leading-relaxed">
            Theo dõi, kiểm soát và tối ưu chi phí tiện ích của gia đình bạn một cách thông minh với sự hỗ trợ từ Trợ lý AI.
          </p>
        </div>

        {/* Right Side Eco Quote Card */}
        <div className="col-12 col-lg-5">
          <div className="relative overflow-hidden rounded-2xl border border-white/80 bg-white/80 p-4.5 backdrop-blur-xl shadow-xs transition-all hover:shadow-md">
            <div className="flex items-start gap-3">
              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-emerald-500 text-white shadow-xs">
                <Sparkles className="h-4.5 w-4.5" />
              </div>
              <div>
                <p className="text-xs font-bold italic text-slate-800 leading-snug">
                  “Tiết kiệm hôm nay. Cho những điều ý nghĩa mai sau.”
                </p>
                <div className="mt-1 text-[11px] font-semibold text-emerald-700">
                  Nhà xanh · Cuộc sống an lành · Tương lai bền vững
                </div>
              </div>
            </div>
            <div className="mt-3 flex items-center justify-between border-t border-slate-100 pt-2.5 text-[11px] font-medium text-slate-500">
              <span>Đạt chuẩn Tiết kiệm 2026</span>
              <span className="font-semibold text-sky-600">Smart Home AI</span>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
