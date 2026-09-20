'use client';

import React, { ReactNode } from 'react';
import { motion, HTMLMotionProps } from 'framer-motion';

export interface ButtonProps extends Omit<HTMLMotionProps<'button'>, 'children'> {
    children: ReactNode;
    variant?: 'primary' | 'secondary' | 'glass' | 'danger' | 'success';
    size?: 'sm' | 'md' | 'lg';
    icon?: ReactNode;
    isLoading?: boolean;
    className?: string;
}

export function PrimaryButton({
    children,
    variant = 'primary',
    size = 'md',
    icon,
    isLoading = false,
    className = '',
    disabled,
    ...props
}: ButtonProps) {
    const sizeStyles = {
        sm: 'px-3.5 py-1.5 text-xs rounded-xl font-bold gap-1.5',
        md: 'px-5 py-2.5 text-xs rounded-2xl font-bold gap-2',
        lg: 'px-6 py-3.5 text-sm rounded-2xl font-extrabold gap-2.5',
    };

    const variantStyles = {
        primary: 'bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-500 text-white shadow-lg shadow-emerald-500/25 border border-white/20 hover:shadow-emerald-500/35',
        secondary: 'bg-white/40 backdrop-blur-xl text-slate-800 border border-white/60 hover:bg-white/60 shadow-sm',
        glass: 'bg-white/20 backdrop-blur-lg text-slate-700 border border-white/40 hover:bg-white/35 shadow-sm',
        danger: 'bg-gradient-to-r from-rose-500 to-red-600 text-white shadow-lg shadow-rose-500/25 border border-white/20 hover:shadow-rose-500/35',
        success: 'bg-gradient-to-r from-emerald-600 to-teal-600 text-white shadow-lg shadow-emerald-600/25 border border-white/20',
    };

    return (
        <motion.button
            whileHover={!disabled && !isLoading ? { scale: 1.02, y: -1 } : undefined}
            whileTap={!disabled && !isLoading ? { scale: 0.98 } : undefined}
            transition={{ duration: 0.15 }}
            disabled={disabled || isLoading}
            className={`
                inline-flex
                items-center
                justify-center
                transition-all
                duration-200
                cursor-pointer
                disabled:opacity-50
                disabled:cursor-not-allowed
                disabled:transform-none
                ${sizeStyles[size]}
                ${variantStyles[variant]}
                ${className}
            `}
            {...props}
        >
            {isLoading ? (
                <span className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" />
            ) : icon ? (
                <span className="flex items-center justify-center">{icon}</span>
            ) : null}
            <span>{children}</span>
        </motion.button>
    );
}

export function SecondaryButton(props: ButtonProps) {
    return <PrimaryButton variant="secondary" {...props} />;
}
