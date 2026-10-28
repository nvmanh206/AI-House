'use client';

import React, { ReactNode, useState } from 'react';
import Link from 'next/link';
import {
    House,
    LayoutDashboard,
    Gauge,
    ReceiptText,
    ChartNoAxesCombined,
    Sparkles,
    Bell,
    Settings,
    Zap,
    ShieldCheck,
    LogOut,
    Menu,
    ChevronRight,
    CalendarDays,
    Search,
    Leaf,
    ArrowRight,
    X,
} from 'lucide-react';
import { AppBackground } from './AppBackground';

export interface AppLayoutProps {
    children: ReactNode;
    user: any;
    screen: string;
    notifications: any[];
    unreadCount: number;
    onLogout: () => void;
    title?: string;
}

interface NavItem {
    href: string;
    label: string;
    icon: any;
    isAI?: boolean;
    hasBadge?: boolean;
}

const navItems: NavItem[] = [
    { href: 'dashboard', label: 'Tổng quan', icon: LayoutDashboard },
    { href: 'readings', label: 'Nhập chỉ số', icon: Gauge },
    { href: 'bills', label: 'Hóa đơn', icon: ReceiptText },
    { href: 'statistics', label: 'Thống kê', icon: ChartNoAxesCombined },
    { href: 'assistant', label: 'Trợ lý AI', icon: Sparkles, isAI: true },
    { href: 'household', label: 'Hộ gia đình', icon: House },
    { href: 'meters', label: 'Công tơ', icon: Zap },
    { href: 'notifications', label: 'Thông báo', icon: Bell, hasBadge: true },
];

const titlesMap: Record<string, string> = {
    dashboard: 'Tổng quan chi tiêu gia đình',
    household: 'Quản lý hộ gia đình',
    'household/members': 'Thành viên gia đình',
    meters: 'Quản lý công tơ điện nước',
    readings: 'Nhập chỉ số điện nước',
    bills: 'Quản lý hóa đơn tiện ích',
    statistics: 'Phân tích & Thống kê chi phí',
    notifications: 'Trung tâm thông báo',
    assistant: 'Trợ lý AI nhà mình',
    settings: 'Cài đặt tài khoản & ứng dụng',
    admin: 'Quản trị hệ thống',
};

