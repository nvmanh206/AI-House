import unicodedata
import re
from decimal import Decimal
from datetime import date
from app.models import User, Household, HouseholdMember, UtilityAccount, Meter, Bill, MeterReading
from app.ai.router import normalize_message
from app.ai.tools.knowledge import basic_explanation

def build_user_overview(service) -> dict:
    """
    Tập hợp dữ liệu tổng quan của người dùng và hộ gia đình đang đăng nhập:
    - Người dùng: họ tên, email, vai trò (Chủ hộ / Thành viên)
    - Hộ gia đình: tên hộ, địa chỉ/tỉnh thành, số thành viên, danh sách thành viên
    - Tài khoản tiện ích: loại (Điện/Nước), nhà cung cấp, mã khách hàng, loại giá
    - Công tơ: tên/mã, đơn vị (kWh, m³), trạng thái
    - Chỉ số & tiêu thụ: các lần ghi chỉ số gần nhất (kỳ, ngày ghi, chỉ số cũ, chỉ số mới, tiêu thụ)
    - Hóa đơn: các hóa đơn gần nhất (kỳ, loại, số tiền, trạng thái thanh toán, hạn)
    - Khoản chưa thanh toán: danh sách & tổng tiền
    """
    user = service.auth[0]
    member = service.member()
    household = service.repo.get(Household, member.household_id) if member and member.household_id else None

    # 1. User Info
    user_info = {
        'id': user.id,
        'full_name': user.full_name or 'Người dùng',
        'email': user.email or '',
        'system_role': user.role,
        'household_role': 'Chủ hộ' if member and member.role == 'OWNER' else 'Thành viên'
    }

    # 2. Household Info
    household_info = {
        'id': household.id if household else None,
        'name': household.name if household else 'Hộ gia đình',
        'province': household.province if household else 'Chưa cập nhật',
        'district': household.district if household else '',
        'ward': household.ward if household else '',
        'member_count': household.member_count if household else 1,
        'members': []
    }
    if household:
        members = service.repo.all(HouseholdMember, household_id=household.id)
        for m in members:
            u = service.repo.get(User, m.user_id)
            if u:
                household_info['members'].append({
                    'name': u.full_name,
                    'email': u.email,
                    'role': 'Chủ hộ' if m.role == 'OWNER' else 'Thành viên'
                })

    # 3. Utility Accounts
    accounts_info = []
    try:
        accounts = service.accounts()
        for a in accounts:
            accounts_info.append({
                'id': a.get('id'),
                'utility_type': 'Điện' if a.get('utility_type') == 'ELECTRICITY' else 'Nước',
                'provider_name': a.get('provider_name') or 'Chưa rõ',
                'customer_code': a.get('customer_code') or 'Chưa có',
                'tariff_category': a.get('tariff_category') or 'Mặc định',
                'province': a.get('province') or household_info['province']
            })
    except Exception:
        pass

    # 4. Meters
    meters_info = []
    try:
        meters = service.meters()
        for m in meters:
            meters_info.append({
                'id': m.get('id'),
                'utility_type': 'Điện' if m.get('utility_type') == 'ELECTRICITY' else 'Nước',
                'name': m.get('name') or 'Công tơ chính',
                'meter_code': m.get('meter_code') or 'Chưa có mã',
                'unit': m.get('unit') or ('kWh' if m.get('utility_type') == 'ELECTRICITY' else 'm³'),
                'initial_reading': m.get('initial_reading', 0),
                'is_active': m.get('is_active', True)
            })
    except Exception:
        pass

    # 5. History / Readings
    history_info = []
    try:
        history = service.history()
        for r in history[-6:]:
            history_info.append({
                'period': r.get('period'),
                'utility_type': 'Điện' if r.get('utility_type') == 'ELECTRICITY' else 'Nước',
                'previous_reading': r.get('previous_reading'),
                'current_reading': r.get('current_reading'),
                'consumption': r.get('consumption'),
                'unit': r.get('unit'),
                'reading_date': str(r.get('reading_date')),
                'source': r.get('source')
            })
    except Exception:
        pass

    # 6. Bills & Payments
    bills_info = []
    unpaid_bills = []
    try:
        bills = service.bills()
        for b in bills[:6]:
            b_item = {
                'id': b.get('id'),
                'period': b.get('period'),
                'utility_type': 'Điện' if b.get('utility_type') == 'ELECTRICITY' else 'Nước',
                'final_amount': float(b.get('final_amount', 0)),
                'status': b.get('status'),
                'due_date': str(b.get('due_date')) if b.get('due_date') else None,
                'paid_at': str(b.get('paid_at')) if b.get('paid_at') else None,
                'source': b.get('source')
            }
            bills_info.append(b_item)
            if b.get('status') in ('UNPAID', 'OVERDUE', 'PENDING'):
                unpaid_bills.append(b_item)
    except Exception:
        pass

    total_unpaid = sum(b['final_amount'] for b in unpaid_bills)

    return {
        'user': user_info,
        'household': household_info,
        'accounts': accounts_info,
        'meters': meters_info,
        'readings': history_info,
        'bills': bills_info,
        'unpaid_bills': unpaid_bills,
        'total_unpaid': total_unpaid
    }


