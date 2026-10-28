"""EVN public-data fetcher: JSON CLI and callable tool for AI agents."""
from __future__ import annotations
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup
import trafilatura

BASE = "https://www.evn.com.vn"
SOURCES = {
    "operation": BASE + "/vi-VN/news-l/Thong-tin-tom-tat-van-hanh-HTD-Quoc-gia-60-2015",
    "prices": BASE + "/vi-VN/news-l/Gia-dien-60-28",
    "news": BASE + "/vi-VN/tin-tuc/",
}
HEADERS = {"User-Agent": "EVNDataReader/1.0 (public-data research; respectful crawl)", "Accept-Language": "vi-VN,vi;q=0.9"}
DATE_RE = re.compile(r"\b(\d{2}/\d{2}/\d{4})\b")
OPERATION_RE = re.compile(r"(?:Thông tin (?:chung|tóm tắt) về )?vận hành (?:hệ thống điện|HTĐ) (?:Quốc gia|quốc gia)", re.I)


def evn_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme == "https" and (parsed.hostname == "evn.com.vn" or (parsed.hostname or "").endswith(".evn.com.vn"))


def get_html(client: httpx.Client, url: str) -> str:
    if not evn_url(url):
        raise ValueError("Blocked non-EVN URL")
    response = client.get(url, follow_redirects=True)
    response.raise_for_status()
    if not evn_url(str(response.url)):
        raise ValueError("Unexpected non-EVN redirect")
    if "html" not in response.headers.get("content-type", "").lower():
        raise ValueError("Expected EVN HTML page")
    return response.text


def find_articles(html: str, listing_url: str, category: str, limit: int) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    articles, seen = [], set()
    for a in soup.find_all("a", href=True):
        url = urljoin(listing_url, a["href"])
        if not evn_url(url) or not re.search(r"/d/vi-VN/news(?:-pdf|-d)?/", url, re.I):
            continue
        title = a.get_text(" ", strip=True)
        if not title:
            title = (a.get("title") or "").strip()
        if len(title) < 12 or url in seen:
            continue
        if category == "operation" and not OPERATION_RE.search(title):
            continue
        if category == "prices" and not re.search(r"giá điện|giá bán|biểu giá|điện bình quân", title, re.I):
            continue
        seen.add(url)
        parent_text = a.parent.get_text(" ", strip=True)[:500] if a.parent else title
        date_match = DATE_RE.search(parent_text)
        articles.append({"title": title, "url": url, "published_hint": date_match.group(1) if date_match else None})
        if len(articles) >= limit:
            break
    return articles


def extract_article(html: str) -> str:
    text = trafilatura.extract(html, include_tables=True, include_comments=False, favor_precision=True)
    if text:
        return text.strip()
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "form"]):
        tag.decompose()
    body = soup.find("article") or soup.find("main") or soup.body
    return body.get_text("\n", strip=True)[:30000] if body else ""


def parse_vi_number(raw: str) -> float:
    s = raw.strip().replace(" ", "")
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    return float(s)


def parse_operation(text: str) -> dict:
    patterns = {
        "peak_mw": r"Công suất lớn nhất trong ngày\s*:?\s*([\d.,]+)\s*MW",
        "energy_million_kwh": r"Sản lượng điện sản xuất và nhập khẩu\s*:?\s*([\d.,]+)\s*triệu\s*kWh",
    }
    out = {}
    for name, pattern in patterns.items():
        match = re.search(pattern, text, re.I)
        if match:
            out[name] = parse_vi_number(match.group(1))
    matches = DATE_RE.findall(text[:500])
    if matches:
        out["reported_dates"] = list(dict.fromkeys(matches))
    # EVN often publishes both commercial and generation-end estimates. Avoid
    # claiming that a single parsed value covers both accounting methods.
    out["extraction_note"] = "First matching figures only; inspect raw_text for alternative rooftop-solar accounting methods."
    return out


def fetch_evn(category: str = "operation", limit: int = 3, output_dir: str = "data") -> dict:
    """Fetch public EVN articles and return structured, source-linked JSON."""
    if category not in SOURCES:
        raise ValueError(f"category must be one of {list(SOURCES)}")
    if not 1 <= limit <= 20:
        raise ValueError("limit must be between 1 and 20")
    retrieved_at = datetime.now(timezone.utc).isoformat()
    with httpx.Client(headers=HEADERS, timeout=25.0) as client:
        listing = get_html(client, SOURCES[category])
        refs = find_articles(listing, SOURCES[category], category, limit)
        if not refs:
            raise RuntimeError("No articles found: EVN markup may have changed or content requires JavaScript.")
        results = []
        for ref in refs:
            try:
                text = extract_article(get_html(client, ref["url"]))
                if not text or len(text) < 80:
                    raise ValueError("Article content was empty/too short")
                item = {**ref, "raw_text": text, "retrieved_at_utc": retrieved_at}
                if category == "operation":
                    item["parsed_metrics"] = parse_operation(text)
                results.append(item)
            except (httpx.HTTPError, ValueError) as exc:
                results.append({**ref, "error": str(exc)})
    output = {"source": "EVN official website", "category": category, "listing_url": SOURCES[category], "retrieved_at_utc": retrieved_at, "articles": results}
    folder = Path(output_dir)
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f"evn_{category}_latest.json").write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    return output


def main() -> int:
    p = argparse.ArgumentParser(description="Fetch current public EVN articles")
    p.add_argument("--category", choices=SOURCES, default="operation")
    p.add_argument("--limit", type=int, default=3)
    p.add_argument("--output-dir", default="data")
    args = p.parse_args()
    try:
        print(json.dumps(fetch_evn(args.category, args.limit, args.output_dir), ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        print(json.dumps({"error": str(exc), "category": args.category}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
