export function ReadingBillingNotice({readingCount,billCount,period,electricityUsage,waterUsage}:{readingCount:number;billCount:number;period:string|null;electricityUsage:number|null;waterUsage:number|null}){
 if(!readingCount||billCount)return null;
 const number=(value:number)=>new Intl.NumberFormat('vi-VN',{maximumFractionDigits:3}).format(value);
 return <section role="status" aria-label="Trạng thái chỉ số và hóa đơn" className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-slate-800 space-y-2">
  <strong>Đã lưu {readingCount} bản ghi chỉ số, chưa có hóa đơn</strong>
  {period&&<p>Kỳ {period}:{electricityUsage!==null&&` điện ${number(electricityUsage)} kWh`}{waterUsage!==null&&` nước ${number(waterUsage)} m³`}.</p>}
  <p>Chỉ số và lượng tiêu thụ đã được ghi nhận. Phần chi phí chưa có số tiền vì chưa có hóa đơn; không được tính là 0 đồng. Kiểm tra biểu giá phù hợp với nhà cung cấp, nhóm sử dụng và khu vực để tạo hóa đơn ước tính.</p>
  <div className="flex flex-wrap gap-4"><a className="underline text-blue-700" href="/readings">Xem chỉ số đã lưu</a><a className="underline text-blue-700" href="/bills">Xem hóa đơn</a></div>
 </section>;
}