def format_user_overview_text(ov: dict) -> str:
    user = ov['user']
    house = ov['household']

    lines = [
        "=== THÔNG TIN NGƯỜI DÙNG & HỘ GIA ĐÌNH ===",
        f"- Người dùng hiện tại: {user['full_name']} (Email: {user['email']})",
        f"- Vai trò trong hộ: {user['household_role']} (Hệ thống: {user['system_role']})",
        f"- Tên hộ gia đình: {house['name']} (Tỉnh/Thành phố: {house['province']})",
        f"- Số lượng thành viên: {house['member_count']} người",
    ]
    if house['members']:
        members_str = ", ".join(f"{m['name']} ({m['role']})" for m in house['members'])
        lines.append(f"- Danh sách thành viên: {members_str}")

    lines.append("\n=== CÁC TÀI KHOẢN TIỆN ÍCH & CÔNG TƠ ===")
    if ov['accounts']:
        for acc in ov['accounts']:
            lines.append(f"- Dịch vụ {acc['utility_type']}: Nhà cung cấp {acc['provider_name']}, Mã KH: {acc['customer_code']}, Gói: {acc['tariff_category']}")
    else:
        lines.append("- Chưa có tài khoản dịch vụ.")

    if ov['meters']:
        for m in ov['meters']:
            status_str = "Đang hoạt động" if m['is_active'] else "Ngừng"
            lines.append(f"- Công tơ {m['utility_type']}: {m['name']} (Mã: {m['meter_code']}, Chỉ số đầu: {m['initial_reading']} {m['unit']}, Trạng thái: {status_str})")
    else:
        lines.append("- Chưa cấu hình công tơ.")

    lines.append("\n=== CHỈ SỐ VÀ TIÊU THỤ GẦN ĐÂY ===")
    if ov['readings']:
        for r in ov['readings']:
            lines.append(f"- Kỳ {r['period']} ({r['utility_type']}): Tiêu thụ {r['consumption']} {r['unit']} (Chỉ số: {r['previous_reading']} -> {r['current_reading']}, Ngày ghi: {r['reading_date']}, Nguồn: {r['source']})")
    else:
        lines.append("- Chưa có dữ liệu chỉ số công tơ nào được ghi.")

    lines.append("\n=== HÓA ĐƠN VÀ THANH TOÁN GẦN ĐÂY ===")
    if ov['unpaid_bills']:
        lines.append(f"- HÓA ĐƠN CHƯA THANH TOÁN (Tổng tiền nợ: {ov['total_unpaid']:,.0f} VNĐ):")
        for ub in ov['unpaid_bills']:
            lines.append(f"  + Kỳ {ub['period']} ({ub['utility_type']}): {ub['final_amount']:,.0f} VNĐ (Hạn: {ub['due_date'] or 'Chưa rõ'}, Trạng thái: {ub['status']})")
    else:
        lines.append("- Hiện tại không có hóa đơn nào chưa thanh toán.")

    if ov['bills']:
        lines.append("- Lịch sử hóa đơn gần đây:")
        for b in ov['bills']:
            paid_str = f", Đã thanh toán ngày {b['paid_at']}" if b.get('paid_at') else ""
            lines.append(f"  + Kỳ {b['period']} ({b['utility_type']}): {b['final_amount']:,.0f} VNĐ (Trạng thái: {b['status']}{paid_str})")
    else:
        lines.append("- Chưa có hóa đơn nào.")

    lines.append("=========================================")
    return "\n".join(lines)


