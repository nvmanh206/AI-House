'use client';

import React, { ReactNode } from 'react';
import Link from 'next/link';
import { ReceiptText } from 'lucide-react';
import { GlassCard } from './GlassCard';

export interface EmptyStateProps {
    title?: string;
    description?: string;
    icon?: ReactNode;
    actionLabel?: string;
    actionHref?: string;
    onAction?: () => void;
    className?: string;
}

export function EmptyState({
    title = 'Chưa có dữ liệu',
    description = 'Không tìm thấy dữ liệu phù hợp.',
    icon = <ReceiptText size={32} className="text-slate-400" />,
    actionLabel,
    actionHref,
    onAction,
    className = '',
}: EmptyStateProps) {
    return (
        <GlassCard depth={1} hover={false} className={`p-8 text-center flex flex-col items-center justify-center ${className}`}>
            <div className="w-16 h-16 rounded-3xl bg-slate-100/80 backdrop-blur-md border border-slate-200/60 flex items-center justify-center mb-3 shadow-inner">
                {icon}
            </div>
            <h3 className="text-sm font-bold text-slate-900 mb-1">{title}</h3>
            <p className="text-xs text-slate-500 max-w-sm mb-4 leading-relaxed">{description}</p>
            {actionLabel && actionHref && (
                <Link
                    href={actionHref}
                    className="px-4 py-2 rounded-2xl bg-gradient-to-r from-emerald-500 to-teal-500 text-white text-xs font-bold shadow-md shadow-emerald-500/20 hover:scale-105 transition-all text-decoration-none"
                >
                    {actionLabel}
                </Link>
            )}
            {actionLabel && onAction && !actionHref && (
                <button
                    onClick={onAction}
                    className="px-4 py-2 rounded-2xl bg-gradient-to-r from-emerald-500 to-teal-500 text-white text-xs font-bold shadow-md shadow-emerald-500/20 hover:scale-105 transition-all cursor-pointer"
                >
                    {actionLabel}
                </button>
            )}
        </GlassCard>
    );
}
