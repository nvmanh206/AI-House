'use client';

import { Sparkles, Leaf, Lightbulb, ArrowRight } from 'lucide-react';
import Link from 'next/link';

export function AISavingTips() {
  return (
    <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-emerald-600 via-teal-600 to-cyan-600 p-6 text-white shadow-xl shadow-emerald-500/20 mb-6 group">
      <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full blur-3xl group-hover:scale-125 transition-transform duration-500 pointer-events-none" />
      
      <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex items-start gap-4">
          <div className="w-12 h-12 rounded-2xl bg-white/20 backdrop-blur-xl border border-white/30 flex items-center justify-center shrink-0 shadow-lg">
            <Sparkles size={24} className="text-yellow-300 animate-pulse" />
          </div>
          <div>
            <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-white/20 backdrop-blur-md text-xs font-semibold text-emerald-100 mb-1 border border-white/20">
              <Leaf size={12} /> Đề xuất tối ưu hóa năng lượng AI
            </div>
            <h3 className="text-lg font-extrabold tracking-tight">Cơ hội tiết kiệm thêm ~180.000 ₫/tháng</h3>
            <p className="text-xs text-emerald-100/90 max-w-2xl mt-0.5">
              Dựa trên phân tích 6 kỳ vừa qua, việc điều chỉnh khung giờ sử dụng các thiết bị công suất cao có thể giúp gia đình bạn giảm thêm 12% tổng chi phí điện sinh hoạt.
            </p>
          </div>
        </div>

        <Link
          href="/assistant"
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-2xl bg-white text-emerald-800 text-xs font-bold hover:bg-emerald-50 hover:shadow-lg transition-all duration-300 shrink-0 border border-white/50"
        >
          <span>Hỏi Trợ Lý AI</span>
          <ArrowRight size={14} />
        </Link>
      </div>
    </div>
  );
}
