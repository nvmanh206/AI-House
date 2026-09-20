'use client';
import { motion } from 'framer-motion';

export function DashboardBackground() {
  return (
    <div className="pointer-events-none fixed inset-0 -z-10 overflow-hidden select-none">
      {/* Top Left Emerald Glow Blob */}
      <motion.div
        animate={{
          scale: [1, 1.1, 1],
          x: [0, 30, 0],
          y: [0, -20, 0]
        }}
        transition={{ duration: 18, repeat: Infinity, ease: 'easeInOut' }}
        className="absolute -top-32 -left-20 h-[500px] w-[500px] rounded-full bg-emerald-200/40 blur-[100px]"
      />

      {/* Bottom Right Sky/Blue Glow Blob */}
      <motion.div
        animate={{
          scale: [1, 1.15, 1],
          x: [0, -40, 0],
          y: [0, 30, 0]
        }}
        transition={{ duration: 22, repeat: Infinity, ease: 'easeInOut' }}
        className="absolute -bottom-36 -right-20 h-[600px] w-[600px] rounded-full bg-sky-200/50 blur-[120px]"
      />

      {/* Center Soft Indigo Glow Blob */}
      <motion.div
        animate={{
          scale: [1, 1.08, 1],
          x: [0, 20, 0],
          y: [0, 20, 0]
        }}
        transition={{ duration: 15, repeat: Infinity, ease: 'easeInOut' }}
        className="absolute top-1/3 right-1/4 h-[400px] w-[400px] rounded-full bg-indigo-200/30 blur-[90px]"
      />

      {/* Subtle Floating Eco Leaf SVGs */}
      <motion.svg
        animate={{ y: [0, -14, 0], rotate: [0, 10, 0] }}
        transition={{ duration: 8, repeat: Infinity, ease: 'easeInOut' }}
        className="absolute top-20 left-16 h-7 w-7 text-emerald-500/20"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.5"
      >
        <path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.4 19 2c1 2 2 4.1 2 7 0 6-4.5 11-10 11Z" />
        <path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12" />
      </motion.svg>

      <motion.svg
        animate={{ y: [0, -18, 0], rotate: [0, -12, 0] }}
        transition={{ duration: 10, repeat: Infinity, ease: 'easeInOut', delay: 2 }}
        className="absolute top-2/3 right-12 h-9 w-9 text-sky-500/20"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.5"
      >
        <path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.4 19 2c1 2 2 4.1 2 7 0 6-4.5 11-10 11Z" />
      </motion.svg>
    </div>
  );
}
