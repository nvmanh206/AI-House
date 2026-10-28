'use client';

import React from 'react';
import { Zap, Droplets, AlertTriangle, HelpCircle, Sparkles, CheckCircle2 } from 'lucide-react';

export type OCRResultData = {
    status: string;
    bill?: {
        type?: string;
        period?: string | null;
        customer_code?: string | null;
        previous_reading?: number | null;
        current_reading?: number | null;
        consumption?: number | null;
        amount?: number | null;
        due_date?: string | null;
        invoice_code?: string | null;
        meter_code?: string | null;
    };
    meter_verification?: {
        status: 'MATCH' | 'MISMATCH' | 'UNKNOWN';
        ocr_reading: number | null;
        database_reading: number | null;
        difference: number | null;
        unit: string;
    };
    comparison?: {
        previous_3_period_average?: number | null;
        current_consumption?: number | null;
        difference_percent?: number | null;
        trend?: string;
    };
    amount_analysis?: {
        ocr_amount?: number | null;
        expected_amount?: number | null;
        difference?: number | null;
        difference_percent?: number | null;
    };
    warnings?: Array<{
        code: string;
        severity: 'critical' | 'high' | 'warning' | 'notice' | 'info';
        message: string;
    }>;
    forecast?: {
        next_period_consumption?: number | null;
        estimated_amount?: number | null;
        trend?: string;
        confidence?: string;
    };
};

