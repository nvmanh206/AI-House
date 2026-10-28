const test=require('node:test');const assert=require('node:assert/strict');
const fs=require('node:fs');const path=require('node:path');const Module=require('node:module');const ts=require('typescript');
function client(){
 const filename=path.resolve(__dirname,'../components/api.ts');const mod=new Module(filename,module);
 mod.filename=filename;mod.paths=Module._nodeModulePaths(path.dirname(filename));
 mod._compile(ts.transpileModule(fs.readFileSync(filename,'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS}}).outputText,filename);return mod.exports;
}
test('same-origin authentication preserves credentials and reports a timeout',async()=>{
 const saved=global.fetch,base=process.env.NEXT_PUBLIC_API_BASE_URL;process.env.NEXT_PUBLIC_API_BASE_URL='/api';
 try{
  const api=client();let request;
  global.fetch=async(url,options)=>{request={url,...options};throw new DOMException('timed out','TimeoutError');};
  await assert.rejects(api.api('/auth/login','POST',{email:'fixture@example.com'},true,15000),/phản hồi quá lâu/);
  assert.equal(request.url,'/api/auth/login');assert.equal(request.credentials,'include');assert.ok(request.signal instanceof AbortSignal);
 }finally{global.fetch=saved;if(base===undefined)delete process.env.NEXT_PUBLIC_API_BASE_URL;else process.env.NEXT_PUBLIC_API_BASE_URL=base;}
});
test('failed refresh releases its pending state so a later session can recover',async()=>{
 const saved=global.fetch;try{
  const api=client();let count=0;
  global.fetch=async(_url,options)=>{count++;assert.ok(options.signal instanceof AbortSignal);if(count===1)throw new DOMException('timed out','TimeoutError');return {ok:true,json:async()=>({access_token:'test-only'})};};
  assert.equal(await api.refreshSession(),false);assert.equal(await api.refreshSession(),true);assert.equal(count,2);
 }finally{global.fetch=saved;}
});
