'use client';

import React, { ReactNode } from 'react';
import Link from 'next/link';
import { House, Sparkles, Zap, Droplets, ShieldCheck, Star } from 'lucide-react';
import { AppBackground } from './AppBackground';
import { GlassCard } from '../ui/GlassCard';

export interface AuthLayoutProps {
    children: ReactNode;
    title: string;
    subtitle: string;
    isRegister?: boolean;
}

export function AuthLayout({
    children,
    title,
    subtitle,
    isRegister = false,
}: AuthLayoutProps) {
    return (
        <div className="min-h-screen w-full relative flex flex-col justify-between overflow-x-hidden p-4 sm:p-6 lg:p-8">
            <AppBackground />

            {/* TOP AUTH HEADER LOGO */}
            <header className="w-full max-w-7xl mx-auto flex items-center justify-between py-2 mb-4">
                <Link className="flex items-center gap-3 text-decoration-none group" href="/">
                    <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-emerald-500 via-teal-500 to-cyan-500 shadow-md shadow-emerald-500/20 flex items-center justify-center text-white relative group-hover:scale-105 transition-transform border border-white/40">
                        <House size={20} className="fill-white/20" />
                        <span className="absolute -top-1 -right-1 w-3.5 h-3.5 bg-yellow-400 rounded-full flex items-center justify-center text-[7px] font-black text-slate-900">
                            <Sparkles size={7} />
                        </span>
                    </div>
                    <div className="flex flex-col">
                        <div className="flex items-baseline">
                            <span className="text-xl font-black tracking-tight bg-gradient-to-r from-emerald-600 via-teal-600 to-cyan-600 bg-clip-text text-transparent">
                                nhà mình
                            </span>
                            <span className="text-emerald-500 font-extrabold text-xl leading-none">.</span>
                        </div>
                        <span className="text-[10px] text-slate-400 font-semibold tracking-wider uppercase -mt-1">
                            Tiện ích thông minh · Sống xanh
                        </span>
                    </div>
                </Link>

                <div className="flex items-center gap-2">
                    <span className="text-xs text-slate-500 hidden sm:inline-block font-medium">
                        {isRegister ? 'Đã có tài khoản?' : 'Chưa có tài khoản?'}
                    </span>
                    <Link
                        href={isRegister ? '/login' : '/register'}
                        className="px-4 py-2 rounded-2xl bg-white/40 backdrop-blur-xl border border-white/60 text-xs font-bold text-slate-700 hover:bg-white/60 transition-all text-decoration-none shadow-sm"
                    >
                        {isRegister ? 'Đăng nhập' : 'Đăng ký ngay'}
                    </Link>
                </div>
            </header>

            {/* MAIN AUTH CONTAINER SPLIT */}
            <main className="w-full max-w-7xl mx-auto flex-1 flex items-center justify-center py-6">
                <div className="w-full grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
                    {/* LEFT BRAND PROMO PANEL (DESKTOP) */}
                    <div className="hidden lg:flex lg:col-span-6 flex-col justify-center space-y-6 pr-4">
                        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-700 text-xs font-bold w-fit">
                            <Sparkles size={14} className="text-emerald-600" />
                            <span>Quản lý hóa đơn thông minh cùng AI</span>
                        </div>

                        <h1 className="text-3xl xl:text-4xl font-black text-slate-900 tracking-tight leading-tight">
                            Kiểm soát chi tiêu.<br />
                            <span className="bg-gradient-to-r from-emerald-600 via-teal-600 to-cyan-600 bg-clip-text text-transparent">
                                Chăm sóc tổ ấm thông minh.
                            </span>
                        </h1>

                        <p className="text-sm font-medium text-slate-600 leading-relaxed max-w-lg">
                            Ứng dụng giúp bạn tự động hóa việc theo dõi tiền điện, nước, nhận cảnh báo hóa đơn bất thường và tối ưu hóa ngân sách gia đình bằng trí tuệ nhân tạo.
                        </p>

                        {/* 3 GLASS HIGHLIGHT CARDS */}
                        <div className="grid grid-cols-2 gap-4 pt-2">
                            <GlassCard depth={1} hover={false} className="p-4">
                                <div className="w-8 h-8 rounded-xl bg-amber-500/15 text-amber-600 flex items-center justify-center mb-2">
                                    <Zap size={18} />
                                </div>
                                <h4 className="text-xs font-bold text-slate-900">Theo dõi Điện & Nước</h4>
                                <p className="text-[11px] text-slate-500 mt-0.5">Biểu đồ sinh hoạt trực quan</p>
                            </GlassCard>

                            <GlassCard depth={1} hover={false} className="p-4">
                                <div className="w-8 h-8 rounded-xl bg-violet-500/15 text-violet-600 flex items-center justify-center mb-2">
                                    <Sparkles size={18} />
                                </div>
                                <h4 className="text-xs font-bold text-slate-900">Phân tích AI Pro</h4>
                                <p className="text-[11px] text-slate-500 mt-0.5">Gợi ý tiết kiệm đến 20%</p>
                            </GlassCard>
                        </div>

                        <div className="flex items-center gap-3 pt-2 text-xs font-semibold text-slate-600">
                            <div className="flex -space-x-2">
                                {['A', 'B', 'C', 'D'].map((letter, i) => (
                                    <div
                                        key={i}
                                        className="w-7 h-7 rounded-full bg-gradient-to-tr from-emerald-400 to-cyan-500 text-white text-[10px] font-bold flex items-center justify-center border-2 border-white"
                                    >
                                        {letter}
                                    </div>
                                ))}
                            </div>
                            <div className="flex items-center gap-1">
                                <div className="flex text-amber-400">
                                    {[...Array(5)].map((_, i) => (
                                        <Star key={i} size={13} fill="currentColor" />
                                    ))}
                                </div>
                                <span className="font-bold text-slate-900">4.9/5</span> từ hơn 10.000+ gia đình
                            </div>
                        </div>
                    </div>

                    {/* RIGHT AUTH FORM CARD */}
                    <div className="lg:col-span-6 w-full max-w-md mx-auto">
                        <GlassCard depth={3} hover={false} className="p-6 sm:p-8">
                            <div className="mb-6">
                                <h2 className="text-xl sm:text-2xl font-black text-slate-900 tracking-tight">
                                    {title}
                                </h2>
                                <p className="text-xs sm:text-sm font-medium text-slate-500 mt-1">
                                    {subtitle}
                                </p>
                            </div>

                            {children}
                        </GlassCard>
                    </div>
                </div>
            </main>

            {/* AUTH FOOTER */}
            <footer className="w-full max-w-7xl mx-auto text-center py-3 text-xs text-slate-400 font-medium">
                © 2026 nhà mình. Bảo mật & Mã hóa dữ liệu chuẩn Enterprise.
            </footer>
        </div>
    );
}
