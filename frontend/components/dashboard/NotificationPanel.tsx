'use client';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { Bell, FileText, Bot, Gauge, ChevronRight } from 'lucide-react';

interface NotificationPanelProps {
  notifications: any[];
}

export function NotificationPanel({ notifications }: NotificationPanelProps) {
  const items = notifications.length ? notifications.slice(0, 3) : [
    {
      id: 'n1',
      title: 'Hóa đơn tiền điện kỳ 09/2026 đã được tạo',
      desc: 'Số tiền 673.200 đ - Hạn thanh toán 28/09/2026',
      time: '2 giờ trước',
      type: 'bill'
    },
    {
      id: 'n2',
      title: 'Cập nhật tính năng Trợ lý AI',
      desc: 'Trải nghiệm phiên bản Trợ lý thông minh hơn.',
      time: '1 ngày trước',
      type: 'ai'
    },
    {
      id: 'n3',
      title: 'Chỉ số điện đã được ghi nhận',
      desc: 'Chỉ số tháng 9/2026: 300 kWh',
      time: '3 ngày trước',
      type: 'reading'
    }
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1], delay: 0.3 }}
      className="rounded-3xl border border-slate-200/70 bg-white/85 p-5 backdrop-blur-xl shadow-[0_10px_30px_rgba(15,23,42,0.03)] transition-all hover:shadow-md"
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-orange-100 text-orange-600">
            <Bell className="h-4 w-4" />
          </div>
          <h2 className="text-base font-bold text-slate-900">
            Thông báo gần đây
          </h2>
        </div>
        <Link
          href="/notifications"
          className="text-xs font-semibold text-blue-600 hover:text-blue-700 hover:underline"
        >
          Xem tất cả <ChevronRight className="inline h-3.5 w-3.5" />
        </Link>
      </div>

      <div className="space-y-2.5">
        {items.map((n: any) => (
          <div
            key={n.id}
            className="group flex items-start gap-3 rounded-2xl border border-slate-100 bg-slate-50/50 p-3 transition-all hover:border-slate-200 hover:bg-white"
          >
            <div className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-blue-50 text-blue-600 border border-blue-100">
              {n.type === 'bill' ? <FileText className="h-3.5 w-3.5" /> : n.type === 'ai' ? <Bot className="h-3.5 w-3.5 text-purple-600" /> : <Gauge className="h-3.5 w-3.5 text-emerald-600" />}
            </div>
            <div className="flex-1">
              <h3 className="text-xs font-bold text-slate-900 group-hover:text-blue-600 transition-colors">
                {n.title}
              </h3>
              <p className="mt-0.5 text-[11px] text-slate-500 leading-snug">
                {n.desc || n.message}
              </p>
            </div>
            <span className="shrink-0 text-[10px] font-medium text-slate-400">
              {n.time || 'vừa xong'}
            </span>
          </div>
        ))}
      </div>
    </motion.div>
  );
}
