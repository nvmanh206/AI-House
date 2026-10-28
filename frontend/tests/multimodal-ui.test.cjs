const assert = require('node:assert/strict');
const {test} = require('node:test');
const fs = require('node:fs');
const ts = require('typescript');
const React = require('react');
const {renderToStaticMarkup} = require('react-dom/server');
for (const ext of ['.tsx', '.ts']) require.extensions[ext] = (module, filename) => {
  const {outputText} = ts.transpileModule(fs.readFileSync(filename, 'utf8'), {compilerOptions: {module:ts.ModuleKind.CommonJS,jsx:ts.JsxEmit.ReactJSX,esModuleInterop:true},fileName:filename});
  module._compile(outputText,filename);
};
const {InvoiceResultDetails} = require('../components/invoice-result-details.tsx');
const {chatStorageKey,persistableMessages} = require('../components/chat-state.ts');
const {ChatAnswer} = require('../components/chat-answer.tsx');
test('internal evidence references do not masquerade as meter-reading citations',()=>{
  const html=renderToStaticMarkup(React.createElement(ChatAnswer,{answer:{message:'Kết quả tự nhiên.',sources:[{type:'evidence',ref:'verification:reading'}]}}));
  assert.match(html,/Kết quả tự nhiên/);
  assert.doesNotMatch(html,/⚡ Chỉ số/);
});
test('invoice fields are optional collapsed details, preserving real zero', () => {
  const html=renderToStaticMarkup(React.createElement(InvoiceResultDetails,{result:{extracted_data:{current_reading:'0',total_amount:null}, extraction:{uncertain_fields:['total_amount'],missing_fields:[]}}}));
  assert.match(html,/<details/);
  assert.doesNotMatch(html,/<details[^>]*\sopen/);
  assert.match(html,/Chỉ số mới/);
  assert.match(html,/>0</);
  assert.match(html,/Không đọc rõ/);
  assert.doesNotMatch(html,/Trùng chỉ số|ĐỐI SOÁT/);
});
test('chat persistence is household scoped and does not retain images',()=>{
  assert.notEqual(chatStorageKey('u','h1'),chatStorageKey('u','h2'));
  const messages=Array.from({length:25},()=>({role:'user',message:'test',imagePreview:'data:image/png;base64,private',image_base64:'private'}));
  const saved=persistableMessages(messages);
  assert.equal(saved.length,20);
  assert.doesNotMatch(JSON.stringify(saved),/private|imagePreview|image_base64/);
});