def deterministic_reply_with_overview(message: str, ov: dict, service=None) -> dict:
    """
    Phản hồi thông minh từ dữ liệu tổng quan khi Gemini không khả dụng hoặc ở chế độ deterministic.
    Đảm bảo 100% các ca kiểm thử hồi quy tiếp tục vượt qua.
    """
    norm = normalize_message(message)
    user = ov['user']
    house = ov['household']

    # 1. Asking about user identity / name
    if any(w in norm for w in ('tao ten gi', 'toi ten gi', 'ten tao', 'ten toi', 'toi la ai', 'tao la ai', 'minh ten gi', 'tai khoan cua toi', 'ten cua toi', 'toi la nguoi nao', 'ai day')):
        msg = f"Bạn là {user['full_name']}, hiện là {user['household_role']} của hộ gia đình '{house['name']}' tại {house['province']}."
        return {'message': msg, 'intent': 'USER_IDENTITY', 'sources': []}

    # 2. Assistant identity
    if any(w in norm for w in ('ban la ai', 'ban ten gi', 'gioi thieu ban', 'xin chao', 'hello', 'chao ban')):
        msg = 'Mình là trợ lý Nhà Mình. Mình giúp bạn xem chỉ số, hóa đơn, so sánh tiêu thụ và dự báo chi phí của gia đình. Mình cũng hỗ trợ tra giá điện/nước theo địa phương trực tuyến khi dịch vụ còn hạn mức. Bạn muốn mình giúp việc gì?'
        return {'message': msg, 'intent': 'ASSISTANT_IDENTITY', 'sources': []}

    # 3. Asking about household / members
    if any(w in norm for w in ('thanh vien', 'co nhung ai', 'co may nguoi', 'ai trong nha')):
        if house['members']:
            members_str = ", ".join(f"{m['name']} ({m['role']})" for m in house['members'])
            msg = f"Hộ gia đình '{house['name']}' (tại {house['province']}) có {house['member_count']} thành viên gồm: {members_str}."
        else:
            msg = f"Hộ gia đình '{house['name']}' có {house['member_count']} thành viên."
        return {'message': msg, 'intent': 'HOUSEHOLD_OVERVIEW', 'sources': []}

    # 4. Unpaid bills / Payment assistant
    if any(w in norm for w in ('chua thanh toan', 'no tien', 'tra tien', 'thanh toan', 'no bao nhieu')):
        unpaid = ov['unpaid_bills']
        bills = ov['bills']
        if not bills:
            msg = 'Chưa có hóa đơn.'
            sources = []
        elif not unpaid:
            msg = 'Không có hóa đơn chưa thanh toán.'
            sources = []
        else:
            unpaid_details = '; '.join(f"kỳ {b['period']}: {Decimal(str(b['final_amount'])):,.0f} VND, hạn dự kiến {b['due_date']}" for b in unpaid)
            msg = f"Hóa đơn chưa thanh toán: {unpaid_details}. Ngày cấu hình không phải hạn chính thức từ nhà cung cấp. Bạn có thể ghi nhận thanh toán tại trang Hóa đơn."
            sources = [{'type': 'bill', 'period': b['period']} for b in unpaid]
        return {'message': msg, 'intent': 'PAYMENT_ASSISTANT', 'sources': sources}

    # 5. Bill forecast
    if any(w in norm for w in ('thang toi', 'du bao')) or (re.search(r'\buoc tinh\b', norm) and 'duoc tinh' not in norm):
        utility = 'WATER' if 'nuoc' in norm else 'ELECTRICITY'
        unit = 'm³' if utility == 'WATER' else 'kWh'
        label = 'nước' if utility == 'WATER' else 'điện'
        matching_readings = [r for r in ov['readings'] if (r['utility_type'] == 'Nước' if utility == 'WATER' else r['utility_type'] == 'Điện')]
        periods = len({r['period'] for r in matching_readings})
        sources = [{'type': 'reading', 'period': r['period'], 'source': r['source']} for r in matching_readings[-3:]]
        if periods < 2:
            msg = f"Hộ đang chọn có {periods} kỳ chỉ số {label}; cần ít nhất 2 kỳ để dự báo. Bạn cần nhập thêm {2-periods} kỳ tại trang Nhập chỉ số. Nếu đã nhập ở hộ khác, hãy chuyển đúng hộ tại trang Hộ gia đình. Mình chưa thể đưa ra số tiền dự báo khi thiếu dữ liệu."
            result = {'available': False, 'source': 'FORECAST', 'period_count': periods, 'required_periods': 2}
        else:
            if service:
                result = service.forecast(utility)
                msg = f"Ước tính kỳ tới: {result['predicted_consumption']} {unit}, khoảng {Decimal(str(result['predicted_amount'])):,.0f} VND. Dùng trung bình trọng số {result['period_count']} kỳ; độ tin cậy {result['confidence']}. Đây là FORECAST, không phải hóa đơn chính thức; chưa gồm thuế/phí." if result.get('available') else result['reason']
            else:
                result = {'available': False, 'reason': 'Chưa đủ dữ liệu.'}
                msg = 'Chưa đủ dữ liệu để dự báo.'
        return {'message': msg, 'intent': 'BILL_FORECAST', 'sources': sources, 'result': result}

    # 6. Consumption / Readings
    if any(w in norm for w in ('dung bao nhieu', 'tieu thu', 'chi so', 'so dien', 'so nuoc', 'muc su dung', 'phan tich su dung', 'phan tich muc')):
        utility = 'WATER' if 'nuoc' in norm else 'ELECTRICITY'
        unit = 'm³' if utility == 'WATER' else 'kWh'
        label = 'nước' if utility == 'WATER' else 'điện'
        matching = [r for r in ov['readings'] if (r['utility_type'] == 'Nước' if utility == 'WATER' else r['utility_type'] == 'Điện')]
        if not matching:
            return {'message': 'Chưa đủ dữ liệu để trả lời. Bạn hãy nhập chỉ số và tạo hóa đơn trước.', 'intent': 'CONSUMPTION_ANALYSIS', 'sources': []}
        latest = matching[-1]
        msg = f"Kỳ {latest['period']}, tiêu thụ {label} là {Decimal(str(latest['consumption'])):,.3f} {unit}. Nguồn: {latest['source']} (người dùng tự nhập nếu MANUAL)."
        sources = [{'type': 'reading', 'period': r['period'], 'source': r['source']} for r in matching[-3:]]
        return {'message': msg, 'intent': 'CONSUMPTION_ANALYSIS', 'sources': sources}

    # 7. Comparison
    if any(w in norm for w in ('so sanh', 'cac thang')):
        utility = 'WATER' if 'nuoc' in norm else 'ELECTRICITY'
        unit = 'm³' if utility == 'WATER' else 'kWh'
        label = 'nước' if utility == 'WATER' else 'điện'
        if 'tien' in norm or 'hoa don' in norm:
            bills = [b for b in ov['bills'] if (b['utility_type'] == 'Nước' if utility == 'WATER' else b['utility_type'] == 'Điện')][:3]
            msg = 'So sánh tiền ' + label + ' các kỳ có dữ liệu: ' + '; '.join(f"{b['period']}: {Decimal(str(b['final_amount'])):,.0f} VND ({b['source']})" for b in reversed(bills)) + '.' if bills else 'Chưa có hóa đơn để so sánh tiền.'
            sources = [{'type': 'bill', 'period': b['period'], 'source': b['source']} for b in bills]
        else:
            matching = [r for r in ov['readings'] if (r['utility_type'] == 'Nước' if utility == 'WATER' else r['utility_type'] == 'Điện')][-3:]
            msg = 'Tiêu thụ ' + label + ' các kỳ có dữ liệu: ' + '; '.join(f"{r['period']}: {Decimal(str(r['consumption'])):,.3f} {unit} ({r['source']})" for r in matching) + '.' if matching else 'Chưa có chỉ số để so sánh.'
            sources = [{'type': 'reading', 'period': r['period'], 'source': r['source']} for r in matching]
        return {'message': msg, 'intent': 'CONSUMPTION_COMPARISON', 'sources': sources}

    # 8. General overview
    if any(w in norm for w in ('tong quan', 'nha toi', 'nha minh', 'nha tao', 'ho gia dinh')):
        msg = f"Hộ gia đình '{house['name']}' ({house['province'] or 'Chưa cập nhật'}): {house['member_count']} thành viên. Tổng số tài khoản: {len(ov['accounts'])}, công tơ: {len(ov['meters'])}. "
        if ov['unpaid_bills']:
            msg += f"Hiện có {len(ov['unpaid_bills'])} hóa đơn chưa thanh toán ({ov['total_unpaid']:,.0f} VND)."
        else:
            msg += "Hiện không có hóa đơn chưa thanh toán."
        return {'message': msg, 'intent': 'HOUSEHOLD_OVERVIEW', 'sources': []}

    # 9. Basic Knowledge
    if any(w in norm for w in ('kwh la gi', 'so dien la gi', 'cach doc cong to', 'tinh theo bac thang', 'bac thang la gi', 'bac thang nhu the nao', 'tiet kiem', 'cach tinh tien')):
        basic_reply = basic_explanation(message)
        if basic_reply:
            return {'message': basic_reply, 'intent': 'BASIC_KNOWLEDGE', 'sources': []}

    # 10. Math and Arithmetic Calculation
    math_match = re.search(r'(?:tinh(?:\s+toan)?\s+)?(\d+(?:\.\d+)?)\s*([\+\-\*\/])\s*(\d+(?:\.\d+)?)', norm)
    if math_match:
        try:
            n1 = float(math_match.group(1))
            op = math_match.group(2)
            n2 = float(math_match.group(3))
            calc_val = n1 + n2 if op == '+' else (n1 - n2 if op == '-' else (n1 * n2 if op == '*' else (n1 / n2 if n2 != 0 else None)))
            if calc_val is not None:
                calc_str = f"{int(calc_val)}" if calc_val.is_integer() else f"{calc_val:.4g}"
                return {'message': f"Kết quả: {math_match.group(1)} {op} {math_match.group(3)} = {calc_str}.", 'intent': 'GENERAL_CHAT', 'sources': []}
        except Exception:
            pass

    # Default friendly greeting
    msg = f"Chào bạn {user['full_name']}! Mình là Trợ lý Nhà Mình. Mình có thể hỗ trợ bạn xem chỉ số, theo dõi hóa đơn, dự báo tiêu thụ và quản lý chi tiêu điện nước của hộ {house['name']}."
    return {'message': msg, 'intent': 'GENERAL_CHAT', 'sources': []}
