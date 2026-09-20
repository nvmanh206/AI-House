const base = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api';
let token: string | null = null;
let refreshing: Promise<boolean> | null = null;
export function setToken(value: string | null) { token=value; }
export async function refreshSession() {
  if (!refreshing) refreshing=fetch(base+'/auth/refresh',{method:'POST',credentials:'include'}).then(async r=>{if(!r.ok)return false; token=(await r.json()).access_token; return true;}).catch(()=>false).finally(()=>{refreshing=null});
  return refreshing;
}
export async function api(path:string,method='GET',body?:unknown,retry=true):Promise<any> {
  let response:Response;
  try { response=await fetch(base+path,{method,credentials:'include',headers:{'Content-Type':'application/json',...(token?{Authorization:'Bearer '+token}:{})},...(body===undefined?{}:{body:JSON.stringify(body)})}); }
  catch {throw new Error('Không kết nối được máy chủ. Kiểm tra backend đang chạy.');}
  if(response.status===401 && retry && !path.startsWith('/auth/') && await refreshSession()) return api(path,method,body,false);
  const data=await response.json();
  if(!response.ok) {
    const msg = data.error?.message || 'Không thể thực hiện yêu cầu.';
    const fieldsDetail = data.error?.fields?.map((f:any)=>`${f.field}: ${f.message}`).join('; ');
    throw new Error(fieldsDetail ? `${msg} (${fieldsDetail})` : msg);
  }
  return data;
}
