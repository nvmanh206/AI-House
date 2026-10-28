const base = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api';
let token: string | null = null;
let refreshing: Promise<boolean> | null = null;
export function setToken(value: string | null) { token=value; }
export async function download(path:string){
  const request=()=>fetch(base+path,{credentials:'include',headers:token?{Authorization:'Bearer '+token}:{}});
  let response=await request();
  if(response.status===401&&await refreshSession())response=await request();
  if(!response.ok)throw new Error('Không tải được bản gốc. Vui lòng thử lại.');
  const url=URL.createObjectURL(await response.blob());
  const disposition=response.headers.get('Content-Disposition')||'';
  const filename=disposition.match(/filename\*=UTF-8''([^;]+)/i)?.[1]||disposition.match(/filename="([^"]+)"/i)?.[1];
  const anchor=document.createElement('a');anchor.href=url;
  try{anchor.download=filename?decodeURIComponent(filename).split(/[\\/]/).pop()||'tai-lieu-goc':'tai-lieu-goc';}catch{anchor.download='tai-lieu-goc';}
  document.body.appendChild(anchor);anchor.click();anchor.remove();
  setTimeout(()=>URL.revokeObjectURL(url),1000);
}
export async function refreshSession() {
  if (!refreshing) refreshing=fetch(base+'/auth/refresh',{method:'POST',credentials:'include',signal:AbortSignal.timeout(15000)}).then(async r=>{if(!r.ok)return false; token=(await r.json()).access_token; return true;}).catch(()=>false).finally(()=>{refreshing=null});
  return refreshing;
}
export async function api(path:string,method='GET',body?:unknown,retry=true,timeoutMs?:number):Promise<any> {
  let response:Response;
  try { response=await fetch(base+path,{method,credentials:'include',headers:{'Content-Type':'application/json',...(token?{Authorization:'Bearer '+token}:{})},...(body===undefined?{}:{body:JSON.stringify(body)}),...(timeoutMs?{signal:AbortSignal.timeout(timeoutMs)}:{})}); }
  catch(e:any) {
    if(e?.name==='TimeoutError'||e?.name==='AbortError')throw new Error('Máy chủ phản hồi quá lâu. Vui lòng thử lại sau ít phút.');
    throw new Error('Không kết nối được máy chủ. Kiểm tra backend đang chạy.');
  }
  if(response.status===401 && retry && !path.startsWith('/auth/') && await refreshSession()) return api(path,method,body,false,timeoutMs);
  const data=await response.json();
  if(!response.ok) {
    const msg = data.error?.message || 'Không thể thực hiện yêu cầu.';
    const fieldsDetail = data.error?.fields?.map((f:any)=>`${f.field}: ${f.message}`).join('; ');
    throw Object.assign(new Error(fieldsDetail ? `${msg} (${fieldsDetail})` : msg),{code:data.error?.code,retryAfter:data.error?.retry_after});
  }
  return data;
}
