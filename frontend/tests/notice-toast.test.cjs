const test=require('node:test');const assert=require('node:assert/strict');const fs=require('node:fs');const path=require('node:path');const Module=require('node:module');
const ts=require('typescript');const React=require('react');const {renderToStaticMarkup}=require('react-dom/server');
const filename=path.resolve(__dirname,'../components/notice-toast.tsx');const mod=new Module(filename,module);mod.filename=filename;mod.paths=Module._nodeModulePaths(path.dirname(filename));mod._compile(ts.transpileModule(fs.readFileSync(filename,'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,jsx:ts.JsxEmit.ReactJSX}}).outputText,filename);
test('toast exposes the actual period rejection and a dismiss control',()=>{
 const message='Không thể ghi kỳ 09/2026: chỉ số 2334 lớn hơn kỳ 10/2026 (2222).';
 const html=renderToStaticMarkup(React.createElement(mod.exports.NoticeToast,{message,onClose(){}}));
 assert.match(html,/role="status"/);assert.match(html,/09\/2026/);assert.match(html,/2334/);assert.match(html,/10\/2026/);assert.match(html,/2222/);assert.match(html,/Đóng thông báo/);
});
test('no empty toast is shown',()=>assert.equal(renderToStaticMarkup(React.createElement(mod.exports.NoticeToast,{message:'',onClose(){}})),''));
