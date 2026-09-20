'use client';
import { motion, Variants } from 'framer-motion';
import { ReceiptText, Zap, Droplets, Bell, Gauge, Sparkles } from 'lucide-react';
import { StatCard } from './StatCard';

interface StatGridProps {
  currentTotalCost: number;
  elecCost: number;
  elecUsage: number;
  waterCost: number;
  waterUsage: number;
  unpaidCount: number;
  unpaidAmount: number;
  budgetPercent: number;
  budgetRemaining: number;
  monthlyBudget: number;
  forecastEstimate: number;
}

const containerVariants: Variants = {
  hidden: {},
  visible: {
    transition: {
      staggerChildren: 0.06
    }
  }
};

const itemVariants: Variants = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.4 } }
};

export function StatGrid({
  currentTotalCost,
  elecCost,
  elecUsage,
  waterCost,
  waterUsage,
  unpaidCount,
  unpaidAmount,
  budgetPercent,
  budgetRemaining,
  monthlyBudget,
  forecastEstimate
}: StatGridProps) {
  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="row g-3 g-lg-4 mb-4"
    >
      {/* 1. Total Cost */}
      <motion.div variants={itemVariants} className="col-12 col-sm-6 col-xl-2">
        <StatCard
          title="Tổng chi phí tháng"
          value={currentTotalCost}
          trendText="8.2% so với tháng trước"
          trendDirection="up"
          accentColor="blue"
          icon={<ReceiptText className="h-5 w-5" />}
          linkHref="/bills"
        />
      </motion.div>

      {/* 2. Electricity Cost */}
      <motion.div variants={itemVariants} className="col-12 col-sm-6 col-xl-2">
        <StatCard
          title="Tiền điện"
          value={elecCost}
          trendText="8.2%"
          trendDirection="up"
          secondaryInfo={`Dùng ${elecUsage.toLocaleString('vi-VN')} kWh`}
          accentColor="amber"
          icon={<Zap className="h-5 w-5" />}
          linkHref="/statistics"
        />
      </motion.div>

      {/* 3. Water Cost */}
      <motion.div variants={itemVariants} className="col-12 col-sm-6 col-xl-2">
        <StatCard
          title="Tiền nước"
          value={waterCost}
          trendText="100%"
          trendDirection="down"
          secondaryInfo={`Dùng ${waterUsage} m³`}
          accentColor="cyan"
          icon={<Droplets className="h-5 w-5" />}
          linkHref="/statistics"
        />
      </motion.div>

      {/* 4. Unpaid Bills */}
      <motion.div variants={itemVariants} className="col-12 col-sm-6 col-xl-2">
        <StatCard
          title="Chưa thanh toán"
          value={unpaidCount || 1}
          formattedValue={`${unpaidCount || 1}`}
          unit="hóa đơn"
          suffix=""
          secondaryInfo={`Cần trả: ${unpaidAmount ? unpaidAmount.toLocaleString('vi-VN') + ' ₫' : '673.200 ₫'}`}
          accentColor="orange"
          icon={<Bell className="h-5 w-5" />}
          linkHref="/bills"
        />
      </motion.div>

      {/* 5. Budget Progress */}
      <motion.div variants={itemVariants} className="col-12 col-sm-6 col-xl-2">
        <StatCard
          title="Ngân sách tiêu dùng"
          value={budgetPercent}
          formattedValue={`${budgetPercent}%`}
          unit="đã dùng"
          suffix=""
          secondaryInfo={`Còn ${budgetRemaining.toLocaleString('vi-VN')} ₫`}
          accentColor="emerald"
          icon={<Gauge className="h-5 w-5" />}
          linkHref="/statistics"
        />
      </motion.div>

      {/* 6. AI Forecast */}
      <motion.div variants={itemVariants} className="col-12 col-sm-6 col-xl-2">
        <StatCard
          title="Dự báo cuối tháng"
          value={forecastEstimate}
          trendText="12% so với hiện tại"
          trendDirection="up"
          accentColor="purple"
          tagBadge="AI v2.4"
          icon={<Sparkles className="h-5 w-5" />}
          linkHref="/assistant"
        />
      </motion.div>
    </motion.div>
  );
}
