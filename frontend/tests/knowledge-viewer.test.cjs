const test=require('node:test');const assert=require('node:assert/strict');
const fs=require('node:fs');const path=require('node:path');const Module=require('node:module');
const ts=require('typescript');const React=require('react');const {renderToStaticMarkup}=require('react-dom/server');
function component(){const filename=path.resolve(__dirname,'../components/knowledge-document-viewer.tsx');const mod=new Module(filename,module);mod.filename=filename;mod.paths=Module._nodeModulePaths(path.dirname(filename));mod._compile(ts.transpileModule(fs.readFileSync(filename,'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,jsx:ts.JsxEmit.ReactJSX,esModuleInterop:true}}).outputText,filename);return mod.exports.KnowledgeDocumentViewer;}
test('opened document is an explicit visible reading region with close control',()=>{
 const Viewer=component();const html=renderToStaticMarkup(React.createElement(Viewer,{document:{id:'v1',title:'Nguồn thử nghiệm',content:'Nội dung thực từ database.',status:'PUBLISHED',url:'https://www.evn.com.vn/',metadata:{},readiness:{can_publish:true,missing:[]}},busy:false,onClose(){},onPublish(){},onBlock(){},onDownload(){}}));
 assert.match(html,/aria-label="Nội dung tài liệu"/);assert.match(html,/Nội dung thực từ database/);assert.match(html,/Đóng nội dung/);
});
test('scanned/empty documents explain what is missing instead of displaying a blank preview',()=>{
 const Viewer=component();const html=renderToStaticMarkup(React.createElement(Viewer,{document:{id:'v2',title:'PDF scan',content:'',status:'PENDING_REVIEW',url:'https://www.evn.com.vn/',metadata:{},readiness:{can_publish:false,missing:['READABLE_TEXT','EFFECTIVE_DATE']}},busy:false,onClose(){},onPublish(){},onBlock(){},onDownload(){}}));
 assert.match(html,/chưa có nội dung chữ/);assert.match(html,/Ngày hiệu lực/);assert.match(html,/Tải bản gốc/);
});
