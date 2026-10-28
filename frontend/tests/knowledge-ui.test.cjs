const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const Module=require('node:module');
const ts=require('typescript');
const React=require('react');
const {renderToStaticMarkup}=require('react-dom/server');
const filename=path.resolve(__dirname,'../components/chat-answer.tsx');
const compiled=ts.transpileModule(fs.readFileSync(filename,'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,jsx:ts.JsxEmit.ReactJSX,esModuleInterop:true}}).outputText;
const loaded=new Module(filename,module);loaded.filename=filename;loaded.paths=Module._nodeModulePaths(path.dirname(filename));loaded._compile(compiled,filename);
const {ChatAnswer}=loaded.exports;
test('RAG citations render as source links with effective date, never as meter readings',()=>{
 const html=renderToStaticMarkup(React.createElement(ChatAnswer,{answer:{message:'Giải thích theo tài liệu. [1]',sources:[{type:'knowledge',index:1,title:'EVN hướng dẫn',url:'https://www.evn.com.vn/a',effective_from:'2026-01-01'}]}}));
 assert.match(html,/href="https:\/\/www.evn.com.vn\/a"/);
 assert.match(html,/Hiệu lực 2026-01-01/);
 assert.doesNotMatch(html,/⚡ Chỉ số/);
});
test('RAG freshness warning is understandable without exposing internal codes',()=>{
 const html=renderToStaticMarkup(React.createElement(ChatAnswer,{answer:{message:'Chưa đủ căn cứ xác minh giá.',metadata:{warnings:['PRICE_SOURCE_STALE']}}}));
 assert.match(html,/chưa được kiểm tra/);
 assert.doesNotMatch(html,/PRICE_SOURCE_STALE/);
});
