'use client';
export type KnowledgeDocument={id:string;title:string;content:string;status?:string;url?:string;metadata:Record<string,unknown>;readiness?:{can_publish:boolean;missing:string[]}};
const reasons:Record<string,string>={READABLE_TEXT:'Tài liệu chưa có nội dung chữ đủ để xác minh.',EFFECTIVE_DATE:'Ngày hiệu lực chưa được xác minh.',SCOPE:'Phạm vi áp dụng chưa được xác minh.',CLASSIFICATION:'Chưa xác định đúng loại tài liệu.',CONFLICTS:'Có trường dữ liệu thiếu căn cứ hoặc mâu thuẫn.'};
export function KnowledgeDocumentViewer({document:doc,busy,onClose,onPublish,onBlock,onDownload}:{document:KnowledgeDocument;busy:boolean;onClose:()=>void;onPublish:()=>void;onBlock:()=>void;onDownload:()=>void}){
 return <section aria-label="Nội dung tài liệu" className="rounded-xl border border-blue-200 bg-white p-5 space-y-4 shadow-sm">
  <div className="flex flex-wrap justify-between gap-3"><h2 className="text-lg font-semibold">{doc.title}</h2><button onClick={onClose} className="underline">Đóng nội dung</button></div>
  {doc.url&&<a href={doc.url} target="_blank" rel="noopener noreferrer" className="text-blue-700 underline break-all">Xem tại nguồn chính thức</a>}
  <p className="text-sm text-slate-600">Nội dung trích xuất từ bản gốc; tài liệu chờ duyệt chưa được dùng để trả lời.</p>
  {doc.readiness&&!doc.readiness.can_publish&&<div role="status" className="rounded-lg bg-amber-50 p-3"><strong>Chưa thể công bố</strong><ul className="list-disc pl-5">{doc.readiness.missing.map(reason=><li key={reason}>{reasons[reason]||reason}</li>)}</ul></div>}
  {doc.content.trim()?<pre className="whitespace-pre-wrap break-words text-sm max-h-[28rem] overflow-auto font-sans border rounded-lg p-4">{doc.content}</pre>:<p>Tài liệu chưa có nội dung chữ. Hãy tải bản gốc để kiểm tra ảnh scan.</p>}
  <div className="flex flex-wrap gap-4"><button disabled={busy} onClick={onDownload} className="underline">Tải bản gốc</button>{doc.status!=='PUBLISHED'&&<button disabled={busy||doc.readiness?.can_publish===false} onClick={onPublish} className="text-blue-700 underline disabled:opacity-50">Công bố tài liệu đã xác minh</button>}{doc.status!=='BLOCKED'&&<button disabled={busy} onClick={onBlock} className="text-red-700 underline">Chặn tài liệu</button>}</div>
 </section>;
}
