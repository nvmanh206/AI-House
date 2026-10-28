'use client';
export function NoticeToast({message,onClose}:{message:string;onClose:()=>void}){
 if(!message)return null;
 return <div className="toast-message" role="status" aria-live="polite" aria-atomic="true"><span>{message}</span><button type="button" aria-label="Đóng thông báo" onClick={onClose} style={{color:'inherit',background:'transparent',border:0,padding:'8px',cursor:'pointer'}}>✕</button></div>;
}
