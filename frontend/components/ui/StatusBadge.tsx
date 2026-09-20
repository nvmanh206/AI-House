'use client';

import React from 'react';

export interface StatusBadgeProps {
    status: string;
    className?: string;
}

const statusConfig: Record<string, { label: string; style: string; dot: string }> = {
    PAID: {
        label: 'Đã thanh toán',
        style: 'bg-emerald-500/15 text-emerald-700 border-emerald-500/30',
        dot: 'bg-emerald-500 shadow-[0_0_8px_#10b981]',
    },
    UNPAID: {
        label: 'Chưa thanh toán',
        style: 'bg-amber-500/15 text-amber-700 border-amber-500/30',
        dot: 'bg-amber-500 shadow-[0_0_8px_#f59e0b]',
    },
    OVERDUE: {
        label: 'Quá hạn',
        style: 'bg-rose-500/15 text-rose-700 border-rose-500/30 animate-pulse',
        dot: 'bg-rose-500 shadow-[0_0_8px_#f43f5e]',
    },
    PENDING: {
        label: 'Đang xử lý',
        style: 'bg-blue-500/15 text-blue-700 border-blue-500/30',
        dot: 'bg-blue-500 shadow-[0_0_8px_#3b82f6]',
    },
    DRAFT: {
        label: 'Bản nháp',
        style: 'bg-slate-500/15 text-slate-700 border-slate-500/30',
        dot: 'bg-slate-500',
    },
    CANCELLED: {
        label: 'Đã hủy',
        style: 'bg-slate-400/15 text-slate-500 border-slate-400/30',
        dot: 'bg-slate-400',
    },
    AI: {
        label: 'Phân tích AI',
        style: 'bg-violet-500/15 text-violet-700 border-violet-500/30',
        dot: 'bg-violet-500 shadow-[0_0_8px_#8b5cf6]',
    },
};

export function StatusBadge({ status, className = '' }: StatusBadgeProps) {
    const config = statusConfig[status] || {
        label: status,
        style: 'bg-slate-500/10 text-slate-700 border-slate-500/20',
        dot: 'bg-slate-400',
    };

    return (
        <span
            className={`
                inline-flex
                items-center
                gap-1.5
                px-2.5
                py-1
                rounded-full
                border
                backdrop-blur-md
                text-[11px]
                font-bold
                leading-none
                ${config.style}
                ${className}
            `}
        >
            <span className={`w-1.5 h-1.5 rounded-full ${config.dot}`} />
            {config.label}
        </span>
    );
}
