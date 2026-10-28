import React from 'react';

type InvoiceResult = {
    extracted_data?: Record<string, string | null> | null;
    extraction?: { uncertain_fields?: string[]; missing_fields?: string[] } | null;
};

const labels: Record<string, string> = {
    provider_name: 'Nhà cung cấp', customer_code: 'Mã khách hàng', meter_code: 'Mã công tơ',
    billing_period: 'Kỳ hóa đơn', previous_reading: 'Chỉ số cũ', current_reading: 'Chỉ số mới',
    consumption: 'Lượng tiêu thụ', unit: 'Đơn vị', total_amount: 'Tổng tiền trên ảnh',
    currency: 'Tiền tệ', due_date: 'Hạn thanh toán',
};

export function InvoiceResultDetails({result}: {result?: InvoiceResult}) {
    if (!result?.extracted_data) return null;
    return <details className="invoice-extraction-details">
        <summary>Xem dữ liệu đọc từ hóa đơn</summary>
        <dl>
            {Object.entries(labels).map(([key, label]) => {
                const value = result.extracted_data?.[key];
                const uncertain = result.extraction?.uncertain_fields?.includes(key);
                return <div key={key}><dt>{label}</dt><dd>{value ?? (uncertain ? 'Không đọc rõ' : 'Không có trên ảnh')}</dd></div>;
            })}
        </dl>
        <p>Dữ liệu này chưa được lưu thành chỉ số hoặc hóa đơn trong hệ thống.</p>
    </details>;
}
