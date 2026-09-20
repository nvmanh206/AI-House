'use client';

import React, { ReactNode } from 'react';
import { GlassCard } from './GlassCard';

export interface PageHeaderProps {
    title: string;
    description?: string;
    icon?: ReactNode;
    actions?: ReactNode;
    className?: string;
}

export function PageHeader({
    title,
    description,
    icon,
    actions,
    className = '',
}: PageHeaderProps) {
    return (
        <GlassCard depth={2} hover={false} className={`p-6 mb-6 ${className}`}>
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="flex items-center gap-4">
                    {icon && (
                        <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-emerald-500 via-teal-500 to-cyan-500 text-white flex items-center justify-center shadow-lg shadow-emerald-500/20 border border-white/40 shrink-0">
                            {icon}
                        </div>
                    )}
                    <div>
                        <h1 className="text-xl sm:text-2xl font-black text-slate-900 tracking-tight leading-tight">
                            {title}
                        </h1>
                        {description && (
                            <p className="text-xs sm:text-sm font-medium text-slate-500 mt-1">
                                {description}
                            </p>
                        )}
                    </div>
                </div>
                {actions && <div className="flex items-center gap-3 shrink-0">{actions}</div>}
            </div>
        </GlassCard>
    );
}
