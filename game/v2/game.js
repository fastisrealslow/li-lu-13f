/* 格罗茨的试炼 · a decision notebook with persistent, honest feedback. */
(function() {
  'use strict';
  const M = window.TrialsModel;
  const app = document.getElementById('app');
  const KEY = 'munger-trials-notebook-v3';
  const chapters = [
    {name:'先选对战场', lens:'化繁为简', intro:'你只有 200 万美元。先确定企业靠什么持续创造价值，再讨论包装和广告。', takeaway:'产品、品牌与铺货要构成同一条链：愿意喝，记得你，而且买得到。',
      questions:[
        ['q1','先向格罗茨解释：什么样的需求有机会支持一个世界级企业？',[
          ['高价格、低频率的收藏饮品','价格高不能代替需求规模。还要回答多少人会持续购买，复购靠什么。'],
          ['可反复购买、容易负担的日常饮品','抓住高频需求只是起点；再用品牌和渠道回答为什么买你的产品。',true],
          ['只在一次热点活动里走红的饮品','关注可能转化为一次销量，却不能自动成为长期习惯。']]],
        ['q2','配方已经有人模仿。下一笔预算应该优先解决什么？',[
          ['把所有钱花在更复杂的瓶盖上','局部设计可以改善体验，但还没有解决顾客如何识别你与模仿者的问题。'],
          ['停止铺货，等到无人能模仿配方','等待完美壁垒会让渠道和习惯留给别人。应同时建设识别度与可得性。'],
          ['保护品牌识别，并保持稳定的产品体验','法律保护、识别度和体验一致性共同积累信任；任何一项都不能独自保证成功。',true]]],
        ['q3','第一座城市的复购不错，但很多商店经常断货。你会怎么扩张？',[
          ['先修好补货和装瓶协作，再按区域复制','品牌承诺要由交付兑现。先形成可复制的供应模式，扩张才不会不断放大断货。',true],
          ['全国投广告，让知名度领先供应','看见广告却买不到，营销预算难以转化为重复购买。'],
          ['只提高价格，不处理断货','提高价格无法解释渠道瓶颈，也可能压缩日常消费场景。']]]]},
    {name:'提前看见失败',lens:'逆向思维',intro:'董事会只想听增长故事。你的任务是先指出三处会使增长链条断裂的地方。',takeaway:'逆向思考要落到可执行的防线：监测体验、保护识别、测试改变，而不是只写“注意风险”。',
      questions:[
        ['q4','新配方在一次盲测里得分更高。应该立即替换所有老配方吗？',[
          ['应该，单次盲测就是全部消费体验','盲测刻意拿掉品牌和使用情境，无法测量顾客失去熟悉产品时的反应。'],
          ['保留原款，小范围试验并观察真实复购','把试饮偏好与实际购买分开看，给顾客选择，也保留可撤回的路径。',true],
          ['从此不准尝试任何新产品','避免一次冒进不等于拒绝实验。关键在于改变的范围、证据和可逆性。']]],
        ['q5','广告转化很好，但连续喝第二份的人明显减少。先查什么？',[
          ['继续加广告，总量增长就够了','增长掩盖复购下降时，获客投入可能只是持续填补流失。'],
          ['把顾客归为不忠诚，不调整产品','责怪消费者不能解释行为。应把问题拆成体验、价格和使用场景。'],
          ['查口感负担、容量与真实饮用体验','先找阻碍重复消费的具体因素；观察第二次购买，比只问第一次好不好喝更有帮助。',true]]],
        ['q6','增长很快，有人提议不断涨价直到顾客抱怨。你如何回应？',[
          ['评估可负担性和复购，让价值感支持价格','短期每份利润与长期销量之间存在取舍。定价权来自持续提供价值，不能只靠测试忍耐。',true],
          ['能提多高就多高，需求永远不变','把需求假设成不随价格变化，会遗漏替代品与消费频率的影响。'],
          ['价格永远不动，不管成本变化','僵硬定价同样可能破坏利润；要让价格、成本、体验一起接受检验。']]]]},
    {name:'让数字说话',lens:'数学思维',intro:'把“全世界都爱喝”的故事拆成年份额、单位利润和估值。完成三次实验，观察哪个假设使结论改变。',takeaway:'算式能检验假设是否相容，却不能证明假设一定实现。先分清销量、利润和估值。'},
    {name:'拆开消费心理',lens:'跨学科思考',intro:'同一次购买可以包含多种原因。以下题目只判断情境里最直接的机制，选完再看它与其他机制怎样连接。',takeaway:'即时体验支持复购，联想支持识别，他人的行为影响选择。三者可能叠加，也可能互相抵消。',
      questions:[
        ['q7','跑完步喝到一口冰凉饮料，满足感促使你下次再买。最直接是什么机制？',[
          ['直接奖励强化重复行为','行为之后得到满足，是这个情境的主要机制。这里不需要假定广告已经起作用。',true],
          ['广告建立的情感联想','情感联想可以存在，但题目给出的直接证据是喝下后的体验。'],
          ['别人都在喝带来的社会认同','题目没有提到别人的选择，不能凭空补这个原因。']]],
        ['q8','一段广告反复把饮料与团聚画面放在一起。后来看到瓶子就想起节日。最直接是什么机制？',[
          ['喝下之后的即时奖励','这里讨论的是看到瓶子时的联想，尚未发生饮用后的奖励。'],
          ['通过反复配对建立联想','产品符号与已有情感反复配对，逐渐形成联系。这是联想层的作用。',true],
          ['朋友实际使用带来的证明','广告里的情境不等同于身边人的实际选择。']]],
        ['q9','在陌生餐馆里，你没有试喝，先点了周围大多数人正在喝的那款。最直接是什么机制？',[
          ['已经体验到好喝','尚未试喝，体验不能解释这一次选择。'],
          ['包装与节日配对','题目没有提供这种联想；应从观察到的他人选择寻找原因。'],
          ['把他人的选择作为线索','信息不足时，人会借助他人行为判断。它可以帮助选择，也可能传播错误判断。',true]]],
        ['q10','广告让人很喜欢，邻桌也都在喝，但你家附近长期买不到。哪条链断了？',[
          ['可得性：愿意买却无法完成购买','心理机制要通过真实体验继续强化。缺少渠道，再强的意愿也不等于已经发生的复购。',true],
          ['只要加强联想就可以忽略供应','增加意愿不能制造现货，缺货需要供应端的行动。'],
          ['社会认同证明渠道已经充足','被看见与买得到是不同证据。别让一个信号替代另一个问题。']]]]},
    {name:'把优势连起来',lens:'协同与激励',intro:'现在你要和装瓶商合作。合同既要让伙伴愿意投入，也要允许未来面对变化。',takeaway:'好产品、品牌、渠道和合理的合作激励互相支持，才有机会产生超过各部分的整体效果。',
      questions:[
        ['q11','装瓶商愿意出资扩张，但要求永久锁定采购价格。你会如何设计协议？',[
          ['永久锁价，未来成本上涨再说','短期换来了投入，长期却可能无法分担成本变化。先把时间跨度和调整机制写清。'],
          ['明确质量、投入义务和价格调整规则','伙伴要有合理回报，你也要保留面对成本变化的机制。可续期与可调整条款比一句“我们拥有定价权”更具体。',true],
          ['随时单方改价，完全不给伙伴保障','伙伴的设备投入需要可预期回报。单方面保留所有权力可能让渠道投资停止。']]],
        ['q12','竞争者降价抢渠道。预算有限，哪种反应更完整？',[
          ['只加广告，不问门店有没有货','品牌传播解决不了每个门店的供应与合作利益。'],
          ['全面削弱质量以追平低价','若体验受损，短期价格优势可能破坏复购与品牌。'],
          ['检查顾客体验、门店供货与伙伴利润一起是否成立','先定位竞争发生在哪一环，再安排投入。协调各环节，避免一种措施破坏另一种优势。',true]]],
        ['q13','董事会认为品牌、渠道和规模都很好，所以估值必然上涨。你的最后一句是什么？',[
          ['逐项核验假设，并看不利情境下利润还剩多少','优势可以相互强化，但结果仍取决于价格、成本、竞争和投入；再好的叙事也需要证据更新。',true],
          ['把所有增长因素直接相加就是收益率','增长因素可能重叠，也有不同单位，不能直接相加。'],
          ['历史故事已说明未来不可能失败','案例帮助提出问题；它无法把未来的不确定性消掉。']]]]}
  ];
  const questions = chapters.flatMap(c => c.questions || []);
  const qmap = Object.fromEntries(questions.map(q=>[q[0],q]));
  function fresh() { return {version:3, screen:'intro', chapter:0, answers:{}, params:{...M.DEFAULTS}, missions:[], alloc:{product:3,brand:3,channel:4}, submitted:false}; }
  let storageOK = true;
  function restore() {
    let raw;
    try { raw=JSON.parse(localStorage.getItem(KEY)); } catch(e) { storageOK=false; }
    const s=fresh();
    if (!raw || raw.version !== 3) return s;
    if (raw.answers && typeof raw.answers === 'object') for (const [id,n] of Object.entries(raw.answers)) {
      if (qmap[id] && Number.isInteger(n) && n >= 0 && n < qmap[id][2].length) s.answers[id]=n;
    }
    s.params=M.parameters(raw.params);
    s.missions=[];
    if (Array.isArray(raw.missions)) for (let i=0;i<3;i++) { if (!raw.missions.includes(i)) break; s.missions.push(i); }
    for (const k of Object.keys(s.alloc)) if (Number.isInteger(raw.alloc && raw.alloc[k]) && raw.alloc[k]>=0 && raw.alloc[k]<=10) s.alloc[k]=raw.alloc[k];
    s.submitted=raw.submitted === true && M.simulate(s.alloc).valid && complete(s,4);
    const unlocked=firstIncomplete(s);
    s.chapter=Number.isInteger(raw.chapter) ? Math.max(0,Math.min(4,raw.chapter,unlocked)) : 0;
    if (['intro','letter','chapter'].includes(raw.screen)) s.screen=raw.screen;
    if (['board','ending'].includes(raw.screen) && unlocked===5) s.screen=raw.screen==='ending' && !s.submitted ? 'board' : raw.screen;
    return s;
  }
  function complete(s,i) { return i===2 ? s.missions.length===3 : chapters[i].questions.every(q=>Object.hasOwn(s.answers,q[0])); }
  function firstIncomplete(s) { for (let i=0;i<5;i++) if(!complete(s,i)) return i; return 5; }
  let state=restore();
  function save() { try { localStorage.setItem(KEY,JSON.stringify(state)); } catch(e) { storageOK=false; } }
  const node=(tag,cls,text) => {const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
  function button(text,fn,cls='button') {const b=node('button',cls,text);b.type='button';b.onclick=fn;return b;}
  function link(text,url,cls='text-link') {const a=node('a',cls,text);a.href=url;return a;}
  function section(title,body,cls='card') {const c=node('section',cls);c.append(node('h2','',title));if(body)c.append(node('p','',body));return c;}
  function change(screen,chapter=state.chapter) {state.screen=screen;state.chapter=chapter;save();render();window.scrollTo({top:0});const h=app.querySelector('h1');if(h){h.tabIndex=-1;h.focus({preventScroll:true});}}
  function status(text,good=false) {const e=node('div','feedback'+(good?' success':''),text);e.setAttribute('role','status');return e;}
  function score(i) {const list=chapters[i].questions || [];return list.filter(q=>q[2][state.answers[q[0]]] && q[2][state.answers[q[0]]][2]).length;}
  function counts() {return Object.keys(state.answers).length+state.missions.length;}
  function render() {
    app.replaceChildren();
    const top=node('header','game-top');const brand=link('思维试炼 / THE MUNGER TRIALS','index.html?v=5','brand');top.append(brand,link('阅读演讲解读 ↗','article.html?v=5'));app.append(top);
    const shell=node('div','shell');const rail=node('aside','chapter-rail');rail.setAttribute('aria-label','章节导航');
    rail.append(node('p','eyebrow','1884 → 2034'),node('h2','','一份商业推演笔记'),node('p','rail-summary','先判断，再计算。用五个思维透镜检验同一个商业故事。'));
    const nav=node('nav','chapter-list');const unlocked=firstIncomplete(state);
    chapters.forEach((c,i)=>{const b=button((complete(state,i)?'✓':String(i+1).padStart(2,'0'))+'  '+c.name,()=>change('chapter',i),'chapter-button'+(state.screen==='chapter'&&state.chapter===i?' active':''));b.disabled=i>unlocked;b.setAttribute('aria-current',state.screen==='chapter'&&state.chapter===i?'step':'false');nav.append(b);});
    const final=button('06  董事会终局',()=>change('board'),'chapter-button'+(['board','ending'].includes(state.screen)?' active':''));final.disabled=unlocked<5;nav.append(final);rail.append(nav);
    const progress=node('div','notebook-progress');progress.append(node('p','',counts()+' / 16 项推演完成'));const meter=node('progress');meter.max=16;meter.value=counts();meter.setAttribute('aria-label','推演完成进度');progress.append(meter);rail.append(progress);
    rail.append(node('p','save-note',storageOK?'进度自动保存在本机浏览器。':'当前浏览器无法保存进度，仍可完成本次游戏。'));
    const resetBox=node('div','reset-box');resetBox.append(button('重新开始',()=>{resetBox.replaceChildren(node('p','','清除本机这一次的回答与进度？'),button('确认重新开始',()=>{state=fresh();change('intro');}),button('保留进度',render,'button subtle'));},'text-button'));rail.append(resetBox);
    shell.append(rail);const main=node('main','game-main');main.id='main';shell.append(main);app.append(shell);
    if (state.screen==='intro') intro(main);
    if (state.screen==='letter') letter(main);
    if (state.screen==='chapter') chapter(main);
    if (state.screen==='board') board(main);
    if (state.screen==='ending') ending(main);
    const foot=node('footer','game-footer','基于 1996 年演讲的原创学习练习 · 题目、压力测试和资源分配为游戏设计');foot.append(link('资料与数字说明','article.html?v=5#sources'));app.append(foot);
  }
  function heading(main,kicker,title,desc) {main.append(node('p','eyebrow',kicker),node('h1','',title),node('p','lead',desc));}
  function actions(main,items) {const bar=node('div','actions');items.forEach(e=>bar.append(e));main.append(bar);}
  function intro(main) {
    heading(main,'商业不是一道单选题','格罗茨的试炼：\n2 万亿的答案','回到 1884 年。如果给你 200 万美元，你能提出一条通往 2034 年、价值 2 万亿美元的商业路径吗？');
    const stats=node('div','hero-stats');[['5','思维透镜'],['16','决策与数字实验'],['15–25 分钟','建议游戏时长']].forEach(([n,l])=>{const c=node('div');c.append(node('b','',n),node('span','',l));stats.append(c);});main.append(stats);
    main.append(section('从“选答案”到“说清楚为什么”','你的每个选择都会留下理由。第三关可以改变参数，第六关需要分配有限资源。最后的复盘会指出你理解了什么，以及哪些假设仍经不起压力。'));
    actions(main,[button(counts()?'继续上次推演':'打开格罗茨的委任书',()=>change(counts()?(firstIncomplete(state)<5?'chapter':state.submitted?'ending':'board'):'letter',Math.min(4,firstIncomplete(state)))),link('先读完整解读','article.html?v=5','button subtle')]);
    main.append(node('p','small','电脑可用 Tab / Enter 操作，答题时也可按 1、2、3 选择。手机直接点选，算账滑块支持拖动与加减按钮。'));
  }
  function letter(main) {
    heading(main,'序章 · 这是一个虚构的委任','你的资金有限，时间很长','你需要把一个商业目标变成可以解释、可以验证、可以修正的计划。');
    main.append(section('200 万美元换取什么？','在芒格的设定里，格罗茨投入全部 200 万美元，换取公司 50% 股权，归慈善基金会持有；另外 50% 归能提出可信计划的创业者。业务限定为非酒精饮料，并需在过程中持续分配大量利润。目标是 2034 年整家公司价值 2 万亿美元，即基金会那一半价值 1 万亿美元。资金并不是一半捐赠、一半投资。'));
    const lenses=node('div','lens-grid');chapters.forEach((c,i)=>{const x=section(String(i+1).padStart(2,'0')+' / '+c.lens,c.takeaway);lenses.append(x);});main.append(lenses);
    main.append(node('p','small','这里允许使用跨学科基础知识，但不能靠知道后来历史来代替推理。后面的历史对照属于复盘材料。'));
    actions(main,[button('开始第一关',()=>change('chapter',0)),button('回到开场',()=>change('intro'),'button subtle')]);
  }
  function chapter(main) {
    const i=state.chapter,c=chapters[i];heading(main,'试炼 '+String(i+1).padStart(2,'0')+' / '+c.lens,c.name,c.intro);
    if(i===2) calculator(main);else {
      const list=node('div','question-list');c.questions.forEach((q,idx)=>list.append(question(q,idx)));main.append(list);
    }
    main.append(section('这一关，带走什么？',c.takeaway,'takeaway'));
    const next=button(i===4?'进入董事会终局':'继续下一关',()=>change(i===4?'board':'chapter',Math.min(4,i+1)));next.disabled=!complete(state,i);
    actions(main,[next,button(i===0?'回到委任书':'上一关',()=>change(i===0?'letter':'chapter',Math.max(0,i-1)),'button subtle')]);
    if(!complete(state,i))main.append(node('p','small','完成本关全部选择或实验后继续。答错也能继续，复盘会保留第一次判断。'));
  }
  function question(q,idx) {
    const [id,title,options]=q,card=section((idx+1)+'. '+title);card.id=id;card.classList.add('question');const answered=Object.hasOwn(state.answers,id);if(!answered)card.dataset.unanswered='true';
    const choices=node('div','choice-list');choices.setAttribute('role','group');choices.setAttribute('aria-label',title);
    options.forEach((op,n)=>{const b=button((n+1)+'. '+op[0],()=>{state.answers[id]=n;save();const newer=question(q,idx);card.replaceWith(newer);const focus=newer.querySelector('.feedback');focus.tabIndex=-1;focus.focus({preventScroll:true});refreshChrome();},'choice'+(answered&&state.answers[id]===n?(op[2]?' chosen good':' chosen reconsider'):''));b.disabled=answered;choices.append(b);});card.append(choices);
    if(answered){const op=options[state.answers[id]],correct=options.find(o=>o[2]);card.append(status((op[2]?'判断成立。':'值得再想一步。')+op[1],Boolean(op[2])));if(!op[2])card.append(node('p','small','较完整的方案：'+correct[0]+'。'+correct[1]));}
    return card;
  }
  // Updating only the rail/actions retains focus, scroll and the other unanswered cards.
  function refreshChrome() {
    const rail=app.querySelector('.chapter-rail');rail.querySelector('progress').value=counts();rail.querySelector('.notebook-progress p').textContent=counts()+' / 16 项推演完成';
    if(!storageOK)rail.querySelector('.save-note').textContent='当前浏览器无法保存进度，仍可完成本次游戏。';
    const unlocked=firstIncomplete(state);rail.querySelectorAll('.chapter-list .chapter-button').forEach((b,i)=>{b.disabled=i>unlocked;if(i<5)b.textContent=(complete(state,i)?'✓':String(i+1).padStart(2,'0'))+'  '+chapters[i].name;});
    const next=app.querySelector('.game-main > .actions button');if(next && state.screen==='chapter')next.disabled=!complete(state,state.chapter);
  }
  function controls(container,key,label,value,min,max,step,onChange,suffix='') {
    const row=node('div','parameter');const lab=node('label','',label);const id='param-'+key;lab.htmlFor=id;const output=node('output','',value+suffix);output.htmlFor=id;const range=node('input');range.type='range';range.id=id;range.min=min;range.max=max;range.step=step;range.value=value;
    const field=node('div','range-controls');const adjust=(delta)=>{range.value=Number(range.value)+delta;range.dispatchEvent(new Event('input'));};const minus=button('−',()=>adjust(-step),'step-button');minus.setAttribute('aria-label',label+'减少');const plus=button('+',()=>adjust(step),'step-button');plus.setAttribute('aria-label',label+'增加');
    range.oninput=()=>{output.textContent=range.value+suffix;onChange(Number(range.value));};row.append(lab,output);field.append(minus,range,plus);row.append(field);container.append(row);
  }
  const yi=n=>(n/1e8).toLocaleString('zh-CN',{maximumFractionDigits:1});
  const trillion=n=>(n/1e12).toLocaleString('zh-CN',{maximumFractionDigits:4});
  function metrics(calc) {const grid=node('div','metric-grid');[['年销量',trillion(calc.servings)+' 万亿份'],['年利润',yi(calc.profit)+' 亿美元'],['对应估值',trillion(calc.value)+' 万亿美元']].forEach(([l,v])=>{const e=node('div');e.append(node('span','',l),node('b','',v));grid.append(e);});return grid;}
  function calculator(main) {
    const card=section('一个算式，四个可以改变的假设','固定底数：演讲假设的 80 亿消费者 × 每天 8 份（每份约 237 毫升）× 365 天。这里只是还原当时的教学假设，液体摄入量不是饮水建议。');
    const workspace=node('div','calculator-grid'),inputs=node('div');
    const defs=[['market','饮水总量中，行业饮料占比','%'],['share','公司在这个饮料市场的份额','%'],['margin','每份净利润',' 美分'],['multiple','利润估值倍数（游戏新增）',' 倍']];
    let result=node('div','calculation');
    defs.forEach(([key,label,suffix])=>{const [min,max,step]=M.LIMITS[key];controls(inputs,key,label,state.params[key],min,max,step,value=>{state.params[key]=value;save();draw();},suffix);});workspace.append(inputs,result);card.append(workspace);main.append(card);
    function draw() {
      const r=M.calculate(state.params);result.replaceChildren(metrics(r));
      result.append(node('p','formula','年销量 = 80 亿 × 8 × 365 × '+state.params.market+'% × '+state.params.share+'%\n年利润 = 年销量 × '+state.params.margin+' ÷ 100 美元\n估值 = 年利润 × '+state.params.multiple));
      result.append(node('p','small',r.neededMultiple===null?'利润为零时，不能用利润倍数推导目标估值。':'要达到 2 万亿美元，当前利润需要约 '+r.neededMultiple.toFixed(2)+' 倍估值。达到金额只说明算术成立。'));
      const mission=main.querySelector('.mission-card');if(mission){const idx=state.missions.length;const b=mission.querySelector('.verify-mission');if(b)b.disabled=idx>=3;}
    }
    draw();
    const experiments=section('三次实验 · 不只寻找最大数值',null,'card mission-card');const content=node('div');experiments.append(content);main.append(experiments);
    function drawMission() {
      content.replaceChildren();state.missions.forEach(i=>content.append(status('实验 '+(i+1)+' ✓ '+M.MISSIONS[i].feedback,true)));
      const idx=state.missions.length;if(idx===3){content.append(node('p','small','三次实验完成。你仍可自由改变参数，比较其他情境。'));return;}
      const mission=M.MISSIONS[idx];content.append(node('h3','',String(idx+1)+'. '+mission.title),node('p','',mission.detail));
      const feedback=node('div');content.append(button('验证当前实验',()=>{if(mission.pass(state.params)){state.missions.push(idx);save();drawMission();refreshChrome();}else feedback.replaceChildren(status('参数还没有满足本次实验。按上方条件逐项核对，两项份额不是同一个百分比。'));},'button verify-mission'),feedback);
    }
    drawMission();
    const stress=section('压力测试 · 用当前参数再问三个问题');const stressResults=node('div','stress-grid');stress.append(stressResults);
    const stressBtn=button('比较不利情境',()=>{const r=M.calculate(state.params);stressResults.replaceChildren();[['每份净利减半',r.marginHalvedValue],['公司市场份额减半',r.shareHalvedValue],['估值改为 12 倍',r.lowerMultipleValue]].forEach(([title,v])=>stressResults.append(section(title,trillion(v)+' 万亿美元')));stressResults.append(node('p','small','每一项都只改变一个变量，其他变量保持当前值。这些情境不是发生概率预测。'));});stress.append(stressBtn);main.append(stress);
    // Recalculate visible stress results whenever inputs change, so examples never go stale.
    inputs.addEventListener('input',()=>{if(stressResults.children.length)stressBtn.click();});
  }
  function board(main) {
    heading(main,'终局 · 10 枚筹码，三个相互依赖的环节','提交你的经营方案','把有限资源分给产品体验、品牌识别与渠道供给。不能只把一个数推到最大：看看优势能否连成一条链。');
    const card=section('资源分配','10 枚筹码必须全部分完。此处的映射只是用于比较取舍的游戏规则。');const input=node('div');const results=node('div','board-results');let submit;
    [['product','产品与成本'],['brand','品牌与识别'],['channel','渠道与供给']].forEach(([key,label])=>controls(input,'alloc-'+key,label,state.alloc[key],0,10,1,value=>{state.alloc[key]=value;state.submitted=false;save();draw();},' 枚'));card.append(input,results);
    const rules=node('details','rules');rules.append(node('summary','','展开全部模型规则'),node('p','','每份净利 = 1 + 产品筹码 × 0.6 美分；公司份额 = 10% + 品牌筹码 × 8 个百分点（最多 80%）；行业饮料占比 = 10% + 渠道筹码 × 5 个百分点（最多 40%）；估值固定 18 倍。使用第三关的销量和利润算式。三项各投入至少 2 枚，记作“协作完整”。这些数值为游戏设定，未做经验校准。'));card.append(rules);main.append(card);
    submit=button('提交方案并看复盘',()=>{const r=M.simulate(state.alloc);if(!r.valid)return;state.submitted=true;change('ending');});actions(main,[submit,button('返回第五关',()=>change('chapter',4),'button subtle')]);
    function draw(){const r=M.simulate(state.alloc),total=r.product+r.brand+r.channel;results.replaceChildren(node('p','budget'+(r.valid?' valid':''),'已分配 '+total+' / 10 枚 · '+(total>10?'超出预算 '+(total-10)+' 枚':total<10?'还有 '+(10-total)+' 枚待分配':'预算平衡')));if(r.valid){results.append(metrics(r),node('p','small',r.balanced?'三个环节都有基础投入。继续观察利润与份额的取舍。':'存在投入不足的环节：'+{product:'产品',brand:'品牌',channel:'渠道'}[r.weakest]+'。金额较大也可能伴随经营短板。'));}submit.disabled=!r.valid;}
    draw();
  }
  function ending(main) {
    const correct=questions.filter(q=>q[2][state.answers[q[0]]] && q[2][state.answers[q[0]]][2]).length;const r=M.simulate(state.alloc);
    heading(main,'复盘 · 把判断还给证据','这份方案，哪些地方站得住？','第一次判断成立 '+correct+' / 13 题，三次数学实验已完成。这里评估的是推理完整性，不能据此推断现实投资收益。');
    main.append(section(r.balanced?'你的方案覆盖了三个环节':'你的方案仍有一个薄弱环节',r.balanced?'资源同时支持体验、识别与交付。下一步需要验证各环节是否真的影响复购、份额与成本。':'优先复查'+{product:'产品体验和单位利润',brand:'识别度和客户选择',channel:'供货覆盖和实际购买'}[r.weakest]+'：模型里的高金额并不能补上这一段经营证据。'));
    main.append(metrics(r));main.append(node('p','small','按你的资源方案计算；数字由终局公开规则产生，非可口可乐实际经营数据。'));
    const review=node('div','review-grid');chapters.forEach((c,i)=>{const n=i===2?'3 / 3 次实验':score(i)+' / '+c.questions.length+' 次判断';const item=section(c.lens+' · '+n,c.takeaway);const misses=(c.questions||[]).filter(q=>!q[2][state.answers[q[0]]][2]);if(misses.length)item.append(node('p','small','建议重读：'+misses.map(q=>q[1]).join('；')));item.append(button('查看本关笔记',()=>change('chapter',i),'text-button'));review.append(item);});main.append(review);
    const history=section('真实历史 · 与虚构设定分开看','1884 年和 200 万美元是演讲的思想实验，不是可口可乐真实创办记录。可口可乐的官方历史记载创始饮料诞生于 1886 年、1899 年出售装瓶权；1985 年的新可乐在消费者抗议后，于 79 天后恢复原配方供应。');history.append(link('查看原始资料和详细解读','article.html?v=5#history'));main.append(history);
    actions(main,[button('重新调整资源方案',()=>change('board')),link('读解读：从故事到证据','article.html?v=5','button subtle')]);
  }
  document.addEventListener('keydown',e=>{
    if(e.defaultPrevented||e.altKey||e.ctrlKey||e.metaKey||!['1','2','3'].includes(e.key)||state.screen!=='chapter'||state.chapter===2)return;
    if(e.target && /INPUT|TEXTAREA|SELECT/.test(e.target.tagName))return;
    const focused=e.target.closest && e.target.closest('.question');
    const q=focused && focused.dataset.unanswered ? focused : app.querySelector('.question[data-unanswered]');
    if(q){const b=q.querySelectorAll('.choice')[Number(e.key)-1];if(b&&!b.disabled){e.preventDefault();b.click();}}
  });
  render();
})();
