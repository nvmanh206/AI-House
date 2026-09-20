# Database

Schema chuẩn PostgreSQL; SQLAlchemy Numeric cho tiền/chỉ số, JSON cho snapshot và permissions, timestamps timezone-aware.

- **users**: email unique, Argon2 hash, role USER/MEMBER/ADMIN, is_active, timestamps.
- **households**: thông tin địa chỉ/số người, owner_user_id → users.
- **household_members**: household_id → households, user_id → users; unique pair; role OWNER/MEMBER; permissions write/pay. MEMBER là vai trò membership, global user có thể vẫn là USER.
- **auth_sessions**: user_id, household_id hiện tại đã authorize, refresh_hash, expiry/revocation. Không lưu refresh token thô.
- **utility_accounts**: household, ELECTRICITY/WATER, provider/customer codes, billing_day/due_day/reminder, nguồn và sync metadata.
- **meters**: household và account, mã, unit, initial_reading, active.
- **billing_periods**: household, year/month unique, start/end/status.
- **meter_readings**: meter + period unique; previous/current/consumption Numeric; check current >= previous và consumption >= 0; source/confidence/image/confirmation/creator.
- **tariffs**: utility/provider/version unique, hiệu lực và active.
- **tariff_tiers**: tariff, from/to/unit_price/order; unique order per tariff. Pydantic kiểm tra các bậc liên tục từ 0, bậc cuối vô hạn.
- **bills**: household/account/period; unique account + period và bill_code; estimated/official/final amount; due_date/status/source; immutable tariff và breakdown snapshot.
- **payments**: bill_id unique cho full payment V1, amount/method/reference/status/paid_at.
- **notifications**: user/household/type/title/message/read/scheduled/sent; dedupe_key unique theo sự kiện + người nhận.
- **ai_analyses**: household/user/intent/input period/model; chỉ lưu trạng thái và số nguồn, không prompt/raw message/chain-of-thought.
- **audit_logs**: actor/household/action/entity; metadata đã hạn chế, không secret. Trường ORM `details` ánh xạ cột `metadata`.

## Quan hệ

User 1→N owned households; users N↔N households qua membership. Household 1→N accounts, meters, periods, bills. Account 1→N meters/bills. Meter 1→N readings. Period 1→N readings/bills. Tariff 1→N tiers. Bill 1→0..1 full manual payment. Notification gắn một user trong một household.

## Migration

Initial migration là các `op.create_table`/constraints đã được Alembic sinh và lưu cố định; không gọi `Base.metadata.create_all` trong app startup hay migration. `alembic upgrade head` trước khi chạy. Seed là lệnh riêng. Test unit có thể dùng create_all để tạo fixture nhanh; không thay thế migration validation.

Không xóa cascade lịch sử thanh toán/hóa đơn. V1 vô hiệu hóa công tơ và tài khoản người dùng; không cung cấp xóa household lịch sử.
