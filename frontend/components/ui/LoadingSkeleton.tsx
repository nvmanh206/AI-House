'use client';

import React from 'react';
import { GlassCard } from './GlassCard';

export function LoadingSkeleton({ className = '' }: { className?: string }) {
    return (
        <div className={`animate-pulse bg-white/40 backdrop-blur-xl rounded-2xl border border-white/40 ${className}`} />
    );
}

export function SkeletonGrid() {
    return (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <GlassCard depth={1} hover={false} className="p-6 h-32 animate-pulse bg-white/30"><div /></GlassCard>
            <GlassCard depth={1} hover={false} className="p-6 h-32 animate-pulse bg-white/30"><div /></GlassCard>
            <GlassCard depth={1} hover={false} className="p-6 h-32 animate-pulse bg-white/30"><div /></GlassCard>
        </div>
    );
}