export function AppLayout({
    children,
    user,
    screen,
    notifications,
    unreadCount,
    onLogout,
    title,
}: AppLayoutProps) {
    const [mobileOpen, setMobileOpen] = useState(false);
    const [todayLabel, setTodayLabel] = useState('');
    React.useEffect(() => {
        const updateDate = () => setTodayLabel(new Intl.DateTimeFormat('vi-VN', {
            dateStyle: 'full', timeZone: 'Asia/Ho_Chi_Minh',
        }).format(new Date()));
        updateDate();
        const timer = window.setInterval(updateDate, 60_000);
        return () => window.clearInterval(timer);
    }, []);
    const mainScrollRef = React.useRef<HTMLDivElement>(null);
    const displayTitle = title || titlesMap[screen] || 'Trang ứng dụng';

    // Lock body scroll on mobile drawer open & handle Escape key
    React.useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if (e.key === 'Escape') setMobileOpen(false);
        };
        if (mobileOpen) {
            document.body.style.overflow = 'hidden';
            window.addEventListener('keydown', handleKeyDown);
        } else {
            document.body.style.overflow = '';
        }
        return () => {
            document.body.style.overflow = '';
            window.removeEventListener('keydown', handleKeyDown);
        };
    }, [mobileOpen]);

    // Reset main content scroll when changing pages
    React.useEffect(() => {
        if (mainScrollRef.current) {
            mainScrollRef.current.scrollTop = 0;
        }
    }, [screen]);

    return (
        <div className="w-full h-screen h-[100dvh] max-h-screen overflow-hidden relative flex p-3 sm:p-5 gap-5 font-sans text-slate-800 antialiased">
            <AppBackground />

            {/* FLOATING GLASS SIDEBAR */}
            <aside
                className={`
                    fixed lg:static top-0 left-0 z-40
                    h-full w-[270px] lg:w-[260px] shrink-0
                    bg-white/20 backdrop-blur-3xl
                    border border-white/40 lg:rounded-3xl
                    flex flex-col justify-between
                    p-5 transition-transform duration-300 ease-in-out
                    shadow-[0_20px_50px_rgba(15,23,42,0.08)]
                    ${mobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
                `}
                aria-label="Sidebar Navigation"
            >
                {/* SECTION 1: BRAND LOGO HEADER */}
                <div className="flex items-center justify-between shrink-0 pb-4 border-b border-white/30">
                    <Link className="flex items-center gap-3 text-decoration-none group" href="/dashboard">
                        <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-blue-500 to-indigo-600 shadow-lg shadow-blue-500/25 flex items-center justify-center text-white relative group-hover:scale-105 transition-transform border border-white/40">
                            <House size={20} className="fill-white/20" />
                        </div>
                        <div className="flex flex-col">
                            <div className="flex items-baseline gap-0.5">
                                <span className="text-xl font-black tracking-tight text-slate-900">
                                    nhà mình
                                </span>
                                <span className="text-blue-600 font-black text-xl leading-none">.</span>
                            </div>
                            <span className="text-[10px] text-slate-500 font-medium">
                                Tiện ích hôm nay, cuộc sống tốt hơn
                            </span>
                        </div>
                    </Link>
                    <button
                        onClick={() => setMobileOpen(false)}
                        className="lg:hidden w-8 h-8 rounded-full bg-white/40 text-slate-500 flex items-center justify-center border border-white/40 hover:bg-white/60 transition-colors"
                        aria-label="Close sidebar"
                    >
                        <X size={16} />
                    </button>
                </div>

                {/* SECTION 2: NAVIGATION MENU (INDEPENDENT SCROLL) */}
                <nav className="flex-1 min-h-0 overflow-y-auto custom-scrollbar space-y-1.5 py-4">
                    {navItems.map(({ href, label, icon: Icon, isAI, hasBadge }) => {
                        const isActive = screen === href || screen.startsWith(href + '/');
                        return (
                            <Link
                                key={href}
                                href={'/' + href}
                                onClick={() => setMobileOpen(false)}
                                className={`
                                    flex items-center gap-3 px-3.5 py-2.5 rounded-2xl text-xs font-semibold transition-all duration-200 text-decoration-none
                                    ${
                                        isActive
                                            ? 'bg-gradient-to-r from-blue-500 to-indigo-600 text-white shadow-lg shadow-blue-500/30 font-bold'
                                            : 'text-slate-700 hover:bg-white/30 hover:text-slate-900'
                                    }
                                `}
                            >
                                <Icon size={17} className={isActive ? 'text-white' : 'text-slate-500'} />
                                <span className="flex-1">{label}</span>
                                {isAI && (
                                    <span className="px-2 py-0.5 rounded-full text-[9px] font-black bg-blue-500/20 text-blue-700 border border-blue-400/30">
                                        AI
                                    </span>
                                )}
                                {hasBadge && unreadCount > 0 && (
                                    <span className="w-5 h-5 rounded-full bg-rose-500 text-white text-[10px] font-bold flex items-center justify-center shadow-xs">
                                        {unreadCount}
                                    </span>
                                )}
                            </Link>
                        );
                    })}
                </nav>

                {/* SECTION 3: BOTTOM UTILITIES & PROMO (SHRINK 0) */}
                <div className="shrink-0 space-y-3 pt-3 border-t border-white/30">
                    {/* PROMO CARD */}
                    <div className="rounded-2xl bg-emerald-500/10 border border-emerald-500/20 p-3 space-y-1">
                        <div className="flex items-center gap-2">
                            <div className="w-5 h-5 rounded-lg bg-emerald-500 text-white flex items-center justify-center text-[10px]">
                                <Leaf size={12} />
                            </div>
                            <span className="text-xs font-bold text-emerald-900">Vì một hành trình xanh</span>
                        </div>
                        <p className="text-[10px] text-emerald-700/80 leading-tight">
                            Tiết kiệm hôm nay cho ngày mai bền vững.
                        </p>
                    </div>

                    <div className="space-y-1">
                        {user && user.role === 'ADMIN' && user.is_active === true && (
                            <Link
                                href="/admin"
                                onClick={() => setMobileOpen(false)}
                                className={`flex items-center gap-3 px-3.5 py-2 rounded-xl text-xs font-semibold text-decoration-none transition-all duration-200 ${
                                    screen === 'admin' || screen.startsWith('admin/')
                                        ? 'bg-gradient-to-r from-blue-500 to-indigo-600 text-white font-bold shadow-md shadow-blue-500/20'
                                        : 'text-slate-700 hover:bg-white/30 hover:text-slate-900'
                                }`}
                            >
                                <ShieldCheck size={16} className={screen === 'admin' || screen.startsWith('admin/') ? 'text-white' : 'text-blue-600'} />
                                <span>Quản trị hệ thống</span>
                            </Link>
                        )}
                        <Link
                            href="/settings"
                            onClick={() => setMobileOpen(false)}
                            className="flex items-center gap-3 px-3.5 py-2 rounded-xl text-xs font-semibold text-slate-700 hover:bg-white/30 text-decoration-none"
                        >
                            <Settings size={16} className="text-slate-500" />
                            <span>Cài đặt</span>
                        </Link>
                        <Link
                            href="/assistant"
                            onClick={() => setMobileOpen(false)}
                            className="flex items-center gap-3 px-3.5 py-2 rounded-xl text-xs font-semibold text-slate-700 hover:bg-white/30 text-decoration-none"
                        >
                            <Sparkles size={16} className="text-slate-500" />
                            <span>Trợ giúp</span>
                        </Link>
                        <button
                            onClick={onLogout}
                            className="w-full flex items-center gap-3 px-3.5 py-2 rounded-xl text-xs font-semibold text-slate-700 hover:bg-rose-500/10 hover:text-rose-600 transition-colors cursor-pointer"
                        >
                            <LogOut size={16} className="text-slate-500" />
                            <span>Đăng xuất</span>
                        </button>
                    </div>

                    <div className="pt-1 text-[10px] text-slate-400 font-medium leading-tight">
                        <div>nhà mình. © 2026</div>
                        <div>Phiên bản 1.0.0</div>
                    </div>
                </div>
            </aside>

            {/* MOBILE BACKDROP */}
            {mobileOpen && (
                <div
                    onClick={() => setMobileOpen(false)}
                    className="fixed inset-0 z-30 bg-slate-900/30 backdrop-blur-xs lg:hidden"
                    aria-hidden="true"
                />
            )}

            {/* MAIN CONTENT AREA CONTAINER */}
            <div className="flex-1 flex flex-col min-w-0 min-h-0 h-full gap-4 sm:gap-5">
                {/* FLOATING STICKY HEADER */}
                <header className="shrink-0 bg-white/20 backdrop-blur-3xl border border-white/40 rounded-3xl px-6 py-3.5 flex items-center justify-between shadow-[0_10px_30px_rgba(15,23,42,0.04)]">
                    <div className="flex items-center gap-3 flex-1 max-w-md">
                        <button
                            onClick={() => setMobileOpen(true)}
                            className="lg:hidden w-9 h-9 rounded-2xl bg-white/40 border border-white/40 text-slate-700 flex items-center justify-center shadow-xs cursor-pointer hover:bg-white/60 transition-colors"
                            aria-label="Open menu"
                        >
                            <Menu size={18} />
                        </button>

                        {/* SEARCH INPUT BAR */}
                        <div className="flex-1 flex items-center gap-2 bg-white/30 backdrop-blur-md px-4 py-2 rounded-full border border-white/50 text-xs text-slate-600 shadow-xs">
                            <Search size={15} className="text-slate-400" />
                            <input
                                type="text"
                                placeholder="Tìm kiếm chức năng, hóa đơn, trợ giúp..."
                                className="bg-transparent border-none outline-none text-xs text-slate-800 placeholder:text-slate-400 w-full"
                            />
                        </div>
                    </div>

                    <div className="flex items-center gap-4">
                        {/* DATE BADGE */}
                        <div className="hidden md:flex items-center gap-2 text-xs font-semibold text-slate-600 bg-white/30 backdrop-blur-md px-4 py-2 rounded-full border border-white/50 shadow-xs">
                            <CalendarDays size={14} className="text-slate-500" />
                            <span>{todayLabel || 'Đang tải ngày'}</span>
                        </div>

                        {/* BELL NOTIFICATION */}
                        <Link
                            href="/notifications"
                            className="relative w-9 h-9 rounded-full bg-white/30 backdrop-blur-md border border-white/50 text-slate-700 flex items-center justify-center hover:bg-white/50 transition-all text-decoration-none shadow-xs"
                        >
                            <Bell size={17} />
                            {unreadCount > 0 && (
                                <span className="absolute top-1 right-1 w-2.5 h-2.5 rounded-full bg-rose-500 border-2 border-white shadow-xs" />
                            )}
                        </Link>

                        {/* USER CHIP */}
                        <div className="flex items-center gap-2.5 pl-2">
                            <div className="w-9 h-9 rounded-full bg-gradient-to-tr from-blue-600 to-indigo-600 text-white font-bold text-xs flex items-center justify-center shadow-md shadow-blue-500/20 border-2 border-white">
                                {user?.full_name ? user.full_name.slice(0, 1) : 'A'}
                            </div>
                            <div className="hidden sm:flex flex-col text-left">
                                <strong className="text-xs font-bold text-slate-900 leading-tight">
                                    {user?.full_name || 'Nguyễn Văn An'}
                                </strong>
                                <span className="text-[10px] font-medium text-slate-500">
                                    Chủ hộ ▾
                                </span>
                            </div>
                        </div>
                    </div>
                </header>

                {/* MAIN SCROLLABLE CONTENT VIEWPORT */}
                <main
                    ref={mainScrollRef}
                    className={`flex-1 min-h-0 ${
                        screen === 'assistant'
                            ? 'h-full overflow-hidden'
                            : 'overflow-y-auto custom-scrollbar pr-1'
                    }`}
                >
                    <div key={screen} className="w-full h-full animate-subtle-slide-in">
                        {children}
                    </div>
                </main>
            </div>
        </div>
    );
}
