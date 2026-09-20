'use client';

import React, { ReactNode } from 'react';
import { motion, HTMLMotionProps } from 'framer-motion';

export interface GlassCardProps extends Omit<HTMLMotionProps<'div'>, 'children'> {
    children: ReactNode;
    depth?: 1 | 2 | 3;
    hover?: boolean;
    className?: string;
    glow?: 'none' | 'emerald' | 'cyan' | 'amber' | 'violet' | 'rose';
}

export function GlassCard({
    children,
    depth = 2,
    hover = true,
    className = '',
    glow = 'none',
    ...props
}: GlassCardProps) {
    const depthStyles = {
        1: 'bg-white/25 border-white/30 shadow-[0_10px_30px_rgba(15,23,42,0.04)]',
        2: 'bg-white/35 border-white/40 shadow-[0_18px_50px_rgba(15,23,42,0.08)]',
        3: 'bg-white/50 border-white/60 shadow-[0_24px_60px_rgba(15,23,42,0.12)]',
    };

    const glowStyles = {
        none: '',
        emerald: 'shadow-emerald-500/10 border-emerald-400/30',
        cyan: 'shadow-cyan-500/10 border-cyan-400/30',
        amber: 'shadow-amber-500/10 border-amber-400/30',
        violet: 'shadow-violet-500/10 border-violet-400/30',
        rose: 'shadow-rose-500/10 border-rose-400/30',
    };

    return (
        <motion.div
            whileHover={hover ? { y: -3, scale: 1.005 } : undefined}
            transition={{ duration: 0.25, ease: 'easeOut' }}
            className={`
                rounded-3xl
                backdrop-blur-2xl
                border
                transition-all
                duration-300
                relative
                overflow-hidden
                ${depthStyles[depth]}
                ${glowStyles[glow]}
                ${hover ? 'hover:bg-white/45 hover:border-white/70 hover:shadow-[0_24px_70px_rgba(15,23,42,0.12)]' : ''}
                ${className}
            `}
            {...props}
        >
            {children}
        </motion.div>
    );
}
