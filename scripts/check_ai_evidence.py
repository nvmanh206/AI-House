#!/usr/bin/env python3
"""
scripts/check_ai_evidence.py
Automated validation of AI Development Documentation, Skills, Rules, and Prompts.
Ensures consistency, valid frontmatter, zero broken links, and zero credentials before commit.
"""
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
AGENTS_DIR = ROOT / ".agents"
PROMPTS_DIR = ROOT / "prompts"

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

errors = []
warnings = []
stats = {
    "skills": 0,
    "rules": 0,
    "prompts": 0,
    "links_checked": 0,
    "diagrams": 0,
}

def log_pass(msg):
    print(f"  {GREEN}[PASS]{RESET} {msg}")

def log_fail(msg):
    print(f"  {RED}[FAIL]{RESET} {msg}")
    errors.append(msg)

def log_warn(msg):
    print(f"  {YELLOW}[WARN]{RESET} {msg}")
    warnings.append(msg)

def check_skills():
    print(f"\n{BOLD}{CYAN}1. Kiểm tra Agent Skills (.agents/skills/){RESET}")
    skills_dir = AGENTS_DIR / "skills"
    if not skills_dir.exists():
        log_fail("Thư mục .agents/skills/ không tồn tại.")
        return

    required_skills = [
        "nha-minh-requirements-planning",
        "nha-minh-implementation",
        "nha-minh-five-layer-testing",
        "nha-minh-security-optimization",
        "nha-minh-documentation-evidence",
        "system-design-orchestrator",
        "architecture-c4",
        "uml-use-case",
        "uml-code-tracer",
        "uml-usecase-generator",
        "diagram-design",
        "diagram-renderer",
    ]

    for req in required_skills:
        req_path = skills_dir / req
        if not req_path.is_dir():
            log_fail(f"Thiếu skill quan trọng: {req}")
        else:
            skill_md = req_path / "SKILL.md"
            if not skill_md.exists():
                log_fail(f"Skill {req} thiếu file SKILL.md")

    for s_path in sorted(skills_dir.iterdir()):
        if s_path.is_dir():
            stats["skills"] += 1
            skill_md = s_path / "SKILL.md"
            if not skill_md.exists():
                log_fail(f"Thư mục skill {s_path.name} thiếu SKILL.md")
                continue
            content = skill_md.read_text(encoding="utf-8")
            if not content.startswith("---"):
                log_fail(f"Skill {s_path.name}/SKILL.md thiếu YAML frontmatter bắt đầu bằng '---'")
            elif "name:" not in content or "description:" not in content:
                log_fail(f"Skill {s_path.name}/SKILL.md thiếu thuộc tính 'name' hoặc 'description'")

    log_pass(f"Đã kiểm tra {stats['skills']} Agent Skills. Tất cả đều có SKILL.md hợp lệ.")

def check_rules():
    print(f"\n{BOLD}{CYAN}2. Kiểm tra Agent Rules (.agents/rules/){RESET}")
    rules_dir = AGENTS_DIR / "rules"
    if not rules_dir.exists():
        log_fail("Thư mục .agents/rules/ không tồn tại.")
        return

    expected_rules = [
        "01-coding-conventions.md",
        "02-architecture.md",
        "03-sdlc.md",
        "04-quality-security.md",
        "05-ai-evidence.md",
        "README.md"
    ]

    for r in expected_rules:
        r_path = rules_dir / r
        if not r_path.is_file():
            log_fail(f"Thiếu rule file: {r}")
        else:
            stats["rules"] += 1
            if r_path.stat().st_size < 50:
                log_warn(f"Rule {r} có nội dung quá ngắn ({r_path.stat().st_size} bytes)")

    log_pass(f"Đã kiểm tra {stats['rules']} Rule files phục vụ AI Coding Agent.")

def check_diagrams():
    print(f"\n{BOLD}{CYAN}3. Kiểm tra Hướng dẫn Sơ đồ (.agents/diagrams/){RESET}")
    diag_dir = AGENTS_DIR / "diagrams"
    if not diag_dir.exists():
        log_fail("Thư mục .agents/diagrams/ không tồn tại.")
        return

    diag_readme = diag_dir / "README.md"
    if not diag_readme.exists():
        log_fail(".agents/diagrams/ thiếu README.md")
    else:
        log_pass("Tồn tại .agents/diagrams/README.md hướng dẫn toàn diện.")

    sdlc_skill = diag_dir / "sdlc-diagrams" / "SKILL.md"
    if not sdlc_skill.exists():
        log_fail("Thiếu .agents/diagrams/sdlc-diagrams/SKILL.md")
    else:
        log_pass("Tồn tại workflow tạo sơ đồ SDLC chuẩn hóa.")

