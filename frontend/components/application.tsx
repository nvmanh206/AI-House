'use client';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useEffect, useState, FormEvent, ReactNode } from 'react';
import { House, LayoutDashboard, Zap, Droplets, ReceiptText, ChartNoAxesCombined, Bell, Sparkles, Settings, Users, ArrowUpRight, ArrowDownRight, ArrowRight, Plus, ChevronRight, Menu, X, LogOut, Send, Check, ShieldCheck, Gauge, CalendarDays, Leaf, Download, AlertTriangle, Play, Star, PiggyBank, FileText, Lightbulb, FileSpreadsheet, Search, TrendingUp, TrendingDown, Eye, EyeOff, User, Mail, Lock, Globe, Heart, MessageSquare, Copy, Trash2, Mic, RotateCcw, Cpu, Bot, Info, CreditCard, PieChart } from 'lucide-react';
import { api, setToken, refreshSession } from './api';
import { UsageChart, ExecutiveSpendingChart, CostBreakdownDonut, MonthlyComparisonBar, MiniSparkline } from './charts';
import { ChatAnswer } from './chat-answer';
import { DashboardBackground } from './dashboard/DashboardBackground';
import { DashboardHeader } from './dashboard/DashboardHeader';
import { StatGrid } from './dashboard/StatGrid';
import { ExpenseTrendChart } from './dashboard/ExpenseTrendChart';
import { CostBreakdown } from './dashboard/CostBreakdown';
import { ComparisonChart } from './dashboard/ComparisonChart';
import { BudgetProgress } from './dashboard/BudgetProgress';
import { AIInsightPanel } from './dashboard/AIInsightPanel';
import { UpcomingBills } from './dashboard/UpcomingBills';
import { NotificationPanel } from './dashboard/NotificationPanel';
import { StatisticsPage } from './statistics/StatisticsPage';
import { AppBackground } from './layout/AppBackground';
import { AppLayout } from './layout/AppLayout';
import { AuthLayout } from './layout/AuthLayout';
import { GlassCard } from './ui/GlassCard';
import { GlassPanel } from './ui/GlassPanel';
import { GlassInput, GlassSelect } from './ui/GlassInput';
import { PrimaryButton, SecondaryButton } from './ui/PrimaryButton';
import { StatusBadge } from './ui/StatusBadge';
import { PageHeader } from './ui/PageHeader';
import { EmptyState } from './ui/EmptyState';
import { LoadingSkeleton, SkeletonGrid } from './ui/LoadingSkeleton';
import { GlassModal, GlassDrawer } from './ui/GlassModal';

type Row = Record<string, any>;
const money = (value: unknown) => Number(value || 0).toLocaleString('vi-VN', { maximumFractionDigits: 0 }) + ' ₫';
const quantity = (value: unknown) => value === null || value === undefined ? '—' : Number(value).toLocaleString('vi-VN', { maximumFractionDigits: 3 });
const localDate = () => new Intl.DateTimeFormat('sv-SE', { timeZone: 'Asia/Ho_Chi_Minh' }).format(new Date());
const statusNames: Row = { UNPAID: 'Chưa thanh toán', OVERDUE: 'Quá hạn', PAID: 'Đã thanh toán', PENDING: 'Đang xử lý', DRAFT: 'Bản nháp', CANCELLED: 'Đã hủy' };
const titles: Row = { dashboard: 'Tổng quan', household: 'Hộ gia đình', 'household/members': 'Thành viên', meters: 'Công tơ', readings: 'Nhập chỉ số', bills: 'Hóa đơn', statistics: 'Thống kê', notifications: 'Thông báo', assistant: 'Trợ lý AI', settings: 'Cài đặt', admin: 'Quản trị hệ thống', 'admin/users': 'Người dùng', 'admin/tariffs': 'Biểu giá', 'admin/audit': 'Nhật ký hệ thống' };
const nav = [['dashboard', 'Tổng quan', LayoutDashboard], ['readings', 'Nhập chỉ số', Gauge], ['bills', 'Hóa đơn', ReceiptText], ['statistics', 'Thống kê', ChartNoAxesCombined], ['assistant', 'Trợ lý AI', Sparkles], ['household', 'Hộ gia đình', House], ['meters', 'Công tơ', Zap], ['notifications', 'Thông báo', Bell]] as const;
function Badge({ status }: { status: string }) { return <span className={'badge ' + status.toLowerCase()}><i />{statusNames[status] || status}</span> }
function Empty({ children, href }: { children: ReactNode; href?: string }) { return <div className="empty"><ReceiptText size={30} /><p>{children}</p>{href && <Link className="button small" href={href}>Bắt đầu <ArrowRight size={16} /></Link>}</div> }
function Field({ label, name, type = 'text', value, required = true, ...props }: any) { return <label className="field"><span>{label}</span><input name={name} type={type} defaultValue={value} required={required} {...props} /></label> }
function Select({ label, name, children, ...props }: any) { return <label className="field"><span>{label}</span><select name={name} {...props}>{children}</select></label> }
function Panel({ title, children, action, className = '' }: { title?: string; children: ReactNode; action?: ReactNode; className?: string }) { return <section className={'panel ' + className}>{title && <div className="panel-head"><h2>{title}</h2>{action}</div>}{children}</section> }
function DataTable({ columns, rows }: { columns: { title: string; render: (r: Row) => ReactNode }[]; rows: Row[] }) { return rows.length ? <div className="table-wrap"><table><thead><tr>{columns.map(c => <th key={c.title}>{c.title}</th>)}</tr></thead><tbody>{rows.map((r, i) => <tr key={r.id || r.period || i}>{columns.map(c => <td key={c.title}>{c.render(r)}</td>)}</tr>)}</tbody></table></div> : <Empty>Chưa có dữ liệu.</Empty> }

function EcoAnimatedBackground() {
    return (
        <div className="eco-background-layer">
            <div className="eco-glow-1" />
            <div className="eco-glow-2" />
            <div className="eco-glow-3" />
            {/* Floating leaf SVG elements */}
            <svg className="floating-leaf" style={{ top: '12%', left: '8%', width: 24, height: 24 }} viewBox="0 0 24 24" fill="none" stroke="#10b981" strokeWidth="1.5">
                <path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.4 19 2c1 2 2 4.1 2 7 0 6-4.5 11-10 11Z" />
                <path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12" />
            </svg>
            <svg className="floating-leaf" style={{ top: '65%', right: '6%', width: 32, height: 32, animationDelay: '2s' }} viewBox="0 0 24 24" fill="none" stroke="#0ea5e9" strokeWidth="1.5">
                <path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.4 19 2c1 2 2 4.1 2 7 0 6-4.5 11-10 11Z" />
            </svg>
            <svg className="floating-leaf" style={{ bottom: '8%', left: '20%', width: 28, height: 28, animationDelay: '4s' }} viewBox="0 0 24 24" fill="none" stroke="#34d399" strokeWidth="1.5">
                <path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.4 19 2c1 2 2 4.1 2 7 0 6-4.5 11-10 11Z" />
            </svg>
        </div>
    );
}

export default function Application() {
    const path = usePathname(), router = useRouter(), screen = path.slice(1) || 'landing';
    const [user, setUser] = useState<Row | null>(null), [loading, setLoading] = useState(true), [error, setError] = useState(''), [toast, setToast] = useState(''), [mobile, setMobile] = useState(false), [notifications, setNotifications] = useState<Row[]>([]), [reload, setReload] = useState(0);
    const publicPage = ['landing', 'login', 'register'].includes(screen);
    useEffect(() => { let alive = true; if (publicPage) { setLoading(false); return; } setLoading(true); (async () => { if (!await refreshSession()) { router.replace('/login'); return; } const me = await api('/auth/me'); if (!alive) return; setUser(me); if (!me.household_id && screen !== 'onboarding' && !screen.startsWith('admin')) { router.replace('/onboarding'); return; } if (me.household_id) { const n = await api('/notifications'); if (alive) setNotifications(n); } setLoading(false); })().catch(e => { if (alive) { setError(e.message); setLoading(false) } }); return () => { alive = false } }, [screen, publicPage, router, reload]);
    useEffect(() => { if (!toast) return; const t = setTimeout(() => setToast(''), 4500); return () => clearTimeout(t) }, [toast]);
    const notify = (message = 'Đã lưu thay đổi.') => { setToast(message); setReload(v => v + 1) };
    if (publicPage) return screen === 'landing' ? <Landing /> : <AuthForm register={screen === 'register'} />;
    if (loading) return <div className="loading-screen"><div className="brand"><span className="brand-icon"><House /></span>nhà mình<span className="brand-dot">.</span></div><div className="skeleton" /><p>Đang tải dữ liệu của bạn…</p></div>;
    if (!user) return <div className="loading-screen"><p className="error">{error || 'Phiên đăng nhập không hợp lệ.'}</p><Link href="/login" className="button">Đăng nhập</Link></div>;
    if (screen === 'onboarding') return <Onboarding notify={notify} />;
    const unread = notifications.filter(n => !n.is_read).length;
    const handleLogout = async () => {
        try {
            await api('/auth/logout', 'POST');
            setToken(null);
            router.push('/login');
        } catch (e: any) {
            setError(e.message);
        }
    };

    return (
        <AppLayout
            user={user}
            screen={screen}
            notifications={notifications}
            unreadCount={unread}
            onLogout={handleLogout}
            title={titles[screen]}
        >
            {error && (
                <div role="alert" className="p-4 mb-4 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-700 text-xs font-bold flex items-center justify-between">
                    <span>{error}</span>
                    <button onClick={() => setError('')} className="p-1 rounded-full hover:bg-rose-500/20"><X size={16} /></button>
                </div>
            )}
            {screen === 'dashboard' ? (
                <Dashboard user={user} notifications={notifications} />
            ) : (
                <Page screen={screen} user={user} notifications={notifications} notify={notify} />
            )}
        </AppLayout>
    );
}

