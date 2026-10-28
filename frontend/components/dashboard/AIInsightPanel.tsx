'use client';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { Sparkles } from 'lucide-react';

export function AIInsightPanel() {
  const insights = [
    {
      id: 'trend',
      title: 'Theo dõi mức sử dụng',
      desc: 'Ghi chỉ số đều đặn để có dữ liệu so sánh lượng điện, nước giữa các kỳ đã nhập.',
    },
    {
      id: 'saving',
      title: 'Gợi ý tiết kiệm chi phí',
      desc: 'Tắt thiết bị khi không sử dụng và kiểm tra rò rỉ nước. Chưa có dữ liệu để tính số tiền gia đình bạn có thể tiết kiệm.',
    },
    {
      id: 'reasonable',
      title: 'Xem lại căn cứ tính tiền',
      desc: 'Kiểm tra chỉ số, biểu giá và nguồn dữ liệu trước khi đối chiếu ước tính với hóa đơn từ nhà cung cấp.',
    }
  ];

  return (
    <motion.div
      initial={false}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1], delay: 0.2 }}
      className="mb-4 rounded-3xl border border-slate-200/70 bg-white/85 p-5 backdrop-blur-xl shadow-[0_10px_30px_rgba(15,23,42,0.03)] transition-all hover:shadow-md"
    >
      <div className="flex flex-wrap items-start justify-between gap-3 mb-4">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-purple-100 text-purple-700">
            <Sparkles className="h-4 w-4" />
          </div>
          <div>
            <h2 className="text-base font-bold text-slate-900">
              Gợi ý chung
            </h2>
            <p className="text-xs text-slate-600">Đây chưa phải phân tích dữ liệu của hộ.</p>
          </div>
        </div>

        <Link
          href="/assistant"
          className="shrink-0 whitespace-nowrap rounded-full border border-purple-200 bg-purple-50 px-3 py-1 text-xs font-bold text-purple-700 hover:bg-purple-100 transition-colors"
        >
          Mở trợ lý
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
              <div className="min-w-0 flex-1">
                <h3 className="text-xs font-bold text-slate-900 group-hover:text-blue-600 transition-colors">
                  {item.title}
                </h3>
                <p className="mt-0.5 text-xs text-slate-600 leading-relaxed">
                  {item.desc}
                </p>
              </div>
            </Link>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
