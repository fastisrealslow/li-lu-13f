const {test}=require('node:test');const assert=require('node:assert/strict');const vm=require('node:vm');const fs=require('node:fs');const path=require('node:path');
const root=path.join(__dirname,'..');
function app(){const nodes=new Map(),tables={};let removed=0;
 const node=id=>{if(!nodes.has(id))nodes.set(id,{id,innerHTML:'',style:{},hidden:false,parentElement:{style:{}},prepend(el){nodes.set(el.id,el);},remove(){removed++;}});return nodes.get(id);};
 const document={getElementById:node,querySelector:s=>tables[s]||(tables[s]=node(s)),createElement:()=>({id:'',className:'',innerHTML:'',style:{}})};const window={};vm.runInNewContext(fs.readFileSync(path.join(root,'public_portfolio.js'),'utf8'),{window,document,URL});return {render:window.PublicPortfolio.render,node,get removed(){return removed;}};}
test('venture projects display associations and actual filing dates without fabricated position values',()=>{
 const a=app(),data=JSON.parse(fs.readFileSync(path.join(root,'wolfe.json'))),config={cik:'1592843'},state={data,lang:'zh',config};
 for(const section of ['summary','holdings','changes','history','timeline','insights'])assert.equal(a.render(section,state),true);
 assert.match(a.node('publicProjects').innerHTML,/官方人物页/);assert.doesNotMatch(a.node('publicProjects').innerHTML,/US\$|历史参考成本|申报占比/);
 assert.match(a.node('publicDisclosures').innerHTML,/2023-02-14/);assert.match(a.node('historyInsight').innerHTML,/不绘制虚构/);assert.ok(a.removed>0);
 assert.equal(a.render('holdings',{data:{meta:{},current:{holdings:[]}},lang:'zh',config}),false);assert.equal(a.node('publicProjects').hidden,true);
});
test('publisher text and company links stay escaped and unsafe link schemes stay inert',()=>{
 const a=app(),data={meta:{portfolioMode:'public_projects'},publicProjects:[{name:'<img src=x onerror=alert(1)>',url:'javascript:alert(1)',sourceUrl:'https://luxcapital.com/'}]};
 a.render('holdings',{data,lang:'en',config:{}});const html=a.node('publicProjects').innerHTML;assert.match(html,/&lt;img/);assert.doesNotMatch(html,/<img|href="javascript:/);
});
