const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
function app(){const c=vm.createContext({console,setTimeout,clearTimeout,AbortController,Date,localStorage:{getItem:()=>null},document:{readyState:'loading',addEventListener(){},querySelectorAll:()=>[]}});vm.runInContext(fs.readFileSync('app.js','utf8'),c);return {c,run:s=>vm.runInContext(s,c)};}
test('old reporter estimates render separately without populating the current estimate',()=>{
 const a=app();a.c.entry={ticker:'BAC',averageBuy:null,historicalSegments:[{kind:'separate_reporter_reference',notCombinedWithCurrent:true,reporterCIK:'1173334',firstQuarter:'2011 Q1',lastQuarter:'2011 Q4',averageBuy:10,averageSell:11,quarters:[{quarter:'2011 Q1',action:'observed',buy:10}],filingSources:{'2011 Q1':'https://www.sec.gov/Archives/edgar/data/1173334/test.txt'}}]};
 const html=a.run('historicalSegmentsHTML(entry)');assert.match(html,/1173334/);assert.match(html,/不与当前成本/);assert.match(html,/首次披露参考/);assert.match(html,/10.00/);assert.equal(a.c.entry.averageBuy,null);
 a.c.entry.historicalSegments[0].notCombinedWithCurrent=false;assert.equal(a.run('historicalSegmentsHTML(entry)'),'');
});
test('segment labels and source links remain escaped and safe',()=>{
 const a=app();a.c.entry={ticker:'BAC',historicalSegments:[{kind:'separate_reporter_reference',notCombinedWithCurrent:true,reporterCIK:'<img>',firstQuarter:'<script>',lastQuarter:'x',quarters:[],filingSources:{x:'javascript:alert(1)'}}]};
 const html=a.run('historicalSegmentsHTML(entry)');assert.doesNotMatch(html,/<img>|<script>|javascript:/);assert.match(html,/&lt;img&gt;/);
});
