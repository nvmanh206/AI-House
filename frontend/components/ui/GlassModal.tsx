'use client';

import React, { ReactNode } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X } from 'lucide-react';
import { GlassCard } from './GlassCard';

export interface GlassModalProps {
    isOpen: boolean;
    onClose: () => void;
    title?: string;
    children: ReactNode;
    maxWidth?: 'sm' | 'md' | 'lg' | 'xl';
}

export function GlassModal({
    isOpen,
    onClose,
    title,
    children,
    maxWidth = 'md',
}: GlassModalProps) {
    const maxWidthStyles = {
        sm: 'max-w-sm',
        md: 'max-w-md',
        lg: 'max-w-lg',
        xl: 'max-w-xl',
    };

    return (
        <AnimatePresence>
            {isOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                    {/* Backdrop */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                        className="fixed inset-0 bg-slate-900/30 backdrop-blur-md"
                    />

                    {/* Modal Content */}
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95, y: 15 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: 15 }}
                        transition={{ duration: 0.25, ease: 'easeOut' }}
                        className={`w-full z-10 ${maxWidthStyles[maxWidth]}`}
                    >
                        <GlassCard depth={3} hover={false} className="p-6">
                            {title && (
                                <div className="flex items-center justify-between pb-4 mb-4 border-b border-white/40">
                                    <h3 className="text-base font-bold text-slate-900">{title}</h3>
                                    <button
                                        onClick={onClose}
                                        className="w-8 h-8 rounded-full bg-slate-100/80 hover:bg-slate-200 text-slate-500 flex items-center justify-center transition-colors cursor-pointer"
                                    >
                                        <X size={16} />
                                    </button>
                                </div>
                            )}
                            {children}
                        </GlassCard>
                    </motion.div>
                </div>
            )}
        </AnimatePresence>
    );
}

export interface GlassDrawerProps {
    isOpen: boolean;
    onClose: () => void;
    title?: string;
    children: ReactNode;
}

export function GlassDrawer({
    isOpen,
    onClose,
    title,
    children,
}: GlassDrawerProps) {
    return (
        <AnimatePresence>
            {isOpen && (
                <div className="fixed inset-0 z-50 flex justify-end">
                    {/* Backdrop */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                        className="fixed inset-0 bg-slate-900/30 backdrop-blur-md"
                    />

                    {/* Drawer Content */}
                    <motion.div
                        initial={{ x: '100%' }}
                        animate={{ x: 0 }}
                        exit={{ x: '100%' }}
                        transition={{ duration: 0.3, ease: 'easeOut' }}
                        className="w-full max-w-md h-full z-10 p-4"
                    >
                        <GlassCard depth={3} hover={false} className="h-full p-6 overflow-y-auto flex flex-col">
                            <div className="flex items-center justify-between pb-4 mb-4 border-b border-white/40">
                                {title && <h3 className="text-base font-bold text-slate-900">{title}</h3>}
                                <button
                                    onClick={onClose}
                                    className="w-8 h-8 rounded-full bg-slate-100/80 hover:bg-slate-200 text-slate-500 flex items-center justify-center transition-colors cursor-pointer ml-auto"
                                >
                                    <X size={16} />
                                </button>
                            </div>
                            <div className="flex-1">{children}</div>
                        </GlassCard>
                    </motion.div>
                </div>
            )}
        </AnimatePresence>
    );
}
