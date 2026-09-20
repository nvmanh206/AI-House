'use client';

import React from 'react';

export function AppBackground() {
    return (
        <div className="fixed inset-0 -z-20 overflow-hidden pointer-events-none select-none">
            {/* Base Sky Light Blue Architectural Background */}
            <div className="absolute inset-0 bg-gradient-to-br from-[#e0f2fe] via-[#eef2ff] to-[#e0f2fe]" />

            {/* Architectural Interior / Exterior Glass Backdrop Bloom Effect */}
            <div
                className="absolute inset-0 opacity-25 mix-blend-overlay bg-cover bg-center"
                style={{
                    backgroundImage: `radial-gradient(ellipse at 50% 30%, rgba(255,255,255,0.9), rgba(186,230,253,0.3) 60%, rgba(147,197,253,0.2) 100%)`,
                }}
            />

            {/* Ambient Blurred Glass Lighting Blobs */}
            <div className="absolute -top-[15%] -left-[10%] w-[60%] h-[60%] rounded-full bg-sky-300/30 blur-[140px]" />
            <div className="absolute top-[10%] right-[-5%] w-[50%] h-[50%] rounded-full bg-blue-400/25 blur-[140px]" />
            <div className="absolute bottom-[-10%] left-[15%] w-[55%] h-[55%] rounded-full bg-teal-300/20 blur-[140px]" />
            <div className="absolute top-[45%] left-[35%] w-[40%] h-[40%] rounded-full bg-indigo-300/15 blur-[130px]" />

            {/* Subtle Architectural Smart Home Grid */}
            <div
                className="absolute inset-0 opacity-[0.03]"
                style={{
                    backgroundImage: `radial-gradient(#0284c7 1.5px, transparent 1.5px)`,
                    backgroundSize: '28px 28px',
                }}
            />

            {/* Floating Soft Ambient Eco Leaves */}
            <svg
                className="absolute top-[12%] left-[6%] w-7 h-7 text-sky-500/30 animate-bounce duration-[8000ms]"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.5"
            >
                <path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.4 19 2c1 2 2 4.1 2 7 0 6-4.5 11-10 11Z" />
                <path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12" />
            </svg>
            <svg
                className="absolute top-[65%] right-[5%] w-9 h-9 text-blue-500/30 animate-pulse duration-[10000ms]"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.5"
            >
                <path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.4 19 2c1 2 2 4.1 2 7 0 6-4.5 11-10 11Z" />
            </svg>
            <svg
                className="absolute bottom-[10%] left-[22%] w-8 h-8 text-teal-500/30 animate-bounce duration-[9000ms]"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.5"
            >
                <path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.4 19 2c1 2 2 4.1 2 7 0 6-4.5 11-10 11Z" />
            </svg>
        </div>
    );
}
