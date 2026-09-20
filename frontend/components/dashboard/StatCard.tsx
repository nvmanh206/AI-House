'use client';
import { ReactNode } from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { ChevronRight } from 'lucide-react';
import { useCountUp } from './useCountUp';

interface StatCardProps {
  title: string;
  value: number;
  formattedValue?: string;
  suffix?: string;
  unit?: string;
  trendText?: string;
  trendDirection?: 'up' | 'down' | 'neutral';
  secondaryInfo?: string;
  linkHref?: string;
  icon: ReactNode;
  accentColor: 'blue' | 'amber' | 'cyan' | 'orange' | 'emerald' | 'purple';
  tagBadge?: string;
}

const accentStyles = {
  blue: {
    bgIcon: 'bg-blue-50 text-blue-600 border-blue-100',
    badge: 'bg-blue-50 text-blue-700 border-blue-200/60',
    ring: 'hover:border-blue-300/60'
  },
  amber: {
    bgIcon: 'bg-amber-50 text-amber-600 border-amber-100',
    badge: 'bg-amber-50 text-amber-700 border-amber-200/60',
    ring: 'hover:border-amber-300/60'
  },
  cyan: {
    bgIcon: 'bg-sky-50 text-sky-600 border-sky-100',
    badge: 'bg-emerald-50 text-emerald-700 border-emerald-200/60',
    ring: 'hover:border-sky-300/60'
  },
  orange: {
    bgIcon: 'bg-orange-50 text-orange-600 border-orange-100',
    badge: 'bg-orange-50 text-orange-700 border-orange-200/60',
    ring: 'hover:border-orange-300/60'
  },
  emerald: {
    bgIcon: 'bg-emerald-50 text-emerald-600 border-emerald-100',
    badge: 'bg-emerald-50 text-emerald-700 border-emerald-200/60',
    ring: 'hover:border-emerald-300/60'
  },
  purple: {
    bgIcon: 'bg-purple-50 text-purple-600 border-purple-100',
    badge: 'bg-purple-50 text-purple-700 border-purple-200/60',
    ring: 'hover:border-purple-300/60'
  }
};

export function StatCard({
  title,
  value,
  formattedValue,
  suffix = ' ₫',
  unit,
  trendText,
  trendDirection = 'up',
  secondaryInfo,
  linkHref = '#',
  icon,
  accentColor,
  tagBadge
}: StatCardProps) {
  const animatedNumber = useCountUp(value, 1000);
  const accent = accentStyles[accentColor];

  // Display value
  const displayVal = formattedValue
    ? formattedValue
    : animatedNumber.toLocaleString('vi-VN') + suffix;

  return (
    <motion.div
      whileHover={{ y: -3 }}
      transition={{ duration: 0.25, ease: [0.22, 1, 0.36, 1] }}
      className={`
        relative overflow-hidden rounded-3xl border border-slate-200/70
        bg-white/85 p-5 backdrop-blur-xl shadow-[0_10px_30px_rgba(15,23,42,0.03)]
        transition-all duration-300 hover:shadow-lg ${accent.ring}
      `}
    >
      {/* Top Header Row */}
      <div className="flex items-center justify-between mb-3">
        <div className={`flex h-11 w-11 items-center justify-center rounded-2xl border ${accent.bgIcon} shadow-xs`}>
          {icon}
        </div>
        {linkHref && (
          <Link
            href={linkHref}
            className="flex h-7 w-7 items-center justify-center rounded-full text-slate-400 hover:bg-slate-100 hover:text-slate-700 transition-colors"
            aria-label={`Chi tiết ${title}`}
          >
            <ChevronRight className="h-4 w-4" />
          </Link>
        )}
      </div>

      {/* Label */}
      <span className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
        {title}
      </span>

      {/* Value */}
      <div className="flex items-baseline gap-1 mb-3">
        <span className="text-2xl font-extrabold tracking-tight text-slate-900">
          {displayVal}
        </span>
        {unit && <span className="text-xs font-medium text-slate-500">{unit}</span>}
      </div>

      {/* Footer Info / Trends */}
      <div className="flex flex-wrap items-center gap-2 text-xs font-medium">
        {trendText && (
          <span className={`inline-flex items-center gap-1 rounded-lg border px-2 py-0.5 font-semibold ${accent.badge}`}>
            {trendDirection === 'up' && '↗'}
            {trendDirection === 'down' && '↘'}
            {trendText}
          </span>
        )}
        {secondaryInfo && (
          <span className="text-slate-600">
            {secondaryInfo}
          </span>
        )}
        {tagBadge && (
          <span className="ml-auto rounded-md bg-purple-100 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-purple-700">
            {tagBadge}
          </span>
        )}
      </div>
    </motion.div>
  );
}