def check_prompts():
    print(f"\n{BOLD}{CYAN}4. Kiểm tra Prompt SDLC (prompts/){RESET}")
    if not PROMPTS_DIR.exists():
        log_fail("Thư mục prompts/ không tồn tại.")
        return

    sdlc_stages = [
        "01-requirements",
        "02-planning",
        "03-design",
        "04-implementation",
        "05-testing",
        "06-deployment",
        "07-optimization",
        "08-documentation",
    ]

    prompt_files = []
    for stage in sdlc_stages:
        stage_dir = PROMPTS_DIR / stage
        if not stage_dir.is_dir():
            log_fail(f"Thiếu thư mục giai đoạn SDLC: prompts/{stage}")
            continue
        stage_files = list(stage_dir.glob("*.md"))
        if not stage_files:
            log_warn(f"Thư mục prompts/{stage} chưa có file prompt nào.")
        prompt_files.extend(stage_files)

    stats["prompts"] = len(prompt_files)

    for pf in prompt_files:
        content = pf.read_text(encoding="utf-8")
        if not content.startswith("---"):
            log_fail(f"File {pf.relative_to(ROOT)} thiếu YAML frontmatter.")
            continue
        fm_match = re.search(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
        if not fm_match:
            log_fail(f"File {pf.relative_to(ROOT)} có YAML frontmatter không hợp lệ.")
            continue
        fm_text = fm_match.group(1)
        if "id:" not in fm_text or "status:" not in fm_text:
            log_fail(f"File {pf.relative_to(ROOT)} thiếu trường 'id' hoặc 'status' trong frontmatter.")

        lower_c = content.lower()
        if "mục đích" not in lower_c and "purpose" not in lower_c:
            log_warn(f"File {pf.relative_to(ROOT)} thiếu tiêu mục 'Mục đích'.")
        if "yêu cầu" not in lower_c and "prompt" not in lower_c:
            log_warn(f"File {pf.relative_to(ROOT)} thiếu tiêu mục 'Nội dung yêu cầu'.")

    log_pass(f"Đã kiểm tra {stats['prompts']} prompt files qua 8 giai đoạn SDLC.")

def check_manifest_and_traceability():
    print(f"\n{BOLD}{CYAN}5. Kiểm tra Manifest & Ma trận Truy vết (TRACEABILITY.md){RESET}")
    manifest_file = PROMPTS_DIR / "manifest.json"
    if not manifest_file.exists():
        log_fail("prompts/manifest.json không tồn tại.")
    else:
        try:
            m_data = json.loads(manifest_file.read_text(encoding="utf-8"))
            if "prompts" not in m_data:
                log_fail("manifest.json thiếu mảng 'prompts'.")
            else:
                log_pass(f"manifest.json hợp lệ, quản lý {len(m_data['prompts'])} bản ghi prompt.")
        except Exception as e:
            log_fail(f"Lỗi parse prompts/manifest.json: {e}")

    trace_file = PROMPTS_DIR / "TRACEABILITY.md"
    if not trace_file.exists():
        log_fail("prompts/TRACEABILITY.md không tồn tại.")
        return

    content = trace_file.read_text(encoding="utf-8")
    links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", content)
    broken = []
    for text, link in links:
        if link.startswith("http://") or link.startswith("https://") or link.startswith("mailto:"):
            continue
        clean_target = link.split("#")[0]
        if not clean_target:
            continue
        target_path = (PROMPTS_DIR / clean_target).resolve()
        stats["links_checked"] += 1
        if not target_path.exists():
            broken.append((text, link))

    if broken:
        for b_text, b_link in broken:
            log_fail(f"Broken link trong TRACEABILITY.md: [{b_text}]({b_link})")
    else:
        log_pass(f"Đã kiểm tra {stats['links_checked']} liên kết trong TRACEABILITY.md. 100% liên kết đều tồn tại.")

def check_security():
    print(f"\n{BOLD}{CYAN}6. Rà soát An toàn & Bảo mật (Không lộ Secrets/Credentials){RESET}")
    secret_pattern = re.compile(
        r"(?:AIza|AQ\.)[0-9A-Za-z_-]{30,}|gh[pousr]_[A-Za-z0-9]{30,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"
    )
    found_secrets = []
    for folder in [AGENTS_DIR, PROMPTS_DIR]:
        for p in folder.rglob("*"):
            if p.is_file() and p.suffix in [".md", ".json", ".txt", ".yaml", ".yml", ".py", ".puml", ".mmd"]:
                try:
                    txt = p.read_text(encoding="utf-8", errors="ignore")
                    if secret_pattern.search(txt):
                        found_secrets.append(p.relative_to(ROOT))
                except Exception:
                    pass

    if found_secrets:
        for s in found_secrets:
            log_fail(f"Phát hiện dấu hiệu API key hoặc Private Key tại: {s}")
    else:
        log_pass("Không phát hiện bất kỳ secret, API key hay private key nào trong tài liệu minh chứng.")

def main():
    print(f"{BOLD}=== KIỂM TRA CHUẨN HÓA TÀI LIỆU MINH CHỨNG PHÁT TRIỂN AI ==={RESET}")
    print(f"Dự án: Hệ thống quản lý hóa đơn điện nước hộ gia đình tích hợp AI (Nhà Mình)")
    print(f"Thư mục gốc: {ROOT}\n")

    check_skills()
    check_rules()
    check_diagrams()
    check_prompts()
    check_manifest_and_traceability()
    check_security()

    print(f"\n{BOLD}=== TỔNG KẾT KẾT QUẢ KIỂM TRA ==={RESET}")
    print(f"- Tổng số Agent Skills: {stats['skills']}")
    print(f"- Tổng số Agent Rules: {stats['rules']}")
    print(f"- Tổng số SDLC Prompts: {stats['prompts']}")
    print(f"- Tổng số liên kết kiểm chứng: {stats['links_checked']}")
    print(f"- Số cảnh báo (Warnings): {len(warnings)}")
    print(f"- Số lỗi chặn (Errors): {len(errors)}")

    if errors:
        print(f"\n{RED}{BOLD}KIỂM TRA THẤT BẠI: Vui lòng sửa {len(errors)} lỗi trước khi commit!{RESET}")
        sys.exit(1)
    else:
        print(f"\n{GREEN}{BOLD}KIỂM TRA THÀNH CÔNG: Tài liệu minh chứng đạt chuẩn 100%, sẵn sàng commit và push lên GitHub!{RESET}")
        sys.exit(0)

if __name__ == "__main__":
    main()
