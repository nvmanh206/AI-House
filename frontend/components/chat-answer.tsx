'use client';

import React from 'react';

type Source = {
    type: string;
    index?: number;
    title?: string;
    url?: string;
    period?: string;
    source?: string;
    effective_from?: string;
    checked_at?: string;
};

// Helper function to render inline markdown syntax (**bold**, *italic*, `code`, and [1] citations)
function renderInlineMarkdown(text: string, sources: Source[] = []) {
    if (!text) return null;

    // Pattern to match citations [1], inline code `code`, bold **text**, and italic *text*
    const tokens = text.split(/(\[\d+\]|`[^`]+`|\*\*[^*]+\*\*|\*[^*]+\*)/g);

    return tokens.map((token, index) => {
        if (!token) return null;

        // 1. Citation matching [1], [2]
        const citationMatch = /^\[(\d+)\]$/.exec(token);
        if (citationMatch) {
            const idxNum = Number(citationMatch[1]);
            const source = sources.find(s => s.index === idxNum && ['web', 'knowledge'].includes(s.type));
            if (source?.url?.startsWith('https://')) {
                return (
                    <a
                        key={index}
                        href={source.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-citation text-blue-600 font-semibold underline hover:text-blue-800 transition-colors"
                    >
                        {token}
                    </a>
                );
            }
            return <span key={index} className="inline-citation text-slate-500 font-semibold">{token}</span>;
        }

        // 2. Inline Code `code`
        if (token.startsWith('`') && token.endsWith('`') && token.length > 2) {
            return (
                <code key={index} className="px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-purple-700 dark:text-purple-300 font-mono text-xs border border-slate-200/80">
                    {token.slice(1, -1)}
                </code>
            );
        }

        // 3. Bold **text**
        if (token.startsWith('**') && token.endsWith('**') && token.length > 4) {
            return (
                <strong key={index} className="font-semibold text-slate-900 dark:text-slate-100">
                    {token.slice(2, -2)}
                </strong>
            );
        }

        // 4. Italic *text*
        if (token.startsWith('*') && token.endsWith('*') && token.length > 2) {
            return (
                <em key={index} className="italic text-slate-700 dark:text-slate-300">
                    {token.slice(1, -1)}
                </em>
            );
        }

        // Standard text
        return <React.Fragment key={index}>{token}</React.Fragment>;
    });
}

// Full Markdown Block Parser
export function ChatAnswer({ answer }: { answer: { message: string; sources?: Source[]; metadata?: { search_suggestions_html?: string; warnings?: string[]; degraded?: boolean } } }) {
    const sources = (answer.sources || []).filter(source => source.type !== 'evidence');
    // GEMINI_* codes describe the degraded answer; the rest describe knowledge retrieval.
    const allWarnings = answer.metadata?.warnings || [];
    const knowledgeWarnings = allWarnings.filter(w => !w.startsWith('GEMINI_'));
    const rawMessage = answer.message || '';

    // Split text into block lines
    const lines = rawMessage.split('\n');

    const blocks: React.ReactNode[] = [];
    let currentListItems: React.ReactNode[] = [];
    let isOrderedList = false;

    const flushList = () => {
        if (currentListItems.length > 0) {
            const ListTag = isOrderedList ? 'ol' : 'ul';
            const listClass = isOrderedList
                ? 'list-decimal pl-5 space-y-1.5 my-2 text-slate-700 dark:text-slate-200'
                : 'list-disc pl-5 space-y-1.5 my-2 text-slate-700 dark:text-slate-200';

            blocks.push(
                <ListTag key={`list-${blocks.length}`} className={listClass}>
                    {currentListItems}
                </ListTag>
            );
            currentListItems = [];
        }
    };

    lines.forEach((line, lineIdx) => {
        const trimmed = line.trim();

        // Empty line
        if (!trimmed) {
            flushList();
            return;
        }

        // Horizontal Rule (--- or ***)
        if (trimmed === '---' || trimmed === '***' || trimmed === '___') {
            flushList();
            blocks.push(<hr key={lineIdx} className="my-3 border-t border-slate-200/80 dark:border-slate-700/80" />);
            return;
        }

        // Headings (###, ##, #)
        if (trimmed.startsWith('#')) {
            flushList();
            const level = trimmed.match(/^#+/)?.[0].length || 1;
            const headingText = trimmed.replace(/^#+\s*/, '');
            const content = renderInlineMarkdown(headingText, sources);

            if (level === 1 || level === 2) {
                blocks.push(
                    <h3 key={lineIdx} className="text-base font-bold text-slate-900 dark:text-white mt-3 mb-1.5 tracking-tight flex items-center gap-2">
                        {content}
                    </h3>
                );
            } else {
                blocks.push(
                    <h4 key={lineIdx} className="text-sm font-semibold text-slate-800 dark:text-slate-100 mt-2.5 mb-1 tracking-tight">
                        {content}
                    </h4>
                );
            }
            return;
        }

        // Unordered List (- item or * item)
        const bulletMatch = /^[*-]\s+(.*)$/.exec(trimmed);
        if (bulletMatch) {
            if (isOrderedList && currentListItems.length > 0) flushList();
            isOrderedList = false;
            currentListItems.push(
                <li key={lineIdx} className="text-sm leading-relaxed">
                    {renderInlineMarkdown(bulletMatch[1], sources)}
                </li>
            );
            return;
        }

        // Ordered List (1. item)
        const numberMatch = /^\d+\.\s+(.*)$/.exec(trimmed);
        if (numberMatch) {
            if (!isOrderedList && currentListItems.length > 0) flushList();
            isOrderedList = true;
            currentListItems.push(
                <li key={lineIdx} className="text-sm leading-relaxed">
                    {renderInlineMarkdown(numberMatch[1], sources)}
                </li>
            );
            return;
        }

        // Regular Paragraph
        flushList();
        blocks.push(
            <p key={lineIdx} className="text-sm leading-relaxed mb-2 text-slate-700 dark:text-slate-200">
                {renderInlineMarkdown(line, sources)}
            </p>
        );
    });

    flushList();

    return (
        <div className="chat-markdown-body space-y-1 text-slate-800 dark:text-slate-100">
            {blocks}
            {answer.metadata?.degraded ? <p role="status" className="text-xs text-amber-800 mt-3">
                {allWarnings.includes('GEMINI_TIMEOUT')
                    ? 'AI phản hồi quá chậm; câu trả lời được lấy từ dữ liệu nội bộ.'
                    : allWarnings.includes('GEMINI_QUOTA')
                        ? 'AI tạm hết hạn mức; câu trả lời được lấy từ dữ liệu nội bộ.'
                        : 'AI tạm thời không trả lời được; câu trả lời được lấy từ dữ liệu nội bộ.'}
            </p> : null}
            {knowledgeWarnings.length ? <p role="status" className="text-xs text-amber-800 mt-3">
                {knowledgeWarnings.includes('PRICE_SOURCE_STALE')
                    ? 'Nguồn giá chưa được kiểm tra thành công trong 24 giờ; chưa bảo đảm giá hiện hành.'
                    : knowledgeWarnings.includes('EMBEDDING_UNAVAILABLE')
                        ? 'Đang tìm tài liệu bằng từ khóa; tìm kiếm ngữ nghĩa tạm thời chưa khả dụng.'
                        : 'Kho tri thức chưa có đủ căn cứ phù hợp cho lượt hỏi này.'}
            </p> : null}

            {/* Citations Footer */}
            {sources.length > 0 && (
                <div className="citations mt-3 pt-2 border-t border-slate-100 dark:border-slate-800 text-xs text-slate-500 flex flex-wrap gap-2">
                    {sources.map((s, i) =>
                        ['web', 'knowledge'].includes(s.type) && s.url?.startsWith('https://') ? (
                            <a
                                key={i}
                                href={s.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-blue-600 dark:text-blue-400 underline hover:text-blue-800"
                            >
                                [{s.index}] {s.title}
                                {s.effective_from && ` · Hiệu lực ${s.effective_from}`}
                                {s.checked_at && ` · Kiểm tra ${new Date(s.checked_at).toLocaleDateString('vi-VN')}`}
                            </a>
                        ) : (
                            <span key={i} className="inline-flex items-center gap-1 bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded-full text-[11px] font-medium text-slate-600 dark:text-slate-300">
                                {s.type === 'bill' ? '🧾 Hóa đơn' : '⚡ Chỉ số'} {s.period} {s.source && `· ${s.source}`}
                            </span>
                        )
                    )}
                </div>
            )}

            {/* Google Search Suggestions HTML Iframe */}
            {answer.metadata?.search_suggestions_html && (
                <iframe
                    title="Gợi ý Google Search"
                    sandbox="allow-popups allow-popups-to-escape-sandbox"
                    referrerPolicy="no-referrer"
                    srcDoc={answer.metadata.search_suggestions_html}
                    className="w-full h-40 border-0 mt-3 rounded-xl bg-slate-50 dark:bg-slate-900"
                />
            )}
        </div>
    );
}
