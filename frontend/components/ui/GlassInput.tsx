'use client';

import React, { InputHTMLAttributes, SelectHTMLAttributes, ReactNode } from 'react';

export interface GlassInputProps extends InputHTMLAttributes<HTMLInputElement> {
    label?: string;
    icon?: ReactNode;
    error?: string;
    help?: string;
}

export function GlassInput({
    label,
    icon,
    error,
    help,
    className = '',
    id,
    name,
    ...props
}: GlassInputProps) {
    const inputId = id || name;

    return (
        <div className="flex flex-col gap-1.5 w-full">
            {label && (
                <label htmlFor={inputId} className="text-xs font-bold text-slate-700">
                    {label}
                </label>
            )}
            <div className="relative flex items-center">
                {icon && (
                    <div className="absolute left-3.5 text-slate-400 pointer-events-none flex items-center justify-center">
                        {icon}
                    </div>
                )}
                <input
                    id={inputId}
                    name={name}
                    className={`
                        w-full
                        px-4
                        py-2.5
                        ${icon ? 'pl-10' : ''}
                        rounded-2xl
                        bg-white/30
                        backdrop-blur-xl
                        border
                        ${error ? 'border-rose-400/80 focus:ring-rose-500/20' : 'border-white/50 focus:border-emerald-500/60 focus:ring-emerald-500/20'}
                        text-xs
                        font-medium
                        text-slate-900
                        placeholder:text-slate-400
                        shadow-inner
                        transition-all
                        duration-200
                        outline-none
                        focus:ring-4
                        focus:bg-white/50
                        ${className}
                    `}
                    {...props}
                />
            </div>
            {error && <p className="text-[11px] font-semibold text-rose-500">{error}</p>}
            {help && !error && <p className="text-[11px] font-medium text-slate-400">{help}</p>}
        </div>
    );
}

export interface GlassSelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
    label?: string;
    icon?: ReactNode;
    error?: string;
    help?: string;
    children: ReactNode;
}

export function GlassSelect({
    label,
    icon,
    error,
    help,
    children,
    className = '',
    id,
    name,
    ...props
}: GlassSelectProps) {
    const selectId = id || name;

    return (
        <div className="flex flex-col gap-1.5 w-full">
            {label && (
                <label htmlFor={selectId} className="text-xs font-bold text-slate-700">
                    {label}
                </label>
            )}
            <div className="relative flex items-center">
                {icon && (
                    <div className="absolute left-3.5 text-slate-400 pointer-events-none flex items-center justify-center">
                        {icon}
                    </div>
                )}
                <select
                    id={selectId}
                    name={name}
                    className={`
                        w-full
                        px-4
                        py-2.5
                        ${icon ? 'pl-10' : ''}
                        rounded-2xl
                        bg-white/40
                        backdrop-blur-xl
                        border
                        ${error ? 'border-rose-400/80 focus:ring-rose-500/20' : 'border-white/50 focus:border-emerald-500/60 focus:ring-emerald-500/20'}
                        text-xs
                        font-medium
                        text-slate-900
                        shadow-inner
                        transition-all
                        duration-200
                        outline-none
                        focus:ring-4
                        focus:bg-white/60
                        appearance-none
                        cursor-pointer
                        ${className}
                    `}
                    {...props}
                >
                    {children}
                </select>
                <div className="absolute right-3.5 pointer-events-none text-slate-400">
                    ▼
                </div>
            </div>
            {error && <p className="text-[11px] font-semibold text-rose-500">{error}</p>}
            {help && !error && <p className="text-[11px] font-medium text-slate-400">{help}</p>}
        </div>
    );
}
