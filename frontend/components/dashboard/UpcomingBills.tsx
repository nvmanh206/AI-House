'use client';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { Zap, Droplets, ArrowRight } from 'lucide-react';

interface UpcomingBillsProps {
  bills: any[];
}

export function UpcomingBills({ bills }: UpcomingBillsProps) {
  const unpaidList = bills.filter(b => ['UNPAID', 'OVERDUE'].includes(b.status));

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1], delay: 0.25 }}
      className="rounded-3xl border border-slate-200/70 bg-white/85 p-5 backdrop-blur-xl shadow-[0_10px_30px_rgba(15,23,42,0.03)] transition-all hover:shadow-md"
    >
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-base font-bold text-slate-900">
            Hóa đơn sắp đến hạn
          </h2>
          <p className="text-xs text-slate-500">
            Danh sách các hóa đơn cần thanh toán trong kỳ
          </p>
        </div>
        <Link
          href="/bills"
          className="inline-flex items-center gap-1 text-xs font-semibold text-blue-600 hover:text-blue-700 hover:underline"
        >
          Xem tất cả hóa đơn <ArrowRight className="h-3.5 w-3.5" />
        </Link>
      </div>

      {unpaidList.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-slate-200 bg-slate-50/50 p-6 text-center">
          <div className="mx-auto mb-2 flex h-10 w-10 items-center justify-center rounded-full bg-emerald-50 text-emerald-600">
            <Zap className="h-5 w-5" />
          </div>
          <p className="text-xs font-bold text-slate-800">Tất cả hóa đơn đã được thanh toán</p>
          <p className="mt-1 text-[11px] text-slate-500">Không có hóa đơn nào sắp đến hạn cần xử lý.</p>
        </div>
      ) : (
        <>
          {/* Desktop Table */}
          <div className="hidden md:block overflow-x-auto rounded-2xl border border-slate-100 bg-white shadow-xs">
            <table className="w-full text-left text-xs">
              <thead className="border-b border-slate-100 bg-slate-50/70 text-[11px] font-bold uppercase tracking-wider text-slate-500">
                <tr>
                  <th className="py-3 px-4">Loại hóa đơn</th>
                  <th className="py-3 px-4">Kỳ hóa đơn</th>
                  <th className="py-3 px-4">Số tiền</th>
                  <th className="py-3 px-4">Hạn thanh toán</th>
                  <th className="py-3 px-4">Trạng thái</th>
                  <th className="py-3 px-4 text-right">Thao tác</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
                {unpaidList.map(b => (
                  <tr key={b.id} className="hover:bg-slate-50/50 transition-colors">
                    <td className="py-3.5 px-4 font-bold text-slate-900">
                      <div className="flex items-center gap-2.5">
                        <div className={`flex h-7 w-7 items-center justify-center rounded-lg ${b.utility_type === 'ELECTRICITY' ? 'bg-amber-100 text-amber-700' : 'bg-sky-100 text-sky-700'}`}>
                          {b.utility_type === 'ELECTRICITY' ? <Zap className="h-3.5 w-3.5" /> : <Droplets className="h-3.5 w-3.5" />}
                        </div>
                        <span>{b.utility_type === 'ELECTRICITY' ? 'Tiền điện' : 'Tiền nước'}</span>
                      </div>
                    </td>
                    <td className="py-3.5 px-4 text-slate-600">{b.period}</td>
                    <td className="py-3.5 px-4 font-extrabold text-slate-900">
                      {Number(b.final_amount).toLocaleString('vi-VN')} ₫
                    </td>
                    <td className="py-3.5 px-4">
                      <div>{b.due_date}</div>
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="inline-flex items-center gap-1 rounded-full border border-amber-200/80 bg-amber-50 px-2.5 py-0.5 text-[11px] font-semibold text-amber-800">
                        <span className="h-1.5 w-1.5 rounded-full bg-amber-500" />
                        {b.status === 'OVERDUE' ? 'Quá hạn' : 'Chưa thanh toán'}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <Link
                        href="/bills"
                        className="inline-flex items-center justify-center rounded-xl bg-blue-600 px-4 py-1.5 text-xs font-semibold text-white shadow-xs hover:bg-blue-700 transition-all active:scale-95"
                      >
                        Thanh toán
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Mobile Card List View */}
          <div className="md:hidden space-y-3">
            {unpaidList.map(b => (
              <div key={b.id} className="rounded-2xl border border-slate-100 bg-white p-4 shadow-xs">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <div className={`flex h-7 w-7 items-center justify-center rounded-lg ${b.utility_type === 'ELECTRICITY' ? 'bg-amber-100 text-amber-700' : 'bg-sky-100 text-sky-700'}`}>
                      {b.utility_type === 'ELECTRICITY' ? <Zap className="h-3.5 w-3.5" /> : <Droplets className="h-3.5 w-3.5" />}
                    </div>
                    <span className="font-bold text-slate-900 text-xs">{b.utility_type === 'ELECTRICITY' ? 'Tiền điện' : 'Tiền nước'}</span>
                  </div>
                  <span className="inline-flex items-center rounded-full border border-amber-200/80 bg-amber-50 px-2 py-0.5 text-[10px] font-bold text-amber-800">
                    {b.status === 'OVERDUE' ? 'Quá hạn' : 'Chưa thanh toán'}
                  </span>
                </div>
                <div className="flex items-baseline justify-between mb-3 text-xs">
                  <span className="text-slate-500">Kỳ {b.period} · Hạn {b.due_date}</span>
                  <span className="font-extrabold text-slate-900 text-sm">{Number(b.final_amount).toLocaleString('vi-VN')} ₫</span>
                </div>
                <Link
                  href="/bills"
                  className="block w-full text-center rounded-xl bg-blue-600 py-2 text-xs font-semibold text-white shadow-xs hover:bg-blue-700 transition-all"
                >
                  Thanh toán ngay
                </Link>
              </div>
            ))}
          </div>
        </>
      )}
    </motion.div>
  );
}