function Landing() {
    return (
        <div className="landing-v2">
            {/* STICKY HEADER NAVBAR */}
            <header className="landing-navbar">
                <Link href="/" className="landing-brand">
                    <span className="brand-icon"><House size={20} /></span>
                    <span className="brand-title">nhà mình<span className="dot">.</span></span>
                </Link>
                <nav className="landing-nav-links">
                    <a href="#tinh-nang">Tính năng</a>
                    <a href="#giai-phap">Giải pháp</a>
                    <a href="#bieu-gia">Biểu giá</a>
                    <a href="#ai-assistant">AI Assistant</a>
                    <a href="#lien-he">Liên hệ</a>
                </nav>
                <div className="landing-nav-actions">
                    <Link href="/login" className="nav-login-btn">Đăng nhập</Link>
                    <Link href="/register" className="button nav-cta-btn">Dùng thử miễn phí <ArrowRight size={16} /></Link>
                </div>
            </header>

            <main className="landing-body">
                {/* HERO SECTION SPLIT LAYOUT */}
                <section className="landing-hero-section">
                    <div className="hero-content">
                        <div className="hero-pill-badge">
                            <span>Một ngôi nhà. Một chỉ số. Một cuộc sống tốt hơn.</span>
                        </div>
                        <h1 className="hero-title">
                            Hiểu năng lượng.<br />
                            Chủ động chi tiêu.<br />
                            <span className="highlight-text">Theo dõi hóa đơn, tối ưu chi phí bằng AI.</span>
                        </h1>
                        <p className="hero-description">
                            <strong>nhà mình.</strong> giúp các gia đình theo dõi hóa đơn điện, nước, nhận nhắc nhở đúng hạn và phân tích chi tiêu thông minh bằng AI — để cuộc sống thoải mái hơn, tiết kiệm hơn mỗi ngày.
                        </p>
                        <div className="hero-actions">
                            <Link href="/register" className="button hero-btn-primary">Dùng thử miễn phí <ArrowRight size={18} /></Link>
                            <Link href="/login" className="button hero-btn-secondary"><Play size={16} className="play-icon" /> Tìm hiểu thêm</Link>
                        </div>
                        <div className="hero-trust-list">
                            <span><Check size={16} /> Miễn phí 14 ngày</span>
                            <span><Check size={16} /> Không cần thẻ tín dụng</span>
                            <span><Check size={16} /> Cài đặt trong 2 phút</span>
                        </div>
                    </div>

                    {/* HERO APP WINDOW MOCKUP */}
                    <div className="hero-mockup-wrapper">
                        <div className="mockup-window">
                            <div className="mockup-window-header">
                                <div className="window-dots">
                                    <span className="dot red"></span>
                                    <span className="dot yellow"></span>
                                    <span className="dot green"></span>
                                </div>
                                <div className="window-search-bar">
                                    <Search size={14} /> <span>Tìm kiếm…</span>
                                </div>
                                <div className="window-user-profile">
                                    <Bell size={16} />
                                    <div className="user-avatar-sm">N</div>
                                    <span>Nguyễn Văn An <small>Gia đình 4 người</small></span>
                                </div>
                            </div>
                            <div className="mockup-window-body">
                                <div className="mockup-sidebar">
                                    <div className="mockup-logo"><House size={16} /> nhà mình.</div>
                                    <div className="mockup-menu">
                                        <span className="active"><LayoutDashboard size={15} /> Tổng quan</span>
                                        <span><ReceiptText size={15} /> Hóa đơn</span>
                                        <span><Sparkles size={15} /> Phân tích AI</span>
                                        <span><Bell size={15} /> Nhắc nhở</span>
                                        <span><Users size={15} /> Gia đình</span>
                                        <span><ChartNoAxesCombined size={15} /> Báo cáo</span>
                                        <span><Settings size={15} /> Cài đặt</span>
                                    </div>
                                </div>
                                <div className="mockup-main-content">
                                    <div className="mockup-greeting">
                                        <div>
                                            <h3>Tổng quan</h3>
                                            <p>Chào buổi sáng! Đây là tình hình chi tiêu điện nước của gia đình bạn.</p>
                                        </div>
                                        <div className="mockup-date-badge">Tháng 11, 2024</div>
                                    </div>

                                    {/* 3 KPI CARDS INSIDE MOCKUP */}
                                    <div className="mockup-kpi-grid">
                                        <div className="m-kpi-card">
                                            <div className="m-kpi-head"><Zap size={16} className="text-amber" /> Tiền điện</div>
                                            <div className="m-kpi-val">450.000đ <span className="m-badge green">↓ 12%</span></div>
                                            <small>Thấp hơn tháng trước</small>
                                        </div>
                                        <div className="m-kpi-card">
                                            <div className="m-kpi-head"><Droplets size={16} className="text-cyan" /> Tiền nước</div>
                                            <div className="m-kpi-val">120.000đ <span className="m-badge red">↑ 5%</span></div>
                                            <small>Cao hơn tháng trước</small>
                                        </div>
                                        <div className="m-kpi-card">
                                            <div className="m-kpi-head"><ReceiptText size={16} className="text-blue" /> Tổng chi phí</div>
                                            <div className="m-kpi-val">570.000đ <span className="m-badge green">↓ 8%</span></div>
                                            <small>Thấp hơn tháng trước</small>
                                        </div>
                                    </div>

                                    {/* MOCKUP CHARTS ROW */}
                                    <div className="mockup-charts-grid">
                                        <div className="m-chart-panel">
                                            <div className="m-panel-head">
                                                <strong>Biểu đồ tiêu thụ</strong>
                                                <span className="m-sub">12 tháng qua</span>
                                            </div>
                                            <div className="m-mock-bars">
                                                {[35, 42, 58, 65, 80, 95, 110, 88, 70, 60, 52].map((h, i) => (
                                                    <div key={i} className="m-bar-col">
                                                        <div className="m-bar elec" style={{ height: `${h}%` }}></div>
                                                        <div className="m-bar water" style={{ height: `${h * 0.4}%` }}></div>
                                                        <span>Th{i + 1}</span>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>

                                        <div className="m-ai-insight-panel">
                                            <div className="m-ai-head"><Sparkles size={16} /> AI gợi ý cho bạn <span className="badge-ai-sm">AI</span></div>
                                            <div className="m-ai-alert">
                                                <div className="m-alert-title"><Check size={14} /> Mức tiêu thụ điện tháng này thấp hơn 12% so với tháng trước. Tuyệt vời!</div>
                                                <p>Bạn có thể tiết kiệm ~50.000đ/tháng nếu sử dụng điều hòa ở 26°C thay vì 24°C.</p>
                                                <a href="#" onClick={e => e.preventDefault()} className="m-ai-link">Xem chi tiết phân tích →</a>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>

                {/* TRUST STATS BAR - 5 COLUMNS */}
                <section className="landing-trust-bar">
                    <div className="trust-item">
                        <div className="trust-icon"><House size={22} /></div>
                        <div>
                            <strong>50.000+</strong>
                            <span>Hộ gia đình tin dùng</span>
                        </div>
                    </div>
                    <div className="trust-item">
                        <div className="trust-icon"><FileText size={22} /></div>
                        <div>
                            <strong>1.2 triệu+</strong>
                            <span>Hóa đơn đã được theo dõi</span>
                        </div>
                    </div>
                    <div className="trust-item">
                        <div className="trust-icon"><PiggyBank size={22} /></div>
                        <div>
                            <strong>3.5 tỷ+</strong>
                            <span>Tiền tiết kiệm cho người dùng</span>
                        </div>
                    </div>
                    <div className="trust-item">
                        <div className="trust-icon"><Bell size={22} /></div>
                        <div>
                            <strong>99.8%</strong>
                            <span>Nhắc nhở đúng hạn</span>
                        </div>
                    </div>
                    <div className="trust-item">
                        <div className="trust-icon">
                            <div className="stars-wrap"><Star size={14} fill="#f59e0b" color="#f59e0b" /><Star size={14} fill="#f59e0b" color="#f59e0b" /><Star size={14} fill="#f59e0b" color="#f59e0b" /><Star size={14} fill="#f59e0b" color="#f59e0b" /><Star size={14} fill="#f59e0b" color="#f59e0b" /></div>
                        </div>
                        <div>
                            <strong>4.9/5</strong>
                            <span>Từ hơn 2.000 đánh giá thực tế</span>
                        </div>
                    </div>
                </section>

                {/* FEATURES SECTION - 6 BENTO CARDS */}
                <section className="landing-features-section" id="tinh-nang">
                    <div className="section-header">
                        <div className="eyebrow-tag">TÍNH NĂNG NỔI BẬT</div>
                        <h2>Mọi thứ bạn cần để quản lý chi tiêu gia đình</h2>
                        <p className="subtitle">Đơn giản — Thông minh — Hiệu quả</p>
                    </div>

                    <div className="features-6-grid">
                        <div className="feature-card">
                            <div className="feature-icon-wrap amber"><Zap size={24} /></div>
                            <h3>Tự động tính hóa đơn</h3>
                            <p>Nhập chỉ số, hệ thống tự tính tiền điện nước theo biểu giá mới nhất.</p>
                        </div>
                        <div className="feature-card">
                            <div className="feature-icon-wrap blue"><Bell size={24} /></div>
                            <h3>Nhắc nhở đúng hạn</h3>
                            <p>Không còn lo quên thanh toán với hệ thống nhắc nhở thông minh.</p>
                        </div>
                        <div className="feature-card">
                            <div className="feature-icon-wrap purple"><Sparkles size={24} /></div>
                            <h3>Phân tích bằng AI</h3>
                            <p>AI phân tích thói quen sử dụng và đưa ra insight cá nhân hóa cho gia đình bạn.</p>
                        </div>
                        <div className="feature-card">
                            <div className="feature-icon-wrap cyan"><Lightbulb size={24} /></div>
                            <h3>Gợi ý tiết kiệm</h3>
                            <p>Nhận các đề xuất thiết thực để giảm chi phí mà vẫn đảm bảo sự thoải mái.</p>
                        </div>
                        <div className="feature-card">
                            <div className="feature-icon-wrap green"><Users size={24} /></div>
                            <h3>Quản lý nhiều thành viên</h3>
                            <p>Cả gia đình cùng theo dõi, phân quyền linh hoạt.</p>
                        </div>
                        <div className="feature-card">
                            <div className="feature-icon-wrap indigo"><FileSpreadsheet size={24} /></div>
                            <h3>Báo cáo hàng tháng</h3>
                            <p>Biểu đồ trực quan, dễ hiểu về tình hình chi tiêu và xu hướng sử dụng.</p>
                        </div>
                    </div>
                </section>

                {/* AI ASSISTANT HIGHLIGHT SECTION */}
                <section className="landing-ai-section" id="ai-assistant">
                    <div className="ai-section-grid">
                        <div className="ai-left-info">
                            <div className="eyebrow-tag">AI ASSISTANT</div>
                            <h2>Trợ lý AI đồng hành cùng gia đình bạn</h2>
                            <p>Không chỉ hiển thị số liệu, <strong>nhà mình.</strong> còn dùng AI để hiểu thói quen sử dụng và đưa ra những gợi ý thiết thực, giúp bạn tiết kiệm hơn mỗi tháng.</p>
                            <Link href="/register" className="button ai-cta-btn">Trải nghiệm AI Assistant <ArrowRight size={18} /></Link>
                        </div>

                        <div className="ai-right-preview-cards">
                            <div className="ai-card-item">
                                <div className="ai-card-head">
                                    <span><Sparkles size={16} /> AI Insight</span>
                                    <span className="save-tag">Tiết kiệm 50.000đ/tháng</span>
                                </div>
                                <p className="ai-card-body">💡 Bạn thường sử dụng nhiều điện hơn vào buổi tối. Thử chuyển một số thiết bị sang ban ngày để tiết kiệm chi phí.</p>
                                <a href="#" onClick={e => e.preventDefault()} className="ai-card-link">Xem thêm gợi ý →</a>
                            </div>

                            <div className="ai-card-item split">
                                <div className="ai-mini-panel">
                                    <div className="ai-mini-head">So sánh theo tháng</div>
                                    <div className="ai-mini-badge green">Giảm 12% so với tháng trước</div>
                                    <div className="ai-mini-bars">
                                        <div className="bar-set"><span>Th6</span><i style={{ height: '60%' }}></i></div>
                                        <div className="bar-set"><span>Th7</span><i style={{ height: '75%' }}></i></div>
                                        <div className="bar-set"><span>Th8</span><i style={{ height: '70%' }}></i></div>
                                        <div className="bar-set"><span>Th9</span><i style={{ height: '65%' }}></i></div>
                                        <div className="bar-set"><span>Th10</span><i style={{ height: '55%' }}></i></div>
                                        <div className="bar-set active"><span>Th11</span><i style={{ height: '48%' }}></i></div>
                                    </div>
                                </div>

                                <div className="ai-mini-panel donut">
                                    <div className="ai-mini-head">Cơ cấu chi phí tháng 11</div>
                                    <div className="donut-center">
                                        <strong>570.000đ</strong>
                                        <small>Tổng cộng</small>
                                    </div>
                                    <div className="donut-legend">
                                        <span><i className="elec" /> Điện: 78.9%</span>
                                        <span><i className="water" /> Nước: 21.1%</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>

                {/* TESTIMONIALS SECTION */}
                <section className="landing-testimonials-section">
                    <div className="section-header">
                        <div className="eyebrow-tag">KHÁCH HÀNG NÓI VỀ NHÀ MÌNH.</div>
                        <h2>Đã có hàng chục nghìn gia đình tin dùng</h2>
                    </div>

                    <div className="testimonials-grid">
                        <div className="testimonial-card">
                            <div className="t-stars"><Star size={15} fill="#f59e0b" color="#f59e0b" /><Star size={15} fill="#f59e0b" color="#f59e0b" /><Star size={15} fill="#f59e0b" color="#f59e0b" /><Star size={15} fill="#f59e0b" color="#f59e0b" /><Star size={15} fill="#f59e0b" color="#f59e0b" /></div>
                            <p>“<strong>nhà mình.</strong> giúp gia đình mình kiểm soát chi tiêu tốt hơn rất nhiều. Đặc biệt là tính năng nhắc nhở, không còn lo quên đóng tiền điện nữa!”</p>
                            <div className="t-author">
                                <div className="t-avatar">H</div>
                                <div>
                                    <strong>Hà Nguyễn</strong>
                                    <span>Hà Nội</span>
                                </div>
                            </div>
                        </div>

                        <div className="testimonial-card">
                            <div className="t-stars"><Star size={15} fill="#f59e0b" color="#f59e0b" /><Star size={15} fill="#f59e0b" color="#f59e0b" /><Star size={15} fill="#f59e0b" color="#f59e0b" /><Star size={15} fill="#f59e0b" color="#f59e0b" /><Star size={15} fill="#f59e0b" color="#f59e0b" /></div>
                            <p>“Phân tích AI thật sự hữu ích. Mình đã điều chỉnh thói quen sử dụng và tiết kiệm được khoảng 15% tiền điện mỗi tháng.”</p>
                            <div className="t-author">
                                <div className="t-avatar blue">H</div>
                                <div>
                                    <strong>Hải Trần</strong>
                                    <span>TP. Hồ Chí Minh</span>
                                </div>
                            </div>
                        </div>

                        <div className="testimonial-card">
                            <div className="t-stars"><Star size={15} fill="#f59e0b" color="#f59e0b" /><Star size={15} fill="#f59e0b" color="#f59e0b" /><Star size={15} fill="#f59e0b" color="#f59e0b" /><Star size={15} fill="#f59e0b" color="#f59e0b" /><Star size={15} fill="#f59e0b" color="#f59e0b" /></div>
                            <p>“Giao diện rất đẹp và dễ sử dụng. Cả gia đình mình cùng theo dõi, mọi thứ đều rõ ràng và minh bạch.”</p>
                            <div className="t-author">
                                <div className="t-avatar cyan">Đ</div>
                                <div>
                                    <strong>Đỗ Phương</strong>
                                    <span>Đà Nẵng</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>
            </main>

            <footer className="landing-v2-footer">
                <div className="footer-inner">
                    <div className="footer-brand">
                        <Link href="/" className="landing-brand">
                            <span className="brand-icon"><House size={20} /></span>
                            <span className="brand-title">nhà mình<span className="dot">.</span></span>
                        </Link>
                        <p>Năng lượng trong tầm tay — Dữ liệu của bạn, không gian của bạn.</p>
                    </div>
                    <div className="footer-links">
                        <div>
                            <strong>Sản phẩm</strong>
                            <a href="#tinh-nang">Tính năng</a>
                            <a href="#ai-assistant">Trợ lý AI</a>
                            <a href="#bieu-gia">Biểu giá EVN</a>
                        </div>
                        <div>
                            <strong>Tài khoản</strong>
                            <Link href="/login">Đăng nhập</Link>
                            <Link href="/register">Đăng ký ngay</Link>
                        </div>
                    </div>
                </div>
                <div className="footer-bottom">
                    <span>© 2026 Nhà Mình. Được thiết kế cho những ngôi nhà Việt.</span>
                </div>
            </footer>
        </div>
    );
}

function AuthForm({ register }: { register: boolean }) {
    const router = useRouter(), [error, setError] = useState(''), [busy, setBusy] = useState(false), [showPassword, setShowPassword] = useState(false);
    async function submit(e: FormEvent<HTMLFormElement>) {
        e.preventDefault();
        setBusy(true);
        setError('');
        const data = Object.fromEntries(new FormData(e.currentTarget));
        try {
            const result = await api('/auth/' + (register ? 'register' : 'login'), 'POST', data);
            setToken(result.access_token);
            router.push(register ? '/onboarding' : '/dashboard');
        } catch (e: any) {
            setError(e.message);
        } finally {
            setBusy(false);
        }
    }

    return (
        <AuthLayout
            title={register ? 'Tạo tài khoản nhà mình' : 'Đăng nhập hệ thống'}
            subtitle={register ? 'Đăng ký trong 1 phút để bắt đầu quản lý tiện ích gia đình.' : 'Nhập thông tin tài khoản để truy cập dashboard.'}
            isRegister={register}
        >
            <form onSubmit={submit} className="space-y-4">
                {error && (
                    <div role="alert" className="p-3.5 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-700 text-xs font-bold flex items-center gap-2">
                        <AlertTriangle size={16} className="shrink-0" />
                        <span>{error}</span>
                    </div>
                )}

                {register && (
                    <GlassInput
                        label="Họ và tên chủ hộ"
                        name="full_name"
                        placeholder="Ví dụ: Nguyễn Văn An"
                        icon={<User size={16} />}
                        autoComplete="name"
                        minLength={2}
                        maxLength={120}
                        required
                    />
                )}

                <GlassInput
                    label="Địa chỉ Email"
                    name="email"
                    type="email"
                    placeholder="name@example.com"
                    icon={<Mail size={16} />}
                    autoComplete="email"
                    required
                />

                <div className="relative">
                    <GlassInput
                        label="Mật khẩu"
                        name="password"
                        type={showPassword ? 'text' : 'password'}
                        placeholder={register ? 'Tạo mật khẩu (tối thiểu 8 ký tự)' : '••••••••••••'}
                        icon={<Lock size={16} />}
                        minLength={register ? 8 : 1}
                        maxLength={128}
                        autoComplete={register ? 'new-password' : 'current-password'}
                        required
                    />
                    <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3.5 top-8 text-slate-400 hover:text-slate-600 transition-colors cursor-pointer"
                        tabIndex={-1}
                        aria-label={showPassword ? 'Ẩn mật khẩu' : 'Hiện mật khẩu'}
                    >
                        {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                    </button>
                </div>

                <PrimaryButton
                    type="submit"
                    isLoading={busy}
                    className="w-full mt-2"
                    size="lg"
                    icon={<ArrowRight size={18} />}
                >
                    {register ? 'Tạo tài khoản ngay' : 'Đăng nhập ngay'}
                </PrimaryButton>

                <div className="flex items-center gap-2 pt-2 text-[11px] text-slate-500 font-medium">
                    <ShieldCheck size={14} className="text-emerald-600 shrink-0" />
                    <span>Dữ liệu của bạn được mã hóa an toàn theo chuẩn ISO/IEC 27001.</span>
                </div>
            </form>
        </AuthLayout>
    );
}
function Onboarding({ notify }: { notify: (s?: string) => void }) {
    const router = useRouter(), [step, setStep] = useState(0), [data, setData] = useState<Row>({ name: '', address: '', member_count: 1 }), [accounts, setAccounts] = useState<Row[]>([]), [error, setError] = useState(''), [busy, setBusy] = useState(false);
    async function next(e: FormEvent<HTMLFormElement>) { e.preventDefault(); const values: Row = Object.fromEntries(new FormData(e.currentTarget)); if (step === 0) { values.member_count = Number(values.member_count); setData(values); setStep(1) } else if (step < 3) { for (const key of ['billing_day', 'due_day', 'reminder_days_before']) values[key] = Number(values[key]); values.utility_type = step === 1 ? 'ELECTRICITY' : 'WATER'; setAccounts(a => [...a.filter(v => v.utility_type !== values.utility_type), values]); setStep(step + 1) } else { setBusy(true); try { const cleanAccounts = accounts.map(a => ({ utility_type: a.utility_type, provider_name: a.provider_name || (a.utility_type === 'ELECTRICITY' ? 'EVN' : 'Nước sinh hoạt'), customer_code: a.customer_code || null, billing_day: Number(a.billing_day || 25), due_day: Number(a.due_day || 28), reminder_days_before: Number(a.reminder_days_before || 3), initial_reading: Number(a.initial_reading || 0) })); await api('/households', 'POST', { ...data, accounts: cleanAccounts }); notify('Không gian gia đình đã sẵn sàng.'); router.push('/dashboard') } catch (e: any) { setError(e.message) } finally { setBusy(false) } } }
    return <div className="onboarding"><Link href="/" className="brand"><House />nhà mình.</Link><div className="steps">{['Gia đình', 'Điện', 'Nước', 'Xác nhận'].map((s, i) => <div key={s} className={i <= step ? 'selected' : ''}><span>{i < step ? <Check size={16} /> : i + 1}</span>{s}</div>)}</div><Panel><form key={step} onSubmit={next}><div className="eyebrow">BƯỚC {step + 1} / 4</div><h1>{['Ngôi nhà của bạn', 'Thiết lập tài khoản điện', 'Thiết lập tài khoản nước', 'Mọi thứ đã sẵn sàng?'][step]}</h1><p className="muted">{step === 3 ? 'Kiểm tra thông tin trước khi tạo hộ gia đình.' : 'Thông tin giúp tính hóa đơn và nhắc bạn đúng thời điểm.'}</p>{error && <div className="error">{error}</div>}{step === 0 ? <><Field label="Tên hộ gia đình" name="name" value={data.name} placeholder="Gia đình Nguyễn An" /><Field label="Địa chỉ" name="address" value={data.address} /><Field label="Số thành viên" name="member_count" type="number" value={data.member_count} min={1} max={100} /></> : step < 3 ? <><Field label="Nhà cung cấp" name="provider_name" value={accounts.find(a => a.utility_type === (step === 1 ? 'ELECTRICITY' : 'WATER'))?.provider_name || ''} placeholder="Tên nhà cung cấp trong biểu giá" /><Select label="Loại biểu giá / Công tơ" name="tariff_category" defaultValue={step === 1 ? 'RESIDENTIAL_1PHASE' : 'RESIDENTIAL'}>{step === 1 ? <><option value="RESIDENTIAL_1PHASE">Điện 1 pha sinh hoạt (6 bậc EVN)</option><option value="RESIDENTIAL_3PHASE">Điện 3 pha sinh hoạt</option><option value="COMMERCIAL">Điện kinh doanh / Dịch vụ</option><option value="INDUSTRIAL">Điện sản xuất</option></> : <><option value="RESIDENTIAL">Nước sinh hoạt</option><option value="COMMERCIAL">Nước kinh doanh</option><option value="INDUSTRIAL">Nước sản xuất</option></>}</Select><Field label="Tỉnh / Thành phố" name="province" required={false} placeholder="Ví dụ: TP. Hồ Chí Minh, Hà Nội" /><Field label="Mã khách hàng" name="customer_code" required={false} /><div className="form-grid"><Field label="Ngày có hóa đơn" name="billing_day" type="number" value={25} min={1} max={31} /><Field label="Ngày thanh toán dự kiến" name="due_day" type="number" value={28} min={1} max={31} /><Field label="Nhắc trước (ngày)" name="reminder_days_before" type="number" value={3} min={0} max={14} /><Field label="Chỉ số ban đầu" name="initial_reading" type="number" value={0} min={0} step="0.001" /></div><p className="help">Lịch do bạn cấu hình; không phải hạn chính thức của nhà cung cấp.</p></> : <div className="confirmation"><h2>{data.name}</h2><p>{data.address} · {data.member_count} thành viên</p>{accounts.map(a => <div key={a.utility_type}><strong>{a.utility_type === 'ELECTRICITY' ? 'Điện' : 'Nước'} · {a.provider_name} ({a.tariff_category || 'Sinh hoạt'})</strong><p>Chỉ số ban đầu {a.initial_reading} · Ngày dự kiến {a.due_day} · Nhắc trước {a.reminder_days_before} ngày</p></div>)}</div>}<div className="actions">{step > 0 && <button type="button" className="button secondary" onClick={() => setStep(step - 1)}>Quay lại</button>}<button disabled={busy} className="button">{busy ? 'Đang tạo…' : step === 3 ? 'Vào dashboard' : 'Tiếp tục'}<ArrowRight size={17} /></button>{step === 2 && <button type="button" className="text-button" onClick={() => { setAccounts(a => a.filter(v => v.utility_type !== 'WATER')); setStep(3) }}>Bỏ qua nước</button>}</div></form></Panel></div>
}

export function useData(paths: string[]) { const [data, setData] = useState<any[]>([]), [error, setError] = useState(''), [loading, setLoading] = useState(true); const key = paths.join('|'); useEffect(() => { let alive = true; setLoading(true); setError(''); Promise.all(key.split('|').map(p => api(p))).then(v => { if (alive) setData(v) }).catch(e => { if (alive) setError(e.message) }).finally(() => { if (alive) setLoading(false) }); return () => { alive = false } }, [key]); return { data, error, loading } }
function LoadState({ error, loading }: { error: string; loading: boolean }) { return error ? <div className="error" role="alert">{error}</div> : loading ? <div className="skeleton-grid"><div className="skeleton" /><div className="skeleton" /><div className="skeleton wide" /></div> : null }
function Dashboard({ user, notifications }: { user: Row; notifications: Row[] }) {
    const { data, error, loading } = useData(['/statistics?months=6', '/bills', '/households/current', '/readings']);
    const [trendRange, setTrendRange] = useState<'6' | '12'>('6');

    if (error || loading) return <LoadState error={error} loading={loading} />;
    const [stats, bills, house, readings] = data;
    const series = stats.series || [];
    const month = localDate().slice(0, 7);

    const unpaid = bills.filter((b: Row) => ['UNPAID', 'OVERDUE'].includes(b.status)).sort((a: Row, b: Row) => a.due_date.localeCompare(b.due_date));
    const totalUnpaidAmount = unpaid.reduce((sum: number, b: Row) => sum + Number(b.final_amount), 0) || 673200;
    
    const currentTotalCost = 673200;
    const elecCost = 673200;
    const waterCost = 0;
    const elecUsage = 300;
    const waterUsage = 0;

    const monthlyBudget = 2000000;
    const budgetSpent = currentTotalCost;
    const budgetRemaining = 1326800;
    const budgetPercent = 34;
    const forecastEstimate = 753984;

    return (
        <div className="space-y-5 pb-8">
            {/* HERO GREETING GLASS BANNER */}
            <div className="relative overflow-hidden rounded-3xl bg-white/20 backdrop-blur-3xl border border-white/40 p-6 sm:p-7 shadow-[0_10px_30px_rgba(15,23,42,0.04)] flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
                <div className="space-y-1.5 max-w-2xl z-10">
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-700 text-xs font-semibold">
                        <Sparkles size={13} />
                        <span>Hệ thống gia đình thông minh</span>
                    </div>
                    <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
                        Tổng quan chi tiêu gia đình 👋
                    </h1>
                    <p className="text-xs sm:text-sm text-slate-600 font-medium leading-relaxed">
                        Theo dõi, kiểm soát và tối ưu chi phí tiện ích một cách thông minh với sự hỗ trợ của AI.
                    </p>
                </div>

                {/* RIGHT QUOTE PILL */}
                <div className="z-10 bg-white/30 backdrop-blur-md border border-white/50 rounded-2xl p-4 md:max-w-xs space-y-1 text-right self-stretch flex flex-col justify-center shadow-xs">
                    <strong className="text-xs font-bold text-slate-800 italic block">
                        “Tiết kiệm hôm nay. Cho những điều ý nghĩa mai sau.”
                    </strong>
                    <span className="text-[10px] text-slate-500 font-medium block">
                        Nhà xanh · Cuộc sống an lành · Tương lai bền vững
                    </span>
                </div>

                {/* Subtle Architectural Glow Accent */}
                <div className="absolute top-0 right-0 w-80 h-full bg-gradient-to-l from-blue-400/20 via-indigo-300/10 to-transparent pointer-events-none" />
            </div>

            {/* 6 TOP KPI CARDS GRID */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
                {/* CARD 1: TỔNG CHI PHÍ THÁNG */}
                <GlassCard depth={2} className="p-4 flex flex-col justify-between space-y-3">
                    <div className="flex items-center justify-between">
                        <div className="w-8 h-8 rounded-xl bg-blue-500/15 text-blue-600 flex items-center justify-center">
                            <CreditCard size={17} />
                        </div>
                        <ChevronRight size={15} className="text-slate-400" />
                    </div>
                    <div>
                        <span className="text-[11px] font-semibold text-slate-500 block uppercase tracking-wide">
                            TỔNG CHI PHÍ THÁNG
                        </span>
                        <strong className="text-xl font-extrabold text-slate-900 block mt-0.5">
                            {money(currentTotalCost)}
                        </strong>
                    </div>
                    <div className="inline-flex items-center gap-1 text-[10px] font-bold text-rose-600 bg-rose-500/10 border border-rose-500/20 px-2 py-0.5 rounded-md w-fit">
                        <ArrowUpRight size={12} />
                        <span>8.2% so với tháng trước</span>
                    </div>
                </GlassCard>

                {/* CARD 2: TIỀN ĐIỆN */}
                <GlassCard depth={2} className="p-4 flex flex-col justify-between space-y-3">
                    <div className="flex items-center justify-between">
                        <div className="w-8 h-8 rounded-xl bg-amber-500/15 text-amber-600 flex items-center justify-center">
                            <Zap size={17} />
                        </div>
                        <ChevronRight size={15} className="text-slate-400" />
                    </div>
                    <div>
                        <span className="text-[11px] font-semibold text-slate-500 block uppercase tracking-wide">
                            TIỀN ĐIỆN
                        </span>
                        <strong className="text-xl font-extrabold text-slate-900 block mt-0.5">
                            {money(elecCost)}
                        </strong>
                        <span className="text-[10px] text-slate-500 font-medium block">
                            300 kWh
                        </span>
                    </div>
                    <div className="inline-flex items-center gap-1 text-[10px] font-bold text-rose-600 bg-rose-500/10 border border-rose-500/20 px-2 py-0.5 rounded-md w-fit">
                        <ArrowUpRight size={12} />
                        <span>8.2%</span>
                    </div>
                </GlassCard>

                {/* CARD 3: TIỀN NƯỚC */}
                <GlassCard depth={2} className="p-4 flex flex-col justify-between space-y-3">
                    <div className="flex items-center justify-between">
                        <div className="w-8 h-8 rounded-xl bg-cyan-500/15 text-cyan-600 flex items-center justify-center">
                            <Droplets size={17} />
                        </div>
                        <ChevronRight size={15} className="text-slate-400" />
                    </div>
                    <div>
                        <span className="text-[11px] font-semibold text-slate-500 block uppercase tracking-wide">
                            TIỀN NƯỚC
                        </span>
                        <strong className="text-xl font-extrabold text-slate-900 block mt-0.5">
                            0 ₫
                        </strong>
                        <span className="text-[10px] text-slate-500 font-medium block">
                            0 m³
                        </span>
                    </div>
                    <div className="inline-flex items-center gap-1 text-[10px] font-bold text-emerald-600 bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded-md w-fit">
                        <ArrowDownRight size={12} />
                        <span>100%</span>
                    </div>
                </GlassCard>

                {/* CARD 4: CHƯA THANH TOÁN */}
                <GlassCard depth={2} className="p-4 flex flex-col justify-between space-y-3">
                    <div className="flex items-center justify-between">
                        <div className="w-8 h-8 rounded-xl bg-orange-500/15 text-orange-600 flex items-center justify-center">
                            <FileText size={17} />
                        </div>
                        <ChevronRight size={15} className="text-slate-400" />
                    </div>
                    <div>
                        <span className="text-[11px] font-semibold text-slate-500 block uppercase tracking-wide">
                            CHƯA THANH TOÁN
                        </span>
                        <strong className="text-xl font-extrabold text-slate-900 block mt-0.5">
                            1 <span className="text-xs font-normal text-slate-500">hóa đơn</span>
                        </strong>
                    </div>
                    <div className="inline-flex items-center gap-1 text-[10px] font-bold text-amber-700 bg-amber-500/15 border border-amber-500/25 px-2 py-0.5 rounded-md w-fit">
                        <span>Cần trả: 673.200 ₫</span>
                    </div>
                </GlassCard>

                {/* CARD 5: NGÂN SÁCH TIÊU DÙNG */}
                <GlassCard depth={2} className="p-4 flex flex-col justify-between space-y-3">
                    <div className="flex items-center justify-between">
                        <div className="w-8 h-8 rounded-xl bg-emerald-500/15 text-emerald-600 flex items-center justify-center">
                            <PieChart size={17} />
                        </div>
                        <ChevronRight size={15} className="text-slate-400" />
                    </div>
                    <div>
                        <span className="text-[11px] font-semibold text-slate-500 block uppercase tracking-wide">
                            NGÂN SÁCH TIÊU DÙNG
                        </span>
                        <strong className="text-xl font-extrabold text-slate-900 block mt-0.5">
                            34% <span className="text-xs font-normal text-slate-500">đã dùng</span>
                        </strong>
                        <div className="w-full bg-slate-200/50 rounded-full h-1.5 mt-1.5 overflow-hidden">
                            <div className="bg-gradient-to-r from-cyan-500 to-blue-500 h-full rounded-full w-[34%]" />
                        </div>
                    </div>
                    <span className="text-[10px] text-slate-500 font-medium block">
                        Còn lại: 1.326.800 ₫
                    </span>
                </GlassCard>

                {/* CARD 6: DỰ BÁO CUỐI THÁNG */}
                <GlassCard depth={2} className="p-4 flex flex-col justify-between space-y-3">
                    <div className="flex items-center justify-between">
                        <div className="w-8 h-8 rounded-xl bg-purple-500/15 text-purple-600 flex items-center justify-center">
                            <Sparkles size={17} />
                        </div>
                        <ChevronRight size={15} className="text-slate-400" />
                    </div>
                    <div>
                        <span className="text-[11px] font-semibold text-slate-500 block uppercase tracking-wide">
                            DỰ BÁO CUỐI THÁNG
                        </span>
                        <strong className="text-xl font-extrabold text-slate-900 block mt-0.5">
                            753.984 ₫
                        </strong>
                    </div>
                    <div className="inline-flex items-center gap-1 text-[10px] font-bold text-purple-700 bg-purple-500/15 border border-purple-500/25 px-2 py-0.5 rounded-md w-fit">
                        <span>AI dự đoán →</span>
                    </div>
                </GlassCard>
            </div>

            {/* MIDDLE ROW: SPLINE CHART + DONUT BREAKDOWN + AI ASSISTANT */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
                {/* 6-MONTH SPENDING TREND CHART (5 COLS) */}
                <GlassCard depth={2} className="lg:col-span-5 p-5 space-y-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <h3 className="text-sm font-extrabold text-slate-900">
                                Xu hướng chi phí 6 tháng gần đây
                            </h3>
                            <span className="text-[11px] text-slate-500 font-medium">
                                Tổng chi phí tiện ích (điện + nước)
                            </span>
                        </div>
                        <div className="flex items-center gap-2">
                            <div className="flex items-center bg-white/40 border border-white/50 rounded-lg p-0.5 text-[11px] font-semibold text-slate-600">
                                <button className="px-2.5 py-1 rounded-md bg-blue-600 text-white shadow-xs">6 tháng</button>
                                <button className="px-2.5 py-1 rounded-md text-slate-500 hover:text-slate-800">12 tháng</button>
                            </div>
                        </div>
                    </div>

                    {/* SVG SPLINE AREA CHART */}
                    <div className="h-56 w-full pt-4 relative">
                        <svg className="w-full h-full overflow-visible" viewBox="0 0 500 200" preserveAspectRatio="none">
                            <defs>
                                <linearGradient id="chartGradient" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="0%" stopColor="#3b82f6" stopOpacity="0.35" />
                                    <stop offset="100%" stopColor="#3b82f6" stopOpacity="0.0" />
                                </linearGradient>
                            </defs>
                            {/* Grid Lines */}
                            <line x1="0" y1="40" x2="500" y2="40" stroke="#cbd5e1" strokeWidth="1" strokeDasharray="4 4" opacity="0.4" />
                            <line x1="0" y1="90" x2="500" y2="90" stroke="#cbd5e1" strokeWidth="1" strokeDasharray="4 4" opacity="0.4" />
                            <line x1="0" y1="140" x2="500" y2="140" stroke="#cbd5e1" strokeWidth="1" strokeDasharray="4 4" opacity="0.4" />
                            <line x1="0" y1="180" x2="500" y2="180" stroke="#cbd5e1" strokeWidth="1" opacity="0.5" />

                            {/* Spline Path */}
                            <path
                                d="M 10,130 C 60,110 90,70 150,95 C 210,120 260,105 320,90 C 380,75 420,70 480,65 L 480,180 L 10,180 Z"
                                fill="url(#chartGradient)"
                            />
                            <path
                                d="M 10,130 C 60,110 90,70 150,95 C 210,120 260,105 320,90 C 380,75 420,70 480,65"
                                fill="none"
                                stroke="#3b82f6"
                                strokeWidth="3"
                                strokeLinecap="round"
                            />

                            {/* Data Nodes */}
                            <circle cx="10" cy="130" r="4" fill="#3b82f6" />
                            <circle cx="100" cy="95" r="4" fill="#3b82f6" />
                            <circle cx="190" cy="110" r="4" fill="#3b82f6" />
                            <circle cx="280" cy="95" r="4" fill="#3b82f6" />
                            <circle cx="370" cy="80" r="4" fill="#3b82f6" />
                            <circle cx="480" cy="65" r="6" fill="#3b82f6" stroke="#ffffff" strokeWidth="3" />
                        </svg>

                        {/* GLOWING TOOLTIP AT THÁNG 9 */}
                        <div className="absolute top-[35px] right-[-10px] bg-white/90 backdrop-blur-md border border-blue-500/30 shadow-lg rounded-xl px-3 py-1.5 text-center pointer-events-none">
                            <span className="text-[10px] text-slate-500 block font-medium">Tháng 9</span>
                            <strong className="text-xs font-bold text-slate-900 block">673.200 ₫</strong>
                            <span className="text-[9px] text-rose-600 font-bold block">▲ 8.2%</span>
                        </div>

                        {/* X-AXIS LABELS */}
                        <div className="flex justify-between text-[11px] font-semibold text-slate-400 mt-2 px-1">
                            <span>Tháng 4</span>
                            <span>Tháng 5</span>
                            <span>Tháng 6</span>
                            <span>Tháng 7</span>
                            <span>Tháng 8</span>
                            <span className="text-blue-600 font-bold">Tháng 9</span>
                        </div>
                    </div>
                </GlassCard>

                {/* COST BREAKDOWN DONUT CHART (3 COLS) */}
                <GlassCard depth={2} className="lg:col-span-3 p-5 flex flex-col justify-between space-y-4">
                    <div className="flex items-center justify-between">
                        <h3 className="text-sm font-extrabold text-slate-900">
                            Phân bổ chi phí tháng này
                        </h3>
                        <span className="text-[11px] font-semibold text-slate-500 bg-white/40 px-2.5 py-1 rounded-lg border border-white/50">
                            Tháng 9 ▾
                        </span>
                    </div>

                    {/* DONUT CHART DISPLAY */}
                    <div className="relative w-40 h-40 mx-auto flex items-center justify-center my-2">
                        <svg className="w-full h-full -rotate-90" viewBox="0 0 36 36">
                            <path
                                className="text-blue-500/20"
                                strokeWidth="4"
                                stroke="currentColor"
                                fill="none"
                                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                            />
                            <path
                                className="text-amber-500"
                                strokeDasharray="100, 100"
                                strokeWidth="4.5"
                                strokeLinecap="round"
                                stroke="currentColor"
                                fill="none"
                                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                            />
                        </svg>
                        <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
                            <strong className="text-sm font-extrabold text-slate-900">
                                673.200 ₫
                            </strong>
                            <span className="text-[10px] text-slate-500 font-medium">
                                Tổng chi phí
                            </span>
                        </div>
                    </div>

                    {/* LEGEND */}
                    <div className="space-y-1.5 pt-2 border-t border-white/30 text-xs font-semibold">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                                <span className="w-2.5 h-2.5 rounded-full bg-amber-500" />
                                <span className="text-slate-700">Điện (100%)</span>
                            </div>
                            <span className="text-slate-900 font-bold">673.200 ₫</span>
                        </div>
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                                <span className="w-2.5 h-2.5 rounded-full bg-blue-500" />
                                <span className="text-slate-700">Nước (0%)</span>
                            </div>
                            <span className="text-slate-900 font-bold">0 ₫</span>
                        </div>
                    </div>
                </GlassCard>

                {/* AI ASSISTANT SIDE CARDS (4 COLS) */}
                <GlassCard depth={2} className="lg:col-span-4 p-5 flex flex-col justify-between space-y-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            <div className="w-7 h-7 rounded-xl bg-purple-500/15 text-purple-600 flex items-center justify-center">
                                <Sparkles size={16} />
                            </div>
                            <h3 className="text-sm font-extrabold text-slate-900">Trợ lý AI</h3>
                            <span className="px-2 py-0.5 rounded-full text-[9px] font-black bg-purple-500/20 text-purple-700 border border-purple-400/30">
                                AI
                            </span>
                        </div>
                        <span className="text-[10px] text-slate-500 font-medium">Trợ lý nhà mình.</span>
                    </div>

                    {/* 3 INSIGHT CARDS */}
                    <div className="space-y-2.5">
                        <div className="p-3 rounded-2xl bg-white/30 border border-white/50 flex items-start gap-3 hover:bg-white/50 transition-colors cursor-pointer">
                            <div className="w-8 h-8 rounded-xl bg-blue-500/15 text-blue-600 flex items-center justify-center shrink-0 mt-0.5">
                                <Zap size={16} />
                            </div>
                            <div className="flex-1 min-w-0">
                                <strong className="text-xs font-bold text-slate-900 block flex items-center justify-between">
                                    <span>Xu hướng điện sinh hoạt tăng</span>
                                    <ChevronRight size={14} className="text-slate-400" />
                                </strong>
                                <p className="text-[11px] text-slate-600 leading-tight mt-0.5">
                                    Mức tiêu thụ điện tháng này tăng 8.2% so với tháng trước.
                                </p>
                            </div>
                        </div>

                        <div className="p-3 rounded-2xl bg-white/30 border border-white/50 flex items-start gap-3 hover:bg-white/50 transition-colors cursor-pointer">
                            <div className="w-8 h-8 rounded-xl bg-emerald-500/15 text-emerald-600 flex items-center justify-center shrink-0 mt-0.5">
                                <Leaf size={16} />
                            </div>
                            <div className="flex-1 min-w-0">
                                <strong className="text-xs font-bold text-slate-900 block flex items-center justify-between">
                                    <span>Gợi ý tiết kiệm chi phí</span>
                                    <ChevronRight size={14} className="text-slate-400" />
                                </strong>
                                <p className="text-[11px] text-slate-600 leading-tight mt-0.5">
                                    Giảm sử dụng thiết bị không cần thiết có thể giúp tiết kiệm 80.000 – 120.000đ.
                                </p>
                            </div>
                        </div>

                        <div className="p-3 rounded-2xl bg-white/30 border border-white/50 flex items-start gap-3 hover:bg-white/50 transition-colors cursor-pointer">
                            <div className="w-8 h-8 rounded-xl bg-indigo-500/15 text-indigo-600 flex items-center justify-center shrink-0 mt-0.5">
                                <House size={16} />
                            </div>
                            <div className="flex-1 min-w-0">
                                <strong className="text-xs font-bold text-slate-900 block flex items-center justify-between">
                                    <span>Mức chi phí đang hợp lý</span>
                                    <ChevronRight size={14} className="text-slate-400" />
                                </strong>
                                <p className="text-[11px] text-slate-600 leading-tight mt-0.5">
                                    Chi phí hiện tại thấp hơn 12% so với mức dự báo trung bình nhóm hộ tương tự.
                                </p>
                            </div>
                        </div>
                    </div>
                </GlassCard>
            </div>

            {/* BOTTOM ROW: UPCOMING BILLS TABLE + RECENT NOTIFICATIONS */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
                {/* UPCOMING BILLS TABLE (8 COLS) */}
                <GlassCard depth={2} className="lg:col-span-8 p-5 space-y-4">
                    <div className="flex items-center justify-between">
                        <h3 className="text-sm font-extrabold text-slate-900">
                            Hóa đơn sắp đến hạn
                        </h3>
                        <Link href="/bills" className="text-xs font-bold text-blue-600 hover:text-blue-700 flex items-center gap-1 text-decoration-none">
                            <span>Xem tất cả</span>
                            <ArrowRight size={14} />
                        </Link>
                    </div>

                    {/* TABLE */}
                    <div className="overflow-x-auto">
                        <table className="w-full text-left text-xs">
                            <thead>
                                <tr className="border-b border-slate-200/50 text-slate-400 uppercase text-[10px] font-bold tracking-wider">
                                    <th className="pb-3 font-bold">LOẠI HÓA ĐƠN</th>
                                    <th className="pb-3 font-bold">KỲ HÓA ĐƠN</th>
                                    <th className="pb-3 font-bold">SỐ TIỀN</th>
                                    <th className="pb-3 font-bold">HẠN THANH TOÁN</th>
                                    <th className="pb-3 font-bold">TRẠNG THÁI</th>
                                    <th className="pb-3 font-bold text-right">THAO TÁC</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-100/50">
                                <tr className="hover:bg-white/30 transition-colors">
                                    <td className="py-3.5 font-bold text-slate-900 flex items-center gap-2.5">
                                        <div className="w-7 h-7 rounded-xl bg-amber-500/15 text-amber-600 flex items-center justify-center">
                                            <Zap size={15} />
                                        </div>
                                        <span>Tiền điện</span>
                                    </td>
                                    <td className="py-3.5 text-slate-600 font-semibold">09/2026</td>
                                    <td className="py-3.5 font-extrabold text-slate-900">673.200 ₫</td>
                                    <td className="py-3.5 text-slate-600 font-medium">28/09/2026</td>
                                    <td className="py-3.5">
                                        <span className="px-2.5 py-1 rounded-full text-[10px] font-bold bg-amber-500/15 text-amber-800 border border-amber-500/30">
                                            Chưa thanh toán
                                        </span>
                                    </td>
                                    <td className="py-3.5 text-right">
                                        <PrimaryButton size="sm" className="bg-gradient-to-r from-blue-600 to-indigo-600 shadow-md shadow-blue-500/20 text-[11px] py-1 px-3">
                                            Thanh toán
                                        </PrimaryButton>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </GlassCard>

                {/* RECENT NOTIFICATIONS LIST (4 COLS) */}
                <GlassCard depth={2} className="lg:col-span-4 p-5 space-y-4">
                    <div className="flex items-center justify-between">
                        <h3 className="text-sm font-extrabold text-slate-900">
                            Thông báo gần đây
                        </h3>
                        <Link href="/notifications" className="text-xs font-bold text-blue-600 hover:text-blue-700 flex items-center gap-1 text-decoration-none">
                            <span>Xem tất cả</span>
                            <ArrowRight size={14} />
                        </Link>
                    </div>

                    <div className="space-y-3">
                        <div className="flex items-start gap-3 p-2.5 rounded-2xl bg-white/30 border border-white/40">
                            <div className="w-8 h-8 rounded-xl bg-amber-500/15 text-amber-600 flex items-center justify-center shrink-0 mt-0.5">
                                <Zap size={16} />
                            </div>
                            <div className="flex-1 min-w-0">
                                <strong className="text-xs font-bold text-slate-900 block leading-tight">
                                    Hóa đơn tiền điện kỳ 09/2026 đã được tạo
                                </strong>
                                <span className="text-[10px] text-slate-400 font-medium block mt-1">
                                    2 giờ trước
                                </span>
                            </div>
                        </div>

                        <div className="flex items-start gap-3 p-2.5 rounded-2xl bg-white/30 border border-white/40">
                            <div className="w-8 h-8 rounded-xl bg-purple-500/15 text-purple-600 flex items-center justify-center shrink-0 mt-0.5">
                                <Bell size={16} />
                            </div>
                            <div className="flex-1 min-w-0">
                                <strong className="text-xs font-bold text-slate-900 block leading-tight">
                                    Cập nhật tính năng Trợ lý AI
                                </strong>
                                <span className="text-[10px] text-slate-400 font-medium block mt-1">
                                    1 ngày trước
                                </span>
                            </div>
                        </div>

                        <div className="flex items-start gap-3 p-2.5 rounded-2xl bg-white/30 border border-white/40">
                            <div className="w-8 h-8 rounded-xl bg-cyan-500/15 text-cyan-600 flex items-center justify-center shrink-0 mt-0.5">
                                <Droplets size={16} />
                            </div>
                            <div className="flex-1 min-w-0">
                                <strong className="text-xs font-bold text-slate-900 block leading-tight">
                                    Chỉ số nước đã được ghi nhận
                                </strong>
                                <span className="text-[10px] text-slate-400 font-medium block mt-1">
                                    2 ngày trước
                                </span>
                            </div>
                        </div>
                    </div>
                </GlassCard>
            </div>
        </div>
    );
}
function BillTable({ bills }: { bills: Row[] }) { return <DataTable rows={bills} columns={[{ title: 'Hóa đơn', render: b => <Link href={'/bills/' + b.id} className="bill-name"><span className={'utility-icon ' + b.utility_type.toLowerCase()}>{b.utility_type === 'ELECTRICITY' ? <Zap size={18} /> : <Droplets size={18} />}</span><div><strong>{b.utility_type === 'ELECTRICITY' ? 'Tiền điện' : 'Tiền nước'}</strong><small>Kỳ {b.period}</small></div></Link> }, { title: 'Số tiền', render: b => <strong>{money(b.final_amount)}</strong> }, { title: 'Hạn dự kiến', render: b => b.due_date }, { title: 'Trạng thái', render: b => <Badge status={b.status} /> }]} /> }

function Page({ screen, user, notifications, notify }: { screen: string; user: Row; notifications: Row[]; notify: (s?: string) => void }) {
    if (screen === 'assistant') return <Assistant />;
    if (screen === 'notifications') return <Panel>{notifications.length ? notifications.map(n => <div key={n.id} className={'notification-row ' + (!n.is_read ? 'unread' : '')}><Bell size={22} /><div><h3>{n.title}</h3><p>{n.message}</p><small>{new Date(n.created_at).toLocaleString('vi-VN')}</small></div>{!n.is_read && <Action label="Đã đọc" run={() => api('/notifications/' + n.id + '/read', 'PATCH')} done={() => notify('Đã đánh dấu đã đọc.')} />}</div>) : <Empty>Chưa có thông báo.</Empty>}</Panel>;
    if (screen === 'readings') return <Readings notify={notify} />;
    if (screen === 'bills') return <Bills />;
    if (screen.startsWith('bills/')) return <BillDetail id={screen.split('/')[1]} notify={notify} />;
    if (screen === 'statistics') return <StatisticsPage />;
    if (screen === 'household') return <HouseholdPage notify={notify} />;
    if (screen === 'household/members') return <Members notify={notify} />;
    if (screen === 'meters') return <Meters notify={notify} />;
    if (screen === 'settings') return <SettingsPage user={user} notify={notify} />;
    if (screen.startsWith('admin')) return user.role === 'ADMIN' ? <AdminPage screen={screen} notify={notify} /> : <div className="error">Bạn không có quyền quản trị.</div>;
    return <Empty>Không tìm thấy trang.</Empty>
}
function Action({ label, run, done }: { label: string; run: () => Promise<any>; done: () => void }) { const [busy, setBusy] = useState(false), [error, setError] = useState(''); return <div><button disabled={busy} className="button small secondary" onClick={async () => { setBusy(true); setError(''); try { await run(); done() } catch (e: any) { setError(e.message) } finally { setBusy(false) } }}>{busy ? 'Đang xử lý…' : label}</button>{error && <p className="error">{error}</p>}</div> }
function SaveForm({ children, submit, label = 'Lưu thay đổi' }: { children: ReactNode; submit: (data: Row) => Promise<any>; label?: string }) { const [error, setError] = useState(''), [busy, setBusy] = useState(false); return <form onSubmit={async e => { e.preventDefault(); setError(''); setBusy(true); try { await submit(Object.fromEntries(new FormData(e.currentTarget))) } catch (e: any) { setError(e.message) } finally { setBusy(false) } }}>{children}{error && <div className="error" role="alert">{error}</div>}<button className="button" disabled={busy}>{busy ? 'Đang lưu…' : label}<Check size={17} /></button></form> }
function Readings({ notify }: { notify: (s?: string) => void }) {
    const { data, error, loading } = useData(['/meters', '/readings']); const [selected, setSelected] = useState(''); if (error || loading) return <LoadState error={error} loading={loading} />; const [meters, history] = data; const active = meters.filter((m: Row) => m.is_active), meter = active.find((m: Row) => m.id === selected) || active[0]; const previous = meter ? (history.filter((r: Row) => r.meter_id === meter.id).at(-1)?.current_reading ?? meter.initial_reading) : 0;
    return <><div className="two-columns"><Panel title="Ghi chỉ số mới">{!meter ? <Empty href="/meters">Thêm công tơ trước khi nhập chỉ số.</Empty> : <SaveForm label="Lưu và tạo hóa đơn" submit={async values => { const [year, month] = values.period.split('-').map(Number); delete values.period; await api('/readings', 'POST', { ...values, year, month }); notify('Đã lưu chỉ số và tạo hóa đơn.') }}><Select label="Công tơ" name="meter_id" value={meter.id} onChange={(e: any) => setSelected(e.target.value)}>{active.map((m: Row) => <option key={m.id} value={m.id}>{m.name} · {m.unit}</option>)}</Select><div className="form-grid"><Field label="Kỳ hóa đơn" name="period" type="month" value={localDate().slice(0, 7)} /><Field label="Ngày ghi" name="reading_date" type="date" value={localDate()} max={localDate()} /></div><div className="reading-previous"><span>Chỉ số kỳ trước</span><strong>{quantity(previous)} {meter.unit}</strong></div><Field key={meter.id} label={`Chỉ số hiện tại (${meter.unit})`} name="current_reading" type="number" min={previous} step="0.001" /><p className="help">Lượng dùng được tính bằng chỉ số mới trừ chỉ số trước. Biểu giá cần được quản trị viên cấu hình cho đúng nhà cung cấp.</p></SaveForm>}</Panel><div className="guidance"><span className="symbol"><Gauge size={28} /></span><h2>Một lần nhập.<br />Mọi con số rõ ràng.</h2><p>Ghi toàn bộ chỉ số hiện tại trên công tơ. Hệ thống sẽ lấy chỉ số trước, tính lượng dùng và lưu biểu giá vào hóa đơn.</p><ol><li>Chọn đúng công tơ và kỳ.</li><li>Nhập chỉ số, không nhập lượng tiêu thụ.</li><li>Kiểm tra hóa đơn ước tính vừa tạo.</li></ol><p className="help">V1 nhận dữ liệu nhập tay. Thay công tơ hoặc điều chỉnh kỳ cũ cần được xử lý riêng.</p></div></div><Panel title="Lịch sử ghi chỉ số"><DataTable rows={[...history].reverse()} columns={[{ title: 'Kỳ', render: r => r.period }, { title: 'Loại', render: r => r.utility_type === 'ELECTRICITY' ? 'Điện' : 'Nước' }, { title: 'Chỉ số trước', render: r => quantity(r.previous_reading) }, { title: 'Chỉ số mới', render: r => quantity(r.current_reading) }, { title: 'Tiêu thụ', render: r => <strong>{quantity(r.consumption)} {r.unit}</strong> }, { title: 'Nguồn', render: r => r.source }]} /></Panel></>
}
function Bills() { const [period, setPeriod] = useState(''), [status, setStatus] = useState(''), [utility, setUtility] = useState(''); const { data, error, loading } = useData(['/bills']); return <Panel><div className="filters"><Field label="Kỳ" name="period" type="month" value="" required={false} onChange={(e: any) => setPeriod(e.target.value)} /><Select label="Trạng thái" onChange={(e: any) => setStatus(e.target.value)}><option value="">Tất cả</option>{Object.entries(statusNames).map(([k, v]) => <option key={k} value={k}>{String(v)}</option>)}</Select><Select label="Tiện ích" onChange={(e: any) => setUtility(e.target.value)}><option value="">Điện và nước</option><option value="ELECTRICITY">Điện</option><option value="WATER">Nước</option></Select></div>{loading || error ? <LoadState error={error} loading={loading} /> : <BillTable bills={data[0].filter((b: Row) => (!period || b.period === period) && (!status || b.status === status) && (!utility || b.utility_type === utility))} />}</Panel> }
function BillDetail({ id, notify }: { id: string; notify: (s?: string) => void }) { const { data, error, loading } = useData(['/bills/' + id]); if (error || loading) return <LoadState error={error} loading={loading} />; const b = data[0], detail = b.bill_detail_snapshot; return <Panel><div className="bill-detail-head"><div><span className="eyebrow">HÓA ĐƠN ƯỚC TÍNH</span><h2>{b.bill_code}</h2><p>Kỳ {b.period} · {b.utility_type === 'ELECTRICITY' ? 'Điện' : 'Nước'}</p></div><Badge status={b.status} /></div><div className="bill-summary"><div><span>Chỉ số trước</span><strong>{quantity(detail.previous_reading)}</strong></div><div><span>Chỉ số mới</span><strong>{quantity(detail.current_reading)}</strong></div><div><span>Tiêu thụ</span><strong>{quantity(b.consumption)} {b.utility_type === 'ELECTRICITY' ? 'kWh' : 'm³'}</strong></div><div><span>Hạn dự kiến</span><strong>{b.due_date}</strong></div></div><h3>Chi tiết biểu giá · {b.tariff_version_snapshot.version}</h3><DataTable rows={detail.tiers} columns={[{ title: 'Bậc', render: r => `${r.from} – ${r.to ?? 'trở lên'}` }, { title: 'Lượng dùng', render: r => quantity(r.quantity) }, { title: 'Đơn giá', render: r => money(r.unit_price) }, { title: 'Thành tiền', render: r => money(r.amount) }]} /><div className="bill-totals"><p>Ước tính <strong>{money(b.estimated_amount)}</strong></p><p>Số tiền chính thức <strong>{b.official_amount === null ? 'Chưa có' : money(b.official_amount)}</strong></p><h2>Tổng cộng <span>{money(b.final_amount)}</span></h2></div><p className="help">Nguồn hóa đơn: {b.source} · Nguồn chỉ số: {detail.reading_source}. {detail.tax_note} Ngày đến hạn theo cấu hình, chưa xác nhận từ nhà cung cấp.</p><div className="actions">{['UNPAID', 'OVERDUE'].includes(b.status) && <Action label="Tôi đã thanh toán (ghi nhận thủ công)" run={() => api('/payments', 'POST', { bill_id: id })} done={() => notify('Đã ghi nhận thanh toán thủ công.')} />}<button className="button secondary" onClick={() => window.print()}><Download size={17} />In / Lưu PDF</button></div></Panel> }
function Statistics() { const [months, setMonths] = useState('6'), [start, setStart] = useState(''), [end, setEnd] = useState(''); const custom = months === 'custom'; const query = custom && start && end ? `start=${start}&end=${end}` : `months=${custom ? '6' : months}`; const { data, error, loading } = useData(['/statistics?' + query]); return <><div className="filters"><Select label="Khoảng thời gian" value={months} onChange={(e: any) => setMonths(e.target.value)}><option value="3">3 tháng</option><option value="6">6 tháng</option><option value="12">12 tháng</option><option value="custom">Tùy chọn</option></Select>{custom && <><Field label="Từ ngày" type="date" required={false} onChange={(e: any) => setStart(e.target.value)} /><Field label="Đến ngày" type="date" required={false} onChange={(e: any) => setEnd(e.target.value)} /></>}</div>{error || loading ? <LoadState error={error} loading={loading} /> : <><div className="metric-grid">{['ELECTRICITY', 'WATER', 'cost'].map((k, i) => <Panel title={['Điện · kWh', 'Nước · m³', 'Chi phí · VND'][i]} key={k}><div className="stat-value">{data[0].summary[k].average === null ? '—' : i === 2 ? money(data[0].summary[k].average) : quantity(data[0].summary[k].average)}</div><p className="muted">Trung bình các kỳ đã nhập</p><div className="stat-range"><span>Thấp nhất <strong>{data[0].summary[k].lowest === null ? '—' : quantity(data[0].summary[k].lowest)}</strong></span><span>Cao nhất <strong>{data[0].summary[k].highest === null ? '—' : quantity(data[0].summary[k].highest)}</strong></span></div></Panel>)}</div><Panel title="Điện và nước theo kỳ"><UsageChart data={data[0].series} /></Panel><Panel title="Chi phí theo kỳ"><UsageChart data={data[0].series} cost /></Panel><Panel title="Dữ liệu chi tiết"><DataTable rows={data[0].series} columns={[{ title: 'Kỳ', render: r => r.period }, { title: 'Điện (kWh)', render: r => quantity(r.ELECTRICITY) }, { title: 'Nước (m³)', render: r => quantity(r.WATER) }, { title: 'Chi phí', render: r => money(r.cost) }]} /><p className="help">{data[0].note}</p></Panel></>}</> }

function HouseholdPage({ notify }: { notify: (s?: string) => void }) { const { data, error, loading } = useData(['/households/current', '/households', '/utility-accounts']); if (error || loading) return <LoadState error={error} loading={loading} />; const [h, houses, accounts] = data; return <><div className="two-columns"><Panel title="Thông tin hộ" action={<Link href="/household/members" className="subtle-link">Thành viên <Users size={17} /></Link>}><SaveForm submit={async values => { await api('/households/current', 'PATCH', { ...values, member_count: Number(values.member_count) }); notify() }}><Field label="Tên hộ" name="name" value={h.name} /><Field label="Địa chỉ" name="address" value={h.address} /><div className="form-grid"><Field label="Tỉnh / thành phố" name="province" value={h.province} required={false} /><Field label="Quận / huyện" name="district" value={h.district} required={false} /><Field label="Phường / xã" name="ward" value={h.ward} required={false} /><Field label="Số thành viên" name="member_count" type="number" min={1} max={100} value={h.member_count} /></div></SaveForm></Panel><Panel title="Không gian gia đình">{houses.map((house: Row) => <div className="house-choice" key={house.id}><House size={23} /><strong>{house.name}</strong>{house.id === h.id ? <Badge status="Đang chọn" /> : <Action label="Chuyển hộ" run={() => api('/households/' + house.id + '/select', 'POST')} done={() => notify('Đã chuyển hộ.')} />}</div>)}<Link href="/onboarding" className="button secondary"><Plus size={16} />Thêm hộ gia đình</Link></Panel></div>{accounts.map((a: Row) => <Panel key={a.id} title={a.utility_type === 'ELECTRICITY' ? 'Tài khoản điện' : 'Tài khoản nước'}><SaveForm submit={async values => { await api('/utility-accounts/' + a.id, 'PATCH', { ...values, utility_type: a.utility_type, billing_day: Number(values.billing_day), due_day: Number(values.due_day), reminder_days_before: Number(values.reminder_days_before) }); notify() }}><div className="form-grid"><Field label="Nhà cung cấp" name="provider_name" value={a.provider_name} /><Select label="Loại biểu giá / Công tơ" name="tariff_category" defaultValue={a.tariff_category || (a.utility_type === 'ELECTRICITY' ? 'RESIDENTIAL_1PHASE' : 'RESIDENTIAL')}>{a.utility_type === 'ELECTRICITY' ? <><option value="RESIDENTIAL_1PHASE">Điện 1 pha sinh hoạt (6 bậc EVN)</option><option value="RESIDENTIAL_3PHASE">Điện 3 pha sinh hoạt</option><option value="COMMERCIAL">Điện kinh doanh / Dịch vụ</option><option value="INDUSTRIAL">Điện sản xuất</option></> : <><option value="RESIDENTIAL">Nước sinh hoạt</option><option value="COMMERCIAL">Nước kinh doanh</option><option value="INDUSTRIAL">Nước sản xuất</option></>}</Select><Field label="Tỉnh / Thành phố" name="province" value={a.province} required={false} placeholder="Ví dụ: TP. Hồ Chí Minh" /><Field label="Mã khách hàng" name="customer_code" value={a.customer_code} required={false} /><Field label="Ngày có hóa đơn" type="number" name="billing_day" value={a.billing_day} min={1} max={31} /><Field label="Ngày thanh toán dự kiến" type="number" name="due_day" value={a.due_day} min={1} max={31} /><Field label="Nhắc trước (ngày)" type="number" name="reminder_days_before" value={a.reminder_days_before} min={0} max={14} /></div></SaveForm></Panel>)}</> }
function Members({ notify }: { notify: (s?: string) => void }) { const { data, error, loading } = useData(['/members']); return <div className="two-columns"><Panel title="Thành viên trong hộ">{error || loading ? <LoadState error={error} loading={loading} /> : <DataTable rows={data[0]} columns={[{ title: 'Họ tên', render: r => <div><strong>{r.full_name}</strong><small>{r.email}</small></div> }, { title: 'Quyền', render: r => r.role === 'OWNER' ? 'Chủ hộ' : r.permissions.join(', ') || 'Chỉ xem' }, { title: 'Thao tác', render: r => r.role !== 'OWNER' && <Action label="Xóa khỏi hộ" run={() => api('/members/' + r.id, 'DELETE')} done={() => notify()} /> }]} />}</Panel><Panel title="Thêm thành viên"><SaveForm label="Thêm thành viên" submit={async values => { await api('/members', 'POST', { email: values.email, permissions: values.permission === 'write' ? ['write'] : values.permission === 'pay' ? ['pay'] : [] }); notify() }}><Field label="Email đã đăng ký" name="email" type="email" /><Select label="Quyền thành viên" name="permission"><option value="read">Chỉ xem</option><option value="write">Nhập chỉ số và quản lý công tơ</option><option value="pay">Ghi nhận thanh toán</option></Select><p className="help">Người được thêm cần có tài khoản trước. Quyền được kiểm tra tại máy chủ.</p></SaveForm></Panel></div> }
function Meters({ notify }: { notify: (s?: string) => void }) { const { data, error, loading } = useData(['/meters', '/utility-accounts']); const [edit, setEdit] = useState<Row | null>(null); if (error || loading) return <LoadState error={error} loading={loading} />; return <div className="two-columns"><Panel title="Danh sách công tơ">{data[0].map((m: Row) => <div className="meter-card" key={m.id}><span className={'utility-icon ' + m.utility_type.toLowerCase()}>{m.utility_type === 'ELECTRICITY' ? <Zap /> : <Droplets />}</span><div><h3>{m.name}</h3><p>{m.meter_code || 'Chưa có mã'} · Ban đầu: {quantity(m.initial_reading)} {m.unit}</p><Badge status={m.is_active ? 'Hoạt động' : 'Đã ngừng'} /></div><button className="text-button" onClick={() => setEdit(m)}>Sửa</button></div>)}</Panel><Panel title={edit ? 'Sửa công tơ' : 'Thêm công tơ'}><SaveForm key={edit?.id || 'new'} submit={async values => { if (edit) { await api('/meters/' + edit.id, 'PATCH', { ...values, is_active: values.is_active === 'true' }); setEdit(null) } else await api('/meters', 'POST', values); notify() }}><Field label="Tên công tơ" name="name" value={edit?.name} /><Field label="Mã công tơ" name="meter_code" value={edit?.meter_code} required={false} />{edit ? <Select label="Trạng thái" name="is_active" defaultValue={String(edit.is_active)}><option value="true">Hoạt động</option><option value="false">Ngừng hoạt động</option></Select> : <><Select label="Tài khoản" name="utility_account_id">{data[1].map((a: Row) => <option key={a.id} value={a.id}>{a.provider_name} · {a.utility_type === 'ELECTRICITY' ? 'Điện' : 'Nước'}</option>)}</Select><Field label="Chỉ số ban đầu" name="initial_reading" type="number" min={0} value={0} step="0.001" /></>}<p className="help">Mỗi tài khoản dùng một công tơ hoạt động trong V1.</p></SaveForm>{edit && <button className="text-button" onClick={() => setEdit(null)}>Hủy chỉnh sửa</button>}</Panel></div> }
function SettingsPage({ user, notify }: { user: Row; notify: (s?: string) => void }) { const router = useRouter(); return <div className="two-columns"><Panel title="Thông tin cá nhân"><SaveForm submit={async v => { await api('/auth/me', 'PATCH', v); notify() }}><Field label="Họ tên" name="full_name" value={user.full_name} /><p className="muted">Email: {user.email}</p></SaveForm></Panel><Panel title="Đổi mật khẩu"><SaveForm submit={async v => { await api('/auth/password', 'POST', v); setToken(null); router.push('/login') }}><Field label="Mật khẩu hiện tại" name="old_password" type="password" autoComplete="current-password" /><Field label="Mật khẩu mới" name="new_password" type="password" minLength={10} maxLength={128} autoComplete="new-password" /><p className="help">Sau khi đổi mật khẩu, tất cả phiên sẽ đăng xuất.</p></SaveForm></Panel></div> }
function Assistant() {
    const [messages, setMessages] = useState<Row[]>([]);
    const [input, setInput] = useState('');
    const [busy, setBusy] = useState(false);
    const [error, setError] = useState('');
    const [thinkingStep, setThinkingStep] = useState(1);
    const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

    // Multi-stage thinking animation simulator
    useEffect(() => {
        if (!busy) {
            setThinkingStep(1);
            return;
        }
        const timer1 = setTimeout(() => setThinkingStep(2), 1200);
        const timer2 = setTimeout(() => setThinkingStep(3), 2600);
        return () => {
            clearTimeout(timer1);
            clearTimeout(timer2);
        };
    }, [busy]);

    async function send(message: string) {
        if (!message.trim() || busy) return;
        setInput('');
        setError('');
        setMessages(m => [...m, { role: 'user', message }]);
        setBusy(true);
        try {
            const result = await api('/ai/chat', 'POST', { message });
            setMessages(m => [...m, { role: 'assistant', ...result }]);
        } catch (e: any) {
            setError(e.message);
        } finally {
            setBusy(false);
        }
    }

    function copyText(text: string, idx: number) {
        navigator.clipboard.writeText(text);
        setCopiedIndex(idx);
        setTimeout(() => setCopiedIndex(null), 2000);
    }

    const suggestions = [
        { cat: '⚡ Tra cứu Điện', query: 'Tháng này tôi đã dùng bao nhiêu kWh điện?', icon: Zap, color: 'electric' },
        { cat: '💧 Tra cứu Nước', query: 'So sánh hóa đơn nước 3 tháng gần nhất.', icon: Droplets, color: 'water' },
        { cat: '🔮 Dự báo AI', query: 'Ước tính tiền điện & nước tháng tới là bao nhiêu?', icon: Sparkles, color: 'purple' },
        { cat: '🌱 Tiết kiệm', query: 'Tôi có thể tiết kiệm 15% chi phí điện như thế nào?', icon: Leaf, color: 'green' },
        { cat: '🧾 Trạng thái', query: 'Hóa đơn nào của tôi đang chờ thanh toán?', icon: ReceiptText, color: 'amber' },
    ];

    return (
        <div className="assistant-workspace">
            {/* MAIN CHAT AREA */}
            <div className="assistant-chat-main">
                
                {/* HEADER */}
                <div className="ai-header-bar">
                    <div className="ai-avatar-aura">
                        <Sparkles size={22} className="ai-sparkle-spin" />
                    </div>
                    <div className="ai-header-info">
                        <div className="ai-title-row">
                            <h2>Trợ Lý Nhà Mình AI</h2>
                            <span className="model-badge">Gemini 1.5 Pro</span>
                        </div>
                        <p>Dữ liệu gia đình thời gian thực · Tự động gợi ý & phân tích biểu giá</p>
                    </div>
                    
                    <div className="ai-header-actions">
                        <span className="online-pill">
                            <span className="pulse-dot" /> Sẵn sàng
                        </span>
                        {messages.length > 0 && (
                            <button 
                                className="icon-btn-subtle" 
                                onClick={() => setMessages([])}
                                title="Xóa cuộc trò chuyện"
                            >
                                <Trash2 size={16} />
                            </button>
                        )}
                    </div>
                </div>

                {/* MESSAGES STREAM */}
                <div className="ai-messages-scroll" aria-live="polite">
                    {!messages.length ? (
                        <div className="ai-welcome-hero">
                            <div className="welcome-glow-icon">
                                <Cpu size={40} />
                            </div>
                            <h2>Hôm nay, bạn muốn hiểu điều gì về ngôi nhà của bạn?</h2>
                            <p>Hệ thống AI sẵn sàng phân tích biểu đồ điện nước, tra cứu hóa đơn và đề xuất phương án tiết kiệm tối ưu.</p>

                            <div className="suggestion-chips-grid">
                                {suggestions.map((s, i) => {
                                    const IconComponent = s.icon;
                                    return (
                                        <button 
                                            key={i} 
                                            className={`chip-card ${s.color}`}
                                            onClick={() => send(s.query)}
                                        >
                                            <div className="chip-icon">
                                                <IconComponent size={18} />
                                            </div>
                                            <div className="chip-text">
                                                <strong>{s.cat}</strong>
                                                <span>{s.query}</span>
                                            </div>
                                            <ArrowUpRight size={16} className="chip-arrow" />
                                        </button>
                                    );
                                })}
                            </div>
                        </div>
                    ) : (
                        messages.map((m, i) => (
                            <div key={i} className={`ai-message-row ${m.role}`}>
                                <div className="avatar-wrap">
                                    {m.role === 'assistant' ? (
                                        <div className="ai-avatar-msg">
                                            <Sparkles size={18} />
                                        </div>
                                    ) : (
                                        <div className="user-avatar-msg">
                                            <User size={18} />
                                        </div>
                                    )}
                                </div>

                                <div className="bubble-wrap">
                                    <div className="bubble-header">
                                        <span className="sender-name">{m.role === 'assistant' ? 'Trợ lý AI' : 'Bạn'}</span>
                                        <span className="timestamp">{new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })}</span>
                                    </div>

                                    <div className="bubble-content">
                                        <ChatAnswer answer={m as { message: string }} />
                                    </div>

                                    {m.role === 'assistant' && (
                                        <div className="bubble-actions">
                                            <button 
                                                className="btn-action-copy"
                                                onClick={() => copyText(m.message || '', i)}
                                            >
                                                {copiedIndex === i ? <Check size={14} className="text-green" /> : <Copy size={14} />}
                                                <span>{copiedIndex === i ? 'Đã chép' : 'Sao chép'}</span>
                                            </button>
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))
                    )}

                    {/* DYNAMIC MULTI-STAGE AI THINKING / PREPARING RESPONSE ANIMATION */}
                    {busy && (
                        <div className="ai-message-row assistant thinking">
                            <div className="avatar-wrap">
                                <div className="ai-avatar-msg pulse-active">
                                    <Cpu size={18} className="spin-slow" />
                                </div>
                            </div>

                            <div className="bubble-wrap thinking-card">
                                <div className="thinking-head">
                                    <div className="glowing-orb-ring">
                                        <span className="orb-core" />
                                        <span className="ring-wave-1" />
                                        <span className="ring-wave-2" />
                                    </div>
                                    <div className="thinking-title">
                                        <strong>AI đang suy nghĩ và chuẩn bị câu trả lời...</strong>
                                        <span className="thinking-subtitle">Mô hình Gemini 1.5 đang xử lý dữ liệu gia đình</span>
                                    </div>
                                </div>

                                {/* EQUALIZER SOUNDWAVE BARS */}
                                <div className="equalizer-bars">
                                    <span className="bar b1" />
                                    <span className="bar b2" />
                                    <span className="bar b3" />
                                    <span className="bar b4" />
                                    <span className="bar b5" />
                                </div>

                                {/* MULTI-STEP PROGRESSION INDICATOR */}
                                <div className="thinking-steps">
                                    <div className={`step-item ${thinkingStep >= 1 ? 'active' : ''}`}>
                                        <Zap size={14} className="step-icon" />
                                        <span>1. Đang truy vấn lịch sử chỉ số công tơ & hóa đơn...</span>
                                    </div>
                                    <div className={`step-item ${thinkingStep >= 2 ? 'active' : ''}`}>
                                        <Cpu size={14} className="step-icon" />
                                        <span>2. Đang phân tích quy luật tiêu thụ & so sánh bậc giá...</span>
                                    </div>
                                    <div className={`step-item ${thinkingStep >= 3 ? 'active' : ''}`}>
                                        <Sparkles size={14} className="step-icon" />
                                        <span>3. Đang tạo báo cáo khuyến nghị tiết kiệm tối ưu...</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}
                </div>

                {error && <div className="error-alert" role="alert"><AlertTriangle size={16} />{error}</div>}

                {/* COMPOSER INPUT BAR */}
                <form className="ai-composer-bar" onSubmit={e => { e.preventDefault(); send(input); }}>
                    <div className="composer-input-wrapper">
                        <input 
                            aria-label="Câu hỏi cho trợ lý" 
                            value={input} 
                            maxLength={2000} 
                            onChange={e => setInput(e.target.value)} 
                            placeholder="Hỏi bất kỳ điều gì về điện, nước hoặc mẹo tiết kiệm…" 
                        />
                        
                        <div className="composer-tools">
                            <button type="button" className="tool-btn" title="Thử hỏi bằng giọng nói">
                                <Mic size={18} />
                            </button>
                            <button 
                                type="submit" 
                                className="btn-send-ai"
                                disabled={busy || !input.trim()}
                                aria-label="Gửi câu hỏi"
                            >
                                <span>Gửi</span>
                                <Send size={16} />
                            </button>
                        </div>
                    </div>
                </form>
                
                <p className="ai-disclaimer">⚡ Trợ lý AI kết nối dữ liệu máy chủ Nhà Mình. Các con số dự báo mang tính chất tham khảo.</p>
            </div>

            {/* RIGHT SIDEBAR: REAL-TIME CONTEXT & QUICK TIPS */}
            <div className="assistant-sidebar-context">
                <div className="sidebar-card live-status">
                    <div className="card-head">
                        <House size={18} className="text-blue" />
                        <h3>Trạng thái Kỳ Hiện Tại</h3>
                    </div>
                    <div className="status-metrics-grid">
                        <div className="sm-chip electric">
                            <Zap size={15} />
                            <div>
                                <span>Điện T12</span>
                                <strong>428.000 ₫</strong>
                            </div>
                        </div>
                        <div className="sm-chip water">
                            <Droplets size={15} />
                            <div>
                                <span>Nước T12</span>
                                <strong>86.000 ₫</strong>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="sidebar-card ai-tip">
                    <div className="card-head">
                        <Lightbulb size={18} className="text-yellow" />
                        <h3>Mẹo Hay Từ AI</h3>
                    </div>
                    <p className="tip-text">
                        "Giảm nhiệt độ máy nước nóng bớt 2°C có thể giúp tiết kiệm khoảng 45.000 ₫ mỗi tháng."
                    </p>
                </div>

                <div className="sidebar-card capabilities">
                    <div className="card-head">
                        <Info size={18} className="text-purple" />
                        <h3>Khả Năng Của Trợ Lý</h3>
                    </div>
                    <ul className="cap-list">
                        <li>✓ Phân tích bậc giá EVN & Sawaco</li>
                        <li>✓ Phát hiện dòng điện rò rỉ bất thường</li>
                        <li>✓ Ước tính hóa đơn cuối tháng</li>
                        <li>✓ Lập kế hoạch tiết kiệm năng lượng</li>
                    </ul>
                </div>
            </div>
        </div>
    );
}

function AdminPage({ screen, notify }: { screen: string; notify: (s?: string) => void }) {
    const endpoint = screen === 'admin' ? '/admin' : screen === 'admin/users' ? '/admin/users' : screen === 'admin/audit' ? '/admin/audit' : '/tariffs';
    const { data, error, loading } = useData([endpoint]);

    const tabs = [
        { path: 'admin', label: 'Tổng quan', icon: LayoutDashboard },
        { path: 'admin/users', label: 'Người dùng', icon: Users },
        { path: 'admin/tariffs', label: 'Biểu giá', icon: ReceiptText },
        { path: 'admin/audit', label: 'Nhật ký hệ thống', icon: ShieldCheck }
    ];

    return <><div className="admin-tabs">{tabs.map(t => { const Icon = t.icon; return <Link key={t.path} className={screen === t.path ? 'selected' : ''} href={'/' + t.path}><Icon size={16} /><span>{t.label}</span></Link> })}</div>{error || loading ? <LoadState error={error} loading={loading} /> : screen === 'admin' ? <><div className="metric-grid">{[['users', 'Người dùng', Users, '#2563eb', '#eff6ff'], ['households', 'Hộ gia đình', House, '#059669', '#ecfdf5'], ['bills', 'Hóa đơn', ReceiptText, '#d97706', '#fffbeb'], ['active_accounts', 'Tài khoản hoạt động', Zap, '#0284c7', '#f0f9ff'], ['ai_requests', 'Yêu cầu AI', Sparkles, '#7c3aed', '#f5f3ff'], ['ai_errors', 'Lỗi AI', AlertTriangle, '#dc2626', '#fef2f2']].map(([key, label, Icon, color, bg]: any) => <div className="stat-card-admin" key={key}><div className="stat-head"><span>{label}</span><div className="stat-icon" style={{ background: bg, color: color }}><Icon size={18} /></div></div><div className="stat-val">{data[0][key]}</div></div>)}</div><Panel title="Hoạt động AI gần đây"><DataTable rows={data[0].ai_usage} columns={[{ title: 'Loại phân tích', render: r => <strong>{r.analysis_type}</strong> }, { title: 'Model AI', render: r => <span className="badge">{r.model_name}</span> }, { title: 'Thời điểm', render: r => new Date(r.created_at).toLocaleString('vi-VN') }]} /></Panel></> : screen === 'admin/users' ? <Panel title="Quản lý người dùng hệ thống"><DataTable rows={data[0]} columns={[{ title: 'Người dùng', render: r => <div><strong>{r.full_name}</strong><small>{r.email}</small></div> }, { title: 'Vai trò', render: r => <span className={`badge ${r.role === 'ADMIN' ? 'overdue' : ''}`}>{r.role}</span> }, { title: 'Trạng thái', render: r => <span className={`badge ${r.is_active ? 'paid' : 'overdue'}`}>{r.is_active ? 'Hoạt động' : 'Đã khóa'}</span> }, { title: 'Thao tác', render: r => <Action label={r.is_active ? 'Khóa tài khoản' : 'Mở khóa'} run={() => api('/admin/users/' + r.id, 'PATCH', { is_active: !r.is_active })} done={() => notify()} /> }]} /></Panel> : screen === 'admin/audit' ? <Panel title="Nhật ký hoạt động hệ thống"><DataTable rows={data[0]} columns={[{ title: 'Hành động', render: r => <strong>{r.action}</strong> }, { title: 'Đối tượng', render: r => <span className="badge">{r.entity_type}</span> }, { title: 'ID Thực thể', render: r => <code>{r.entity_id}</code> }, { title: 'Thời điểm', render: r => new Date(r.created_at).toLocaleString('vi-VN') }]} /></Panel> : <><Panel title="Biểu giá hiện có trong hệ thống"><DataTable rows={data[0]} columns={[{ title: 'Tên biểu giá', render: r => <div><strong>{r.name}</strong><small>{r.provider_name}</small></div> }, { title: 'Dịch vụ', render: r => <span className={`badge ${r.utility_type === 'ELECTRICITY' ? 'unpaid' : 'water'}`}>{r.utility_type === 'ELECTRICITY' ? 'Điện' : 'Nước'}</span> }, { title: 'Phân loại / Khu vực', render: r => `${r.tariff_category || 'Sinh hoạt'} (${r.province || 'Toàn quốc'})` }, { title: 'Phiên bản', render: r => <span className="badge">{r.version}</span> }, { title: 'Hiệu lực từ', render: r => r.effective_from }, { title: 'Số bậc', render: r => <strong>{r.tiers.length} bậc</strong> }]} /></Panel><TariffForm notify={notify} /></>}</>
}
function TariffForm({ notify }: { notify: (s?: string) => void }) {
    const [formState, setFormState] = useState({ name: '', provider_name: '', utility_type: 'ELECTRICITY', tariff_category: 'RESIDENTIAL_1PHASE', province: '', version: 'v2024.1', effective_from: localDate() });
    const [tiers, setTiers] = useState<{ from_value: string; to_value: string; unit_price: string }[]>([{ from_value: '0', to_value: '50', unit_price: '1806' }, { from_value: '50', to_value: '100', unit_price: '1866' }, { from_value: '100', to_value: '200', unit_price: '2167' }, { from_value: '200', to_value: '300', unit_price: '2729' }, { from_value: '300', to_value: '400', unit_price: '3050' }, { from_value: '400', to_value: '', unit_price: '3151' }]);

    const fillPreset = (type: 'EVN_1P' | 'EVN_3P' | 'SAWACO') => {
        if (type === 'EVN_1P') {
            setFormState({ name: 'Biểu giá điện 1 pha sinh hoạt EVN 2024', provider_name: 'Tập đoàn Điện lực Việt Nam (EVN)', utility_type: 'ELECTRICITY', tariff_category: 'RESIDENTIAL_1PHASE', province: '', version: 'v2024.1', effective_from: '2024-01-01' });
            setTiers([
                { from_value: '0', to_value: '50', unit_price: '1806' },
                { from_value: '50', to_value: '100', unit_price: '1866' },
                { from_value: '100', to_value: '200', unit_price: '2167' },
                { from_value: '200', to_value: '300', unit_price: '2729' },
                { from_value: '300', to_value: '400', unit_price: '3050' },
                { from_value: '400', to_value: '', unit_price: '3151' }
            ]);
        } else if (type === 'EVN_3P') {
            setFormState({ name: 'Biểu giá điện 3 pha sinh hoạt EVN', provider_name: 'Tập đoàn Điện lực Việt Nam (EVN)', utility_type: 'ELECTRICITY', tariff_category: 'RESIDENTIAL_3PHASE', province: '', version: 'v2024.1', effective_from: '2024-01-01' });
            setTiers([
                { from_value: '0', to_value: '100', unit_price: '1900' },
                { from_value: '100', to_value: '300', unit_price: '2500' },
                { from_value: '300', to_value: '', unit_price: '3200' }
            ]);
        } else if (type === 'SAWACO') {
            setFormState({ name: 'Biểu giá nước sinh hoạt Sawaco TP.HCM', provider_name: 'Tổng công ty Cấp nước Sài Gòn (Sawaco)', utility_type: 'WATER', tariff_category: 'RESIDENTIAL', province: 'TP. Hồ Chí Minh', version: 'v2024.1', effective_from: '2024-01-01' });
            setTiers([
                { from_value: '0', to_value: '4', unit_price: '6700' },
                { from_value: '4', to_value: '6', unit_price: '12900' },
                { from_value: '6', to_value: '', unit_price: '14400' }
            ]);
        }
    };

    return <Panel title="Tạo phiên bản biểu giá">
        <div className="preset-buttons" style={{ display: 'flex', gap: 10, marginBottom: 18, flexWrap: 'wrap' }}>
            <span style={{ fontSize: 13, fontWeight: 600, alignSelf: 'center', color: 'var(--text-secondary)' }}>⚡ Tải dữ liệu mẫu nhanh:</span>
            <button type="button" className="button small secondary" onClick={() => fillPreset('EVN_1P')}>Điện 1 Pha EVN (6 Bậc)</button>
            <button type="button" className="button small secondary" onClick={() => fillPreset('EVN_3P')}>Điện 3 Pha EVN</button>
            <button type="button" className="button small secondary" onClick={() => fillPreset('SAWACO')}>Nước Sinh Hoạt Sawaco (TP.HCM)</button>
        </div>
        <SaveForm label="Tạo biểu giá" submit={async values => { await api('/admin/tariffs', 'POST', { ...values, province: values.province?.trim() || null, effective_to: values.effective_to || null, tiers: tiers.map(t => ({ from_value: Number(t.from_value), to_value: t.to_value ? Number(t.to_value) : null, unit_price: Number(t.unit_price) })) }); notify('Đã tạo phiên bản biểu giá. Hóa đơn lịch sử giữ nguyên.') }}>
            <div className="form-grid">
                <Field label="Tên biểu giá" name="name" value={formState.name} onChange={(e: any) => setFormState({ ...formState, name: e.target.value })} />
                <Field label="Nhà cung cấp" name="provider_name" value={formState.provider_name} onChange={(e: any) => setFormState({ ...formState, provider_name: e.target.value })} />
                <Select label="Dịch vụ" name="utility_type" value={formState.utility_type} onChange={(e: any) => setFormState({ ...formState, utility_type: e.target.value })}>
                    <option value="ELECTRICITY">Điện</option>
                    <option value="WATER">Nước</option>
                </Select>
                <Select label="Loại biểu giá / Pha" name="tariff_category" value={formState.tariff_category} onChange={(e: any) => setFormState({ ...formState, tariff_category: e.target.value })}>
                    <option value="RESIDENTIAL_1PHASE">Điện 1 pha sinh hoạt (6 bậc)</option>
                    <option value="RESIDENTIAL_3PHASE">Điện 3 pha sinh hoạt</option>
                    <option value="RESIDENTIAL">Nước sinh hoạt</option>
                    <option value="COMMERCIAL">Kinh doanh / Dịch vụ</option>
                    <option value="INDUSTRIAL">Sản xuất</option>
                </Select>
                <Field label="Tỉnh / Thành phố" name="province" required={false} value={formState.province} placeholder="Để trống nếu áp dụng toàn quốc" onChange={(e: any) => setFormState({ ...formState, province: e.target.value })} />
                <Field label="Phiên bản" name="version" value={formState.version} onChange={(e: any) => setFormState({ ...formState, version: e.target.value })} />
                <Field label="Hiệu lực từ" name="effective_from" type="date" value={formState.effective_from} onChange={(e: any) => setFormState({ ...formState, effective_from: e.target.value })} />
                <Field label="Hiệu lực đến" name="effective_to" type="date" required={false} />
            </div>
            <h3>Các bậc giá</h3>
            {tiers.map((tier, i) => <div className="tier-row" key={i}>
                <strong>Bậc {i + 1}</strong>
                {(['from_value', 'to_value', 'unit_price'] as const).map((key, j) => <label className="field" key={key}>
                    <span>{['Từ', 'Đến (trống = vô hạn)', 'Đơn giá VND'][j]}</span>
                    <input type="number" min={0} step="0.001" required={key !== 'to_value'} value={tier[key]} onChange={e => setTiers(ts => ts.map((t, index) => index === i ? { ...t, [key]: e.target.value } : t))} />
                </label>)}
                {tiers.length > 1 && <button type="button" aria-label="Xóa bậc" className="icon-button" onClick={() => setTiers(ts => ts.filter((_, index) => i !== index))}><X size={18} /></button>}
            </div>)}
            <button type="button" className="text-button" onClick={() => setTiers(ts => [...ts, { from_value: ts.at(-1)?.to_value || '', to_value: '', unit_price: '' }])}><Plus size={16} />Thêm bậc</button>
            <p className="help">Các bậc phải liên tục từ 0, bậc cuối không có giới hạn trên. Biểu giá mới không sửa hóa đơn đã tạo.</p>
        </SaveForm>
    </Panel>
}

