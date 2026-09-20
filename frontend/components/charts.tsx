'use client';

import {
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
  LineChart,
  Line
} from 'recharts';

const ELECTRICITY_COLOR = '#f59e0b';
const WATER_COLOR = '#0ea5e9';
const PRIMARY_COLOR = '#2563eb';
const SUCCESS_COLOR = '#10b981';

// Format helper
const formatVND = (val: number) => {
  if (val >= 1_000_000) return (val / 1_000_000).toFixed(1) + 'M ₫';
  if (val >= 1_000) return (val / 1_000).toFixed(0) + 'k ₫';
  return val.toLocaleString('vi-VN') + ' ₫';
};

/**
 * Legacy & Multi-purpose usage chart
 */
export function UsageChart({ data, cost = false }: { data: any[]; cost?: boolean }) {
  if (!data || !data.length) {
    return <div className="empty">Chưa có dữ liệu thống kê trong khoảng thời gian này.</div>;
  }

  return (
    <div className="chart" role="img" aria-label={cost ? 'Biểu đồ chi phí theo tháng' : 'Biểu đồ điện và nước theo tháng'}>
      <ResponsiveContainer width="100%" height={290}>
        {cost ? (
          <BarChart data={data} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
            <XAxis dataKey="period" tick={{ fill: '#64748b', fontSize: 12 }} />
            <YAxis tickFormatter={v => formatVND(v)} tick={{ fill: '#64748b', fontSize: 12 }} />
            <Tooltip
              formatter={(v: any) => [Number(v).toLocaleString('vi-VN') + ' ₫', 'Chi phí']}
              contentStyle={{ borderRadius: '8px', border: '1px solid #e2e8f0', boxShadow: '0 4px 12px rgba(0,0,0,0.08)' }}
            />
            <Bar dataKey="cost" name="Chi phí" fill={PRIMARY_COLOR} radius={[6, 6, 0, 0]} />
          </BarChart>
        ) : (
          <AreaChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="electricGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={ELECTRICITY_COLOR} stopOpacity={0.3} />
                <stop offset="95%" stopColor={ELECTRICITY_COLOR} stopOpacity={0.0} />
              </linearGradient>
              <linearGradient id="waterGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={WATER_COLOR} stopOpacity={0.3} />
                <stop offset="95%" stopColor={WATER_COLOR} stopOpacity={0.0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
            <XAxis dataKey="period" tick={{ fill: '#64748b', fontSize: 12 }} tickFormatter={v => (v.length > 5 ? v.slice(5) : v)} />
            <YAxis yAxisId="electric" unit=" kWh" width={60} tick={{ fill: '#64748b', fontSize: 11 }} />
            <YAxis yAxisId="water" orientation="right" unit=" m³" width={50} tick={{ fill: '#64748b', fontSize: 11 }} />
            <Tooltip
              contentStyle={{ borderRadius: '8px', border: '1px solid #e2e8f0', boxShadow: '0 4px 12px rgba(0,0,0,0.08)' }}
              formatter={(val: any, name: any) => [
                Number(val).toLocaleString('vi-VN') + (name?.includes('Điện') ? ' kWh' : ' m³'),
                name
              ]}
            />
            <Legend wrapperStyle={{ paddingTop: 10 }} />
            <Area yAxisId="electric" type="monotone" dataKey="ELECTRICITY" name="Điện (kWh)" stroke={ELECTRICITY_COLOR} fill="url(#electricGrad)" strokeWidth={2.5} />
            <Area yAxisId="water" type="monotone" dataKey="WATER" name="Nước (m³)" stroke={WATER_COLOR} fill="url(#waterGrad)" strokeWidth={2.5} />
          </AreaChart>
        )}
      </ResponsiveContainer>
    </div>
  );
}

/**
 * Executive Spending Area Chart (Electricity, Water, Total Spending)
 */
export function ExecutiveSpendingChart({ data, metric = 'cost' }: { data: any[]; metric?: 'cost' | 'ELECTRICITY' | 'WATER' }) {
  if (!data || !data.length) {
    return <div className="empty">Chưa có dữ liệu xu hướng chi phí.</div>;
  }

  const isElec = metric === 'ELECTRICITY';
  const isWater = metric === 'WATER';
  const color = isElec ? ELECTRICITY_COLOR : isWater ? WATER_COLOR : PRIMARY_COLOR;
  const name = isElec ? 'Tiền điện (kWh)' : isWater ? 'Tiền nước (m³)' : 'Tổng chi phí (₫)';

  return (
    <div className="chart" style={{ width: '100%', height: 300 }}>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 20, right: 20, left: 10, bottom: 0 }}>
          <defs>
            <linearGradient id="dynamicGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={color} stopOpacity={0.35} />
              <stop offset="95%" stopColor={color} stopOpacity={0.0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
          <XAxis dataKey="period" tick={{ fill: '#64748b', fontSize: 12 }} />
          <YAxis tickFormatter={v => (metric === 'cost' ? formatVND(v) : v.toString())} tick={{ fill: '#64748b', fontSize: 12 }} width={70} />
          <Tooltip
            contentStyle={{ borderRadius: '12px', background: '#ffffff', borderColor: '#e2e8f0', color: '#0f172a', boxShadow: '0 8px 24px rgba(0,0,0,0.08)' }}
            formatter={(val: any) => [
              metric === 'cost' ? Number(val).toLocaleString('vi-VN') + ' ₫' : Number(val).toLocaleString('vi-VN') + (isElec ? ' kWh' : ' m³'),
              name
            ]}
          />
          <Area type="monotone" dataKey={metric} name={name} stroke={color} fill="url(#dynamicGrad)" strokeWidth={3} dot={{ r: 5, fill: color, strokeWidth: 2, stroke: '#ffffff' }} activeDot={{ r: 7, strokeWidth: 3 }} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

/**
 * Executive Cost Breakdown Donut Chart (Electricity vs Water %)
 */
export function CostBreakdownDonut({ electricityCost = 0, waterCost = 0 }: { electricityCost: number; waterCost: number }) {
  const total = electricityCost + waterCost;
  if (total === 0) {
    return <div className="empty">Chưa có dữ liệu phân bổ chi phí.</div>;
  }

  const chartData = [
    { name: 'Tiền Điện', value: electricityCost, color: ELECTRICITY_COLOR },
    { name: 'Tiền Nước', value: waterCost, color: WATER_COLOR }
  ];

  const elecPercent = Math.round((electricityCost / total) * 100);
  const waterPercent = 100 - elecPercent;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: '100%' }}>
      <div style={{ position: 'relative', width: '100%', height: 210 }}>
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={85}
              paddingAngle={4}
              dataKey="value"
            >
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip formatter={(val: any) => [Number(val).toLocaleString('vi-VN') + ' ₫', 'Chi phí']} />
          </PieChart>
        </ResponsiveContainer>
        <div
          style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            textAlign: 'center',
            pointerEvents: 'none'
          }}
        >
          <div style={{ fontSize: 11, color: '#64748b', fontWeight: 600, textTransform: 'uppercase' }}>TỔNG CHỈ TÊU</div>
          <div style={{ fontSize: 16, fontWeight: 700, color: '#0f172a' }}>{formatVND(total)}</div>
        </div>
      </div>
      <div style={{ display: 'flex', gap: 20, marginTop: 8, fontSize: 13 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <span style={{ width: 10, height: 10, borderRadius: '50%', background: ELECTRICITY_COLOR }} />
          <span>Điện: <strong>{elecPercent}%</strong> ({electricityCost.toLocaleString('vi-VN')} ₫)</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <span style={{ width: 10, height: 10, borderRadius: '50%', background: WATER_COLOR }} />
          <span>Nước: <strong>{waterPercent}%</strong> ({waterCost.toLocaleString('vi-VN')} ₫)</span>
        </div>
      </div>
    </div>
  );
}

