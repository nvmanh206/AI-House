'use client';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { Sparkles, Leaf, Lightbulb, Home, ChevronRight } from 'lucide-react';

export function AIInsightPanel() {
  const insights = [
    {
      id: 'trend',
      title: 'Xu hướng điện sinh hoạt tăng',
      desc: 'Mức tiêu thụ điện tháng này tăng 8.2% so với tháng trước. Bạn có thể xem lại các thiết bị điện có mức tiêu thụ cao.',
      icon: <Leaf className="h-4 w-4 text-emerald-600" />,
      bgIcon: 'bg-emerald-50 border-emerald-100'
    },
    {
      id: 'saving',
      title: 'Gợi ý tiết kiệm chi phí',
      desc: 'Giảm sử dụng thiết bị không cần thiết có thể giúp tiết kiệm khoảng 80.000 – 120.000đ mỗi tháng.',
      icon: <Lightbulb className="h-4 w-4 text-amber-600" />,
      bgIcon: 'bg-amber-50 border-amber-100'
    },
    {
      id: 'reasonable',
      title: 'Mức chi phí của bạn đang hợp lý',
      desc: 'Chi phí hiện tại thấp hơn 12% so với mức dự báo trung bình của nhóm hộ gia đình tương tự trong khu vực.',
      icon: <Home className="h-4 w-4 text-blue-600" />,
      bgIcon: 'bg-blue-50 border-blue-100'
    }
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1], delay: 0.2 }}
      className="mb-4 rounded-3xl border border-slate-200/70 bg-white/85 p-5 backdrop-blur-xl shadow-[0_10px_30px_rgba(15,23,42,0.03)] transition-all hover:shadow-md"
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-purple-100 text-purple-700">
            <Sparkles className="h-4 w-4" />
          </div>
          <div>
            <h2 className="text-base font-bold text-slate-900">
              AI Insight
            </h2>
            <p className="text-xs text-slate-500">Phân tích sinh thái & tối ưu</p>
          </div>
        </div>

        <Link
          href="/assistant"
          className="rounded-full border border-purple-200 bg-purple-50 px-3 py-1 text-xs font-bold text-purple-700 hover:bg-purple-100 transition-colors"
        >
          Trợ lý nhà mình.
        </Link>
      </div>

      {/* Insight List Items */}
      <div className="space-y-2.5">
        {insights.map(item => (
          <motion.div
            key={item.id}
            whileHover={{ x: 3 }}
            transition={{ duration: 0.2 }}
          >
            <Link
              href="/assistant"
              className="group flex items-start gap-3 rounded-2xl border border-slate-100 bg-slate-50/60 p-3.5 transition-all hover:border-slate-200 hover:bg-white hover:shadow-xs"
            >
              <div className={`mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-xl border ${item.bgIcon}`}>
                {item.icon}
              </div>
              <div className="flex-1">
                <h3 className="text-xs font-bold text-slate-900 group-hover:text-blue-600 transition-colors">
                  {item.title}
                </h3>
                <p className="mt-0.5 text-xs text-slate-600 leading-relaxed">
                  {item.desc}
                </p>
              </div>
              <ChevronRight className="h-4 w-4 shrink-0 text-slate-400 group-hover:text-blue-600 transition-colors self-center" />
            </Link>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
