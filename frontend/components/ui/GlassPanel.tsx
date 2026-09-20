'use client';

import React, { ReactNode } from 'react';
import { GlassCard, GlassCardProps } from './GlassCard';

export interface GlassPanelProps extends GlassCardProps {
    title?: string;
    subtitle?: string;
    icon?: ReactNode;
    action?: ReactNode;
}

export function GlassPanel({
    title,
    subtitle,
    icon,
    action,
    children,
    className = '',
    ...props
}: GlassPanelProps) {
    return (
        <GlassCard className={`p-6 ${className}`} {...props}>
            {(title || action) && (
                <div className="flex items-center justify-between gap-4 mb-5 pb-4 border-b border-white/30">
                    <div className="flex items-center gap-3">
                        {icon && (
                            <div className="w-9 h-9 rounded-2xl bg-gradient-to-tr from-emerald-500/20 to-teal-500/10 text-emerald-600 border border-emerald-500/20 flex items-center justify-center">
                                {icon}
                            </div>
                        )}
                        <div>
                            {title && <h3 className="text-base font-bold text-slate-900 leading-tight">{title}</h3>}
                            {subtitle && <p className="text-xs text-slate-500 font-medium mt-0.5">{subtitle}</p>}
                        </div>
                    </div>
                    {action && <div>{action}</div>}
                </div>
            )}
            {children}
        </GlassCard>
    );
}