/**
 * Month-over-Month Comparison Bar Chart
 */
export function MonthlyComparisonBar({ data }: { data: any[] }) {
  if (!data || !data.length) {
    return <div className="empty">Chưa có dữ liệu so sánh các tháng.</div>;
  }

  return (
    <div style={{ width: '100%', height: 260 }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
          <XAxis dataKey="period" tick={{ fill: '#64748b', fontSize: 12 }} />
          <YAxis tickFormatter={v => formatVND(v)} tick={{ fill: '#64748b', fontSize: 12 }} width={65} />
          <Tooltip
            formatter={(val: any, name: any) => [Number(val).toLocaleString('vi-VN') + ' ₫', name]}
            contentStyle={{ borderRadius: '8px', border: '1px solid #e2e8f0' }}
          />
          <Legend wrapperStyle={{ paddingTop: 8 }} />
          <Bar dataKey="ELECTRICITY_COST" name="Tiền điện" fill={ELECTRICITY_COLOR} radius={[4, 4, 0, 0]} />
          <Bar dataKey="WATER_COST" name="Tiền nước" fill={WATER_COLOR} radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

/**
 * Mini Sparkline Component for KPI Cards
 */
export function MiniSparkline({ data, dataKey = 'val', color = PRIMARY_COLOR }: { data: any[]; dataKey?: string; color?: string }) {
  if (!data || data.length < 2) return null;
  return (
    <div style={{ width: 80, height: 28 }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <Line type="monotone" dataKey={dataKey} stroke={color} strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