export function BillAnalysisCard({ result }: { result: OCRResultData }) {
    if (!result || result.status !== 'success' || !result.bill) return null;

    const { bill, meter_verification, forecast } = result;
    const isElectric = bill.type?.toLowerCase() === 'electricity';
    
    const verStatus = meter_verification?.status || 'UNKNOWN';
    const ocrReading = meter_verification?.ocr_reading ?? bill.current_reading ?? null;
    const dbReading = meter_verification?.database_reading ?? null;
    const diff = meter_verification?.difference ?? null;
    const unitStr = meter_verification?.unit || (isElectric ? 'kWh' : 'm³');

    const hasOptionalData = (bill.consumption !== null && bill.consumption !== undefined) || (bill.amount !== null && bill.amount !== undefined);

    return (
        <div className="bill-analysis-card rounded-2xl bg-white/95 dark:bg-slate-900/95 border border-slate-200 dark:border-slate-800 p-4 sm:p-5 shadow-sm my-3 space-y-4 text-slate-800 dark:text-slate-100">
            {/* CARD HEADER */}
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
                <div className="flex items-center gap-2.5">
                    <div className={`p-2 rounded-xl text-white font-bold shadow-xs ${isElectric ? 'bg-amber-500' : 'bg-blue-500'}`}>
                        {isElectric ? <Zap size={18} /> : <Droplets size={18} />}
                    </div>
                    <div>
                        <h4 className="text-sm sm:text-base font-bold text-slate-900 dark:text-white leading-tight">
                            Hóa đơn {isElectric ? 'Điện' : 'Nước'} {bill.period ? `(Kỳ ${bill.period})` : ''}
                        </h4>
                        {bill.customer_code && (
                            <p className="text-xs text-slate-500 dark:text-slate-400 font-medium">
                                Mã KH: <span className="font-mono">{bill.customer_code}</span>
                            </p>
                        )}
                    </div>
                </div>

                {/* DYNAMIC VERIFICATION BADGE */}
                {verStatus === 'MATCH' && (
                    <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800">
                        <CheckCircle2 size={14} />
                        <span>✓ Trùng chỉ số</span>
                    </div>
                )}
                {verStatus === 'MISMATCH' && (
                    <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-50 dark:bg-amber-950/40 text-amber-800 dark:text-amber-400 border border-amber-300 dark:border-amber-800">
                        <AlertTriangle size={14} />
                        <span>⚠ Không trùng chỉ số</span>
                    </div>
                )}
                {verStatus === 'UNKNOWN' && (
                    <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700">
                        <HelpCircle size={14} />
                        <span>? Chưa đối soát được</span>
                    </div>
                )}
            </div>

            {/* METER READING COMPARISON MAIN SECTION */}
            <div className="p-4 rounded-xl bg-slate-50/80 dark:bg-slate-800/40 border border-slate-200/80 dark:border-slate-800 text-center space-y-3">
                <span className="text-xs font-extrabold uppercase tracking-wider text-slate-500 dark:text-slate-400 block">
                    ĐỐI SOÁT CHỈ SỐ CÔNG TƠ
                </span>

                <div className="grid grid-cols-2 gap-3 items-center max-w-sm mx-auto">
                    <div className="p-3 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-xs">
                        <span className="text-[11px] font-medium text-slate-500 dark:text-slate-400 block mb-0.5">Hóa đơn</span>
                        <strong className="text-base sm:text-lg font-bold text-slate-900 dark:text-white block">
                            {ocrReading !== null ? `${ocrReading.toLocaleString('vi-VN')} ${unitStr}` : 'Không đọc được'}
                        </strong>
                    </div>

                    <div className="p-3 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-xs">
                        <span className="text-[11px] font-medium text-slate-500 dark:text-slate-400 block mb-0.5">Hệ thống</span>
                        <strong className="text-base sm:text-lg font-bold text-slate-900 dark:text-white block">
                            {dbReading !== null ? `${dbReading.toLocaleString('vi-VN')} ${unitStr}` : '---'}
                        </strong>
                    </div>
                </div>

                {diff !== null && diff !== 0 && (
                    <p className="text-xs font-bold text-amber-600 dark:text-amber-400">
                        Chênh lệch: <span className="font-extrabold">{diff > 0 ? `+${diff}` : diff} {unitStr}</span>
                    </p>
                )}

                {/* STATUS CALLOUT BOX */}
                {verStatus === 'MATCH' && (
                    <div className="p-2.5 rounded-lg bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-200/80 dark:border-emerald-800/80 text-emerald-800 dark:text-emerald-200 text-xs font-medium flex items-center justify-center gap-2">
                        <CheckCircle2 size={16} className="text-emerald-600 dark:text-emerald-400 shrink-0" />
                        <span>Chỉ số công tơ trên hóa đơn trùng với chỉ số hiện có trong hệ thống.</span>
                    </div>
                )}

                {verStatus === 'MISMATCH' && (
                    <div className="p-2.5 rounded-lg bg-amber-50 dark:bg-amber-950/30 border border-amber-300 dark:border-amber-800 text-amber-900 dark:text-amber-200 text-xs font-medium flex items-center justify-center gap-2">
                        <AlertTriangle size={16} className="text-amber-600 dark:text-amber-400 shrink-0" />
                        <span>Chỉ số công tơ không trùng khớp (Hóa đơn: {ocrReading} {unitStr} | Hệ thống: {dbReading} {unitStr}).</span>
                    </div>
                )}

                {verStatus === 'UNKNOWN' && (
                    <div className="p-2.5 rounded-lg bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 text-xs font-medium flex items-center justify-center gap-2">
                        <HelpCircle size={16} className="text-slate-500 shrink-0" />
                        <span>Chưa đủ dữ liệu để đối chiếu đúng tài khoản, công tơ và kỳ hóa đơn. Kiểm tra mã khách hàng, kỳ và chỉ số đã ghi; nếu thiếu chỉ số, hãy gửi ảnh rõ hơn.</span>
                    </div>
                )}
            </div>

            {/* SECONDARY OPTIONAL INFORMATION (NO EMPTY CARDS WITH ---) */}
            {hasOptionalData && (
                <div className="pt-2 border-t border-slate-100 dark:border-slate-800 space-y-2">
                    <span className="text-[11px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider block">
                        Thông tin bổ sung
                    </span>
                    <div className="grid grid-cols-2 gap-2 text-xs">
                        {bill.consumption !== null && bill.consumption !== undefined && (
                            <div className="p-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-800">
                                <span className="text-slate-500 dark:text-slate-400 block text-[11px]">Sản lượng tiêu thụ</span>
                                <strong className="text-slate-900 dark:text-white font-bold text-sm">
                                    {bill.consumption.toLocaleString('vi-VN')} {unitStr}
                                </strong>
                            </div>
                        )}
                        {bill.amount !== null && bill.amount !== undefined && (
                            <div className="p-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-800">
                                <span className="text-slate-500 dark:text-slate-400 block text-[11px]">Tổng tiền hóa đơn</span>
                                <strong className="text-emerald-600 dark:text-emerald-400 font-bold text-sm">
                                    {bill.amount.toLocaleString('vi-VN')} ₫
                                </strong>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* OPTIONAL FORECAST CARD */}
            {forecast?.next_period_consumption !== null && forecast?.next_period_consumption !== undefined && (
                <div className="p-3 rounded-xl bg-gradient-to-r from-purple-500/10 via-indigo-500/10 to-blue-500/10 border border-purple-200/60 dark:border-purple-800/60 flex items-center justify-between gap-3">
                    <div className="flex items-center gap-2.5">
                        <div className="p-2 rounded-lg bg-purple-600 text-white shrink-0 shadow-xs">
                            <Sparkles size={16} />
                        </div>
                        <div>
                            <span className="text-xs font-bold text-purple-900 dark:text-purple-200 block">Dự báo kỳ tiếp theo</span>
                            <p className="text-[11px] text-slate-500 dark:text-slate-400">
                                Độ tin cậy: <span className="font-medium text-purple-700 dark:text-purple-300">{forecast.confidence || 'Vừa'}</span>
                            </p>
                        </div>
                    </div>

                    <div className="text-right">
                        <strong className="text-sm font-bold text-purple-900 dark:text-purple-100 block">
                            ~{forecast.next_period_consumption} {unitStr}
                        </strong>
                        {forecast.estimated_amount && (
                            <span className="text-xs font-semibold text-emerald-600 dark:text-emerald-400">
                                ≈ {forecast.estimated_amount.toLocaleString('vi-VN')} ₫
                            </span>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}
