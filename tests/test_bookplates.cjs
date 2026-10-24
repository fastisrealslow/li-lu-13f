const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const root=path.resolve(__dirname,'..');
function app(){
  const attrs={'data-appearance':'current'},styles={},figure={children:[],querySelector(tag){return this.children.find(e=>e.tag===tag);},replaceChildren(...items){this.children=items;}};
  const document={documentElement:{getAttribute:k=>attrs[k],setAttribute:(k,v)=>attrs[k]=v,removeAttribute:k=>delete attrs[k],style:{setProperty:(k,v)=>styles[k]=v,removeProperty:k=>delete styles[k]}},querySelector:()=>figure,createElement:tag=>({tag,attrs:{},setAttribute(k,v){this.attrs[k]=v;},getAttribute(k){return this.attrs[k];}})};
  const window={};vm.runInNewContext(fs.readFileSync(path.join(root,'investor_bookplates.js'),'utf8'),{window,document});
  return {api:window.InvestorBookplates,attrs,styles,figure};
}
test('every configured investor has a distinct original bookplate, ink and bilingual caption',()=>{
  const a=app(),people=JSON.parse(fs.readFileSync(path.join(root,'investors.json'))).investors;
  assert.deepEqual(Object.keys(a.api.designs).sort(),people.map(p=>p.id).sort());
  const arts=new Set(),inks=new Set(),labels=new Set();
  for(const p of people){
    const d=a.api.designs[p.id],svg=fs.readFileSync(path.join(root,'assets/almanac/bookplates',p.id+'.svg'),'utf8');
    assert.match(svg,/<svg/);assert.doesNotMatch(svg,/<script|\son\w+=|(?:href|src)=["'](?:https?:|data:|javascript:)/i);
    assert.ok(d.label.every(x=>typeof x==='string'&&x.trim()));arts.add(svg);inks.add(d.ink);labels.add(d.label[0]);
  }
  assert.equal(arts.size,people.length);assert.equal(inks.size,people.length);assert.equal(labels.size,people.length);
});
test('the default appearance has no hidden image downloads and an activated bookplate follows the chosen investor',()=>{
  const a=app();a.api.select('akre');assert.equal(a.figure.children.length,0);
  a.attrs['data-appearance']='almanac';a.api.refresh();
  assert.equal(a.figure.children[0].attrs.src,'assets/almanac/bookplates/akre.svg');assert.equal(a.figure.children[1].textContent,'三条腿的凳子');
  a.api.select('webb',true);assert.equal(a.attrs['data-investor'],'webb');assert.equal(a.styles['--identity-ink'],a.api.designs.webb.ink);
  assert.equal(a.figure.children[0].attrs.src,'assets/almanac/bookplates/webb.svg');assert.equal(a.figure.children[1].textContent,'Let the sunlight in');
  a.attrs['data-appearance']='current';a.api.refresh();assert.equal(a.figure.children.length,0);
});
test('unknown or prototype-shaped identities clear stale styling without creating a remote asset path',()=>{
  const a=app();a.attrs['data-appearance']='almanac';
  for(const bad of ['__proto__','constructor','../../outside','https://outside.test/']){
    a.api.select('lilu');a.api.select(bad);assert.equal(a.figure.children.length,0);assert.equal(a.attrs['data-investor'],undefined);assert.equal(a.styles['--identity-ink'],undefined);
  }
});
test('chapter inks keep small captions readable on the common paper and their own tinted paper',()=>{
  const L=h=>{const c=[1,3,5].map(i=>parseInt(h.slice(i,i+2),16)/255);return c.reduce((s,x,i)=>s+(x<=.04045?x/12.92:((x+.055)/1.055)**2.4)*[.2126,.7152,.0722][i],0);};
  for(const [id,d] of Object.entries(app().api.designs))for(const bg of ['#efe2c8',d.wash]){
    const [a,b]=[L(d.ink),L(bg)].sort((a,b)=>a-b);assert.ok((b+.05)/(a+.05)>=4.5,id);
  }
});
