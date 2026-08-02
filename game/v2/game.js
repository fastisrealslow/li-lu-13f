/* ============================================
   格罗茨的试炼：2万亿的答案 — v2 纯原生引擎
   改编自查理·芒格 1996 年演讲《关于现实思维的现实思考》
   ============================================ */
(function(){
  'use strict';

  var app = document.getElementById('app');
  var state = {
    scene: 'intro',   // intro | trial1..trial5 | ending
    seals: [],        // 已获得的印章 key 列表
    soundOn: false,
  };

  var SEAL_DEFS = [
    { key:'water',   icon:'💧' },
    { key:'reverse', icon:'🔄' },
    { key:'reflex',  icon:'🔔' },
    { key:'moat',    icon:'🏰' },
    { key:'lolla',   icon:'⚡' },
  ];

  function el(tag, cls, html){
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (html !== undefined) e.innerHTML = html;
    return e;
  }

  function haptic(){
    if (window.navigator && window.navigator.vibrate) {
      try { window.navigator.vibrate(8); } catch(e){}
    }
  }

  function goScene(name){
    state.scene = name;
    render();
    // 场景切换后回到内容区顶部
    var stage = document.querySelector('.stage');
    if (stage) stage.scrollTop = 0;
  }

  function earnSeal(key){
    if (state.seals.indexOf(key) === -1) state.seals.push(key);
  }

  /* ---------- 顶部栏 + 山景背景（除开场外常驻） ---------- */
  function renderChrome(container, chapterLabel){
    var bg = el('div','scene-bg',
      '<div class="hill hill4"></div><div class="hill hill3"></div>' +
      '<div class="hill hill2"></div><div class="hill hill1"></div><div class="sun"></div>');
    container.appendChild(bg);

    var top = el('div','topbar');
    var badge = el('div','badge', chapterLabel || '格罗茨的试炼');
    var soundBtn = el('button','sound-btn', state.soundOn ? '🔊' : '🔈');
    soundBtn.setAttribute('aria-label','toggle sound');
    soundBtn.onclick = function(){
      state.soundOn = !state.soundOn;
      soundBtn.textContent = state.soundOn ? '🔊' : '🔈';
      haptic();
    };
    top.appendChild(badge);
    top.appendChild(soundBtn);
    container.appendChild(top);
  }

  function renderProgress(container, stepIndex, total){
    var track = el('div','progress-track');
    var fill = el('div','progress-fill');
    fill.style.width = (Math.max(0,stepIndex) / total * 100) + '%';
    track.appendChild(fill);
    container.appendChild(track);
  }

  /* ============================================
     开场屏
     ============================================ */
  function renderIntro(){
    var root = el('div');
    renderChrome(root, '1884 · 亚特兰大');
    var stage = el('div','stage');

    var intro = el('div','intro-screen scene-enter');
    intro.appendChild(el('h1','intro-title','格罗茨的试炼'));
    intro.appendChild(el('div','intro-sub','源自查理·芒格 1996 年演讲'));
    intro.appendChild(el('div','intro-sub','《关于现实思维的现实思考》'));
    intro.appendChild(el('p','intro-sub2','一场穿越 150 年的思维试炼——从两百万，到两万亿。'));
    var cta = el('button','intro-cta','踏入试炼');
    cta.onclick = function(){ haptic(); goScene('letter'); };
    intro.appendChild(cta);
    stage.appendChild(intro);
    root.appendChild(stage);
    return root;
  }

  /* ============================================
     序章：信封 / 委任
     ============================================ */
  function renderLetter(){
    var root = el('div');
    renderChrome(root, '致：未来的商业天才');
    var stage = el('div','stage');
    stage.appendChild(chapterTag('序 言 · 两百万的委任'));

    var card = el('div','card scene-enter');
    card.appendChild(el('div','card-title','贰佰万美元整'));
    card.appendChild(el('div','card-quote',
      '欢迎来到 1884 年的亚特兰大。格罗兹先生愿意拿出 200 万美元，换取一个承诺：' +
      '150 年后，这家公司必须值 2 万亿——即便每年都要分红。你有十五分钟。'));
    card.appendChild(el('div','card-body',
      '你有十五分钟陈述你的方案。你会对格罗兹说什么？'));
    stage.appendChild(card);

    root.appendChild(stage);
    var nav = el('div','bottom-nav');
    var next = el('button','nav-btn primary','接受挑战');
    next.onclick = function(){ haptic(); goScene('trial1'); };
    nav.appendChild(next);
    root.appendChild(nav);
    return root;
  }

  function chapterTag(text){
    return el('div','chapter-tag', text);
  }

  /* ============================================
     试炼一：不做钢琴，做水一样的东西
     ============================================ */
  var T1_OPTIONS = [
    { key:'piano', label:'像钢琴一样精密、昂贵的奢侈品', correct:false },
    { key:'water', label:'像水一样普适、廉价、人人天天需要的东西', correct:true },
    { key:'lux',   label:'只服务少数高净值人群的稀缺品', correct:false },
  ];

  function renderTrial1(){
    var root = el('div');
    renderChrome(root, '试炼 一');
    var stage = el('div','stage');
    renderProgress(stage, 1, 5);
    stage.appendChild(chapterTag('试炼 一 · 化繁为简'));

    var card = el('div','card scene-enter');
    card.appendChild(el('div','card-title','第一个真相：没有人能靠钢琴赚到 2 万亿'));
    card.appendChild(el('div','card-quote',
      '钢琴太贵、太复杂，一个人一辈子只买一次。你需要的，是像水一样普适、廉价、能激发人性本能的东西。'));
    card.appendChild(el('div','card-body','如果目标是 2 万亿，你会选择做什么样的产品？'));
    stage.appendChild(card);

    var list = el('div','choice-list');
    var answered = false;
    T1_OPTIONS.forEach(function(opt){
      var btn = el('button','choice-btn', opt.label);
      btn.onclick = function(){
        if (answered) return;
        answered = true;
        haptic();
        Array.prototype.forEach.call(list.children, function(b){ b.disabled = true; });
        if (opt.correct) {
          btn.classList.add('correct');
          earnSeal('water');
          showTrial1Result(stage, true);
        } else {
          btn.classList.add('wrong');
          showTrial1Result(stage, false);
        }
        updateNav();
      };
      list.appendChild(btn);
    });
    stage.appendChild(list);

    var resultSlot = el('div','result-slot');
    stage.appendChild(resultSlot);

    function showTrial1Result(stageEl, correct){
      var box = el('div','result-box scene-enter',
        (correct
          ? '<b>正确。</b> 到 2034 年，全球将有约 <b>80 亿</b>饮料消费者，每人每天必须摄入约 64 盎司（8 杯）的水。'
          : '<b>再想想。</b> 卖一种平庸的饮料，永远不可能创造出价值 2 万亿的东西——但一种像水一样普适的产品可以。') +
        '<br><br>反过来想，总是反过来想——这是芒格引用的数学校训，也是商业第一原则。');
      resultSlot.appendChild(box);
    }

    root.appendChild(stage);
    var nav = el('div','bottom-nav');
    var next = el('button','nav-btn primary','下一试炼');
    next.disabled = true;
    next.onclick = function(){ haptic(); goScene('trial2'); };
    nav.appendChild(next);
    root.appendChild(nav);

    function updateNav(){ next.disabled = false; }
    return root;
  }

  /* ============================================
     试炼二：反过来想的护城河（危险牌翻转）
     ============================================ */
  var T2_CARDS = [
    { danger:'回味阻碍', safe:'清爽无碍', detail:'人体天生会用"回味"提醒你少喝——这是进化留下的保护机制。大热天，顾客要能一瓶接一瓶地喝，回味必须降到几乎为零。' },
    { danger:'商标被稀释', safe:'商标独占', detail:'哪怕只丢掉商标的一半保护，代价都极其惨重。绝不能让"胡椒可乐"之类的仿名钻了空子——如果真出现，也必须是我们自己的品牌。' },
    { danger:'树大招风', safe:'定价坦荡', detail:'成功太快，必然招来嫉妒。避免嫉妒最好的办法，就是让自己真正配得上这份成功——产品要过硬，价格要厚道。' },
    { danger:'突变配方', safe:'配方永恒', detail:'哪怕盲测证明新口味更好，也绝不能贸然大改配方——消费者的"被剥夺超反应"会瞬间爆发，这正是后来"新可乐"惨败的真实教训。' },
  ];

  function renderTrial2(){
    var root = el('div');
    renderChrome(root, '试炼 二');
    var stage = el('div','stage');
    renderProgress(stage, 2, 5);
    stage.appendChild(chapterTag('试炼 二 · 反过来想的护城河'));

    var card = el('div','card scene-enter');
    card.appendChild(el('div','card-title','提前避开四个致命伤'));
    card.appendChild(el('div','card-quote',
      '别只想着怎么赢，先想清楚：怎么会输？找出那把杀死我们的刀，然后离它远一点。'));
    card.appendChild(el('div','card-body','点击每张"危险牌"，翻出对应的解法。'));
    stage.appendChild(card);

    var grid = el('div','danger-grid');
    var flippedCount = 0;
    T2_CARDS.forEach(function(c, idx){
      var wrap = el('div','danger-card');
      var inner = el('div','danger-inner');
      var front = el('div','danger-face danger-front', c.danger);
      var back = el('div','danger-face danger-back', c.safe);
      inner.appendChild(front);
      inner.appendChild(back);
      wrap.appendChild(inner);
      wrap.onclick = function(){
        if (wrap.classList.contains('flipped')) return;
        wrap.classList.add('flipped');
        haptic();
        flippedCount++;
        var detailBox = el('div','result-box scene-enter', c.detail);
        detailSlot.appendChild(detailBox);
        if (flippedCount === T2_CARDS.length) {
          earnSeal('reverse');
          next.disabled = false;
        }
      };
      grid.appendChild(wrap);
    });
    stage.appendChild(grid);

    var detailSlot = el('div','detail-slot');
    stage.appendChild(detailSlot);

    root.appendChild(stage);
    var nav = el('div','bottom-nav');
    var next = el('button','nav-btn primary','下一试炼');
    next.disabled = true;
    next.onclick = function(){ haptic(); goScene('trial3'); };
    nav.appendChild(next);
    root.appendChild(nav);
    return root;
  }

  /* ============================================
     试炼三：芒格的算账题（滑块）
     ============================================ */
  function renderTrial3(){
    var root = el('div');
    renderChrome(root, '试炼 三');
    var stage = el('div','stage');
    renderProgress(stage, 3, 5);
    stage.appendChild(chapterTag('试炼 三 · 数字流畅性'));

    var card = el('div','card scene-enter');
    card.appendChild(el('div','card-title','芒格的算账题'));
    card.appendChild(el('div','card-quote',
      '把三个参数都推到最高值：如果 X% 的世界人口愿意为你的饮料改变饮水习惯，你还要拿下这个新市场的 Y% 份额，同时保持 Z 美分的高利润。'));
    card.appendChild(el('div','card-body',
      '拖动下面三个滑块，用最朴素、可验证的保守假设，算出这个结果是否依然惊人。'));
    stage.appendChild(card);

    var sliderCard = el('div','card scene-enter');
    var group = el('div','slider-group');

    var vals = { pop: 80, share: 25, profit: 4 };
    var labels = {};

    function makeSlider(id, labelText, min, max, step, initVal, suffix){
      var row = el('div','slider-row');
      var lab = el('div','slider-label');
      var span = el('span', null, labelText);
      var valSpan = el('b', null, initVal + suffix);
      labels[id] = valSpan;
      lab.appendChild(span);
      lab.appendChild(valSpan);
      row.appendChild(lab);
      var input = document.createElement('input');
      input.type = 'range';
      input.min = min; input.max = max; input.step = step; input.value = initVal;
      input.oninput = function(){
        vals[id] = parseFloat(input.value);
        valSpan.textContent = input.value + suffix;
        updateResult();
      };
      row.appendChild(input);
      group.appendChild(row);
    }

    makeSlider('pop', '全球饮料消费人口渗透率', 0, 100, 1, 80, '%');
    makeSlider('share', '你的产品市场份额', 0, 100, 1, 25, '%');
    makeSlider('profit', '每份净赚（美分）', 1, 10, 0.5, 4, '¢');

    sliderCard.appendChild(group);
    var resultBox = el('div','result-box');
    sliderCard.appendChild(resultBox);
    stage.appendChild(sliderCard);

    function updateResult(){
      // 到 2034 年全球约 80 亿人，每人每天 8 杯（64 盎司）水需求
      var totalPeople = 8e9; // 80亿
      var dailyServings = 8; // 每人每天 8 杯
      var reachablePeople = totalPeople * (vals.pop/100);
      var servedPeople = reachablePeople * (vals.share/100);
      var dailyProfitUSD = servedPeople * dailyServings * (vals.profit/100);
      var annualProfitUSD = dailyProfitUSD * 365;
      var annualProfitBillion = annualProfitUSD / 1e9;
      resultBox.innerHTML = '按当前假设，年利润约为 <b>' + annualProfitBillion.toFixed(0) +
        ' 亿美元</b>' + (annualProfitBillion >= 100 ? '，足以支撑 2 万亿估值。' : '，仍需提升三个参数中的某一项。') +
        '<br><br>这正是芒格算账的精髓：不是编造一个乐观故事，而是用最朴素的假设检验一个宏大结论是否站得住脚。';
    }
    updateResult();

    root.appendChild(stage);
    var nav = el('div','bottom-nav');
    var next = el('button','nav-btn primary','下一试炼');
    next.onclick = function(){ haptic(); earnSeal('reflex'); goScene('trial4'); };
    nav.appendChild(next);
    root.appendChild(nav);
    return root;
  }

  /* ============================================
     试炼四：双重条件反射分类
     ============================================ */
  var T4_ITEMS = [
    { label:'冰镇解暑', type:'operant', detail:'喝下去立刻感到凉爽——这是直接的生理奖励，行为发生后马上得到满足，属于操作性条件反射。' },
    { label:'圣诞团聚', type:'pavlov', detail:'喝可乐本身不会带来圣诞节的快乐，这只是长期广告把两者反复配对后产生的纯粹联想，属于巴甫洛夫条件反射。' },
    { label:'提神咖啡因', type:'operant', detail:'咖啡因带来真实的生理提神效果，喝下去就有感觉，是直接奖励，属于操作性条件反射。' },
    { label:'香槟质感', type:'pavlov', detail:'把饮料做成香槟的样子，只是借用"香槟=庆祝"的既有联想，产品本身并不能带来香槟的效果，属于巴甫洛夫条件反射。' },
    { label:'甜味刺激', type:'operant', detail:'甜味直接刺激味蕾产生愉悦感，这是即时的生理奖励，属于操作性条件反射。' },
    { label:'士兵与家', type:'pavlov', detail:'可乐不能真的把士兵送回家，这是"可乐=家乡"的联想被反复强化后的结果，属于巴甫洛夫条件反射。' },
  ];

  function renderTrial4(){
    var root = el('div');
    renderChrome(root, '试炼 四');
    var stage = el('div','stage');
    renderProgress(stage, 4, 5);
    stage.appendChild(chapterTag('试炼 四 · 双重条件反射'));

    var card = el('div','card scene-enter');
    card.appendChild(el('div','card-title','欲望闭环：操作性 + 巴甫洛夫'));
    card.appendChild(el('div','card-quote',
      '不要指望靠讲道理说服消费者。人的大脑，本质上和巴甫洛夫的狗没有区别。' +
      '我们要同时启动两套机制：操作性条件反射给奖励，巴甫洛夫条件反射建联想。'));
    card.appendChild(el('div','card-body','点击每张卡片，判断它属于哪一种条件反射。'));
    stage.appendChild(card);

    var grid = el('div','tile-grid');
    var doneCount = 0;
    T4_ITEMS.forEach(function(item){
      var tile = el('div','tile', item.label);
      tile.onclick = function(){
        if (tile.classList.contains('picked')) return;
        haptic();
        openPicker(item, tile);
      };
      grid.appendChild(tile);
    });
    stage.appendChild(grid);

    var detailSlot = el('div','detail-slot');
    stage.appendChild(detailSlot);

    function openPicker(item, tile){
      var pickerCard = el('div','card scene-enter');
      pickerCard.appendChild(el('div','card-body', '"' + item.label + '" 属于——'));
      var list = el('div','choice-list');
      var opA = el('button','choice-btn','操作性条件反射（给奖励）');
      var opB = el('button','choice-btn','巴甫洛夫条件反射（建联想）');
      function pick(chosenType, btnEl){
        Array.prototype.forEach.call(list.children, function(b){ b.disabled = true; });
        if (chosenType === item.type) {
          btnEl.classList.add('correct');
        } else {
          btnEl.classList.add('wrong');
        }
        var det = el('div','result-box scene-enter', item.detail);
        pickerCard.appendChild(det);
        tile.classList.add('picked','locked-correct');
        doneCount++;
        if (doneCount === T4_ITEMS.length) {
          earnSeal('moat');
          next.disabled = false;
        }
      }
      opA.onclick = function(){ pick('operant', opA); };
      opB.onclick = function(){ pick('pavlov', opB); };
      list.appendChild(opA);
      list.appendChild(opB);
      pickerCard.appendChild(list);
      detailSlot.innerHTML = '';
      detailSlot.appendChild(pickerCard);
      pickerCard.scrollIntoView({ behavior:'smooth', block:'nearest' });
    }

    root.appendChild(stage);
    var nav = el('div','bottom-nav');
    var next = el('button','nav-btn primary','下一试炼');
    next.disabled = true;
    next.onclick = function(){ haptic(); goScene('trial5'); };
    nav.appendChild(next);
    root.appendChild(nav);
    return root;
  }

  /* ============================================
     试炼五：分包而非放权（历史抉择）
     ============================================ */
  var T5_OPTIONS = [
    { key:'perm', label:'一次性授予永久特许权，条款永不可改', correct:false,
      detail:'这正是可口可乐真实犯过的错误。真实历史上，公司把装瓶权作为永久特许权批给了各地装瓶商，价格条款一次锁死、永不能改。短期看，这换来了装瓶商快速跑马圈地的积极性；但代价是此后几十年，无论原材料成本怎么涨，公司都无法向这些装瓶商重新议价——定价权就这样被永久让渡了出去，这也是公司历史上最惨痛的战略失误之一。' },
    { key:'sub', label:'签阶段性分包协议，定期重新谈判条款', correct:true,
      detail:'这才是芒格会做的选择。把装瓶商定位成"分包商"而非"永久特许受让人"——协议要设定周期，到期重新谈判价格和条款。这样公司既能借装瓶商的资金和人力快速铺开全球网络，又能始终握住重新定价的权力，不被通胀和成本上涨反噬。真正的护城河不仅是产品端的，也包括你和合作伙伴之间的权力结构设计。' },
  ];

  function renderTrial5(){
    var root = el('div');
    renderChrome(root, '试炼 五');
    var stage = el('div','stage');
    renderProgress(stage, 5, 5);
    stage.appendChild(chapterTag('试炼 五 · 分包而非放权'));

    var card = el('div','card scene-enter');
    card.appendChild(el('div','card-title','定价权永远不丢'));
    card.appendChild(el('div','card-quote',
      '六座工厂都建好了，装瓶商代表找上门来，提出签一份长期协议。你会怎么定这份合约？'));
    stage.appendChild(card);

    var list = el('div','choice-list');
    var answered = false;
    var resultSlot = el('div','result-slot');
    T5_OPTIONS.forEach(function(opt){
      var btn = el('button','choice-btn', opt.label);
      btn.onclick = function(){
        if (answered) return;
        answered = true;
        haptic();
        Array.prototype.forEach.call(list.children, function(b){ b.disabled = true; });
        btn.classList.add(opt.correct ? 'correct' : 'wrong');
        var box = el('div','result-box scene-enter', opt.detail);
        resultSlot.appendChild(box);
        earnSeal('lolla');
        next.disabled = false;
      };
      list.appendChild(btn);
    });
    stage.appendChild(list);
    stage.appendChild(resultSlot);

    root.appendChild(stage);
    var nav = el('div','bottom-nav');
    var next = el('button','nav-btn primary','查看历史尾声');
    next.disabled = true;
    next.onclick = function(){ haptic(); goScene('ending'); };
    nav.appendChild(next);
    root.appendChild(nav);
    return root;
  }

  /* ============================================
     尾声：真实历史对照 + 印章总结
     ============================================ */
  function renderEnding(){
    var root = el('div');
    renderChrome(root, '智慧的回响');
    var stage = el('div','stage');
    stage.appendChild(chapterTag('尾 声 · 真实历史对照'));

    var scoreCard = el('div','card scene-enter');
    var hero = el('div','score-hero');
    hero.appendChild(el('div','num', state.seals.length + ' / 5'));
    hero.appendChild(el('div','lbl','枚思维印章'));
    scoreCard.appendChild(hero);

    var strip = el('div','seal-strip');
    SEAL_DEFS.forEach(function(s){
      var earned = state.seals.indexOf(s.key) !== -1;
      var seal = el('div','seal' + (earned ? ' earned' : ''), s.icon);
      strip.appendChild(seal);
    });
    scoreCard.appendChild(strip);

    var msg = state.seals.length === 5
      ? '满分！思维大师——四个模型同向发力，自我催化产生奇迹。'
      : (state.seals.length >= 3 ? '不错！继续努力。' : '再试一次吧。');
    scoreCard.appendChild(el('p','card-body', msg));
    stage.appendChild(scoreCard);

    var historyCard = el('div','card scene-enter');
    historyCard.appendChild(el('div','card-title','即使犯了这些错误，正确的战略依然让它走到了这一步'));
    historyCard.appendChild(el('div','card-body',
      '真实的可口可乐公司净值不足 15 万美元，几乎没有利润。公司确实丢掉了商标的一半，还把永久特许权批给了装瓶商，从此失去了大量定价权。' +
      '"新可乐"事件中，管理层没能预见消费者的心理反应，险些酿成灾难。'));
    historyCard.appendChild(el('div','card-body',
      '<b style="color:var(--gold-dark)">即便如此，公司仍值约 1250 亿美元</b>——此后只需年化个位数的增速，就能在 2034 年抵达 2 万亿。'));
    stage.appendChild(historyCard);

    var quoteCard = el('div','card scene-enter');
    quoteCard.appendChild(el('div','card-quote',
      '我想让每一位美国大兵，伸手就能拿到一罐可乐——那是家乡的味道。'));
    quoteCard.appendChild(el('div','card-narrator','—— 艾森豪威尔，盟军最高统帅'));
    stage.appendChild(quoteCard);

    var wisdomCard = el('div','card scene-enter');
    wisdomCard.appendChild(el('div','card-title','所有的智慧都在你日常的常识里'));
    wisdomCard.appendChild(el('div','card-body',
      '掌握那些基础的、跨学科的思维模型——化繁为简、反过来想、双重条件反射、分包而非放权——四个模型同时发力，自我催化产生奇迹（鲁拉帕路萨效应）。你也能创造自己的奇迹。'));
    wisdomCard.appendChild(el('div','card-narrator','—— 查理·芒格'));
    stage.appendChild(wisdomCard);

    root.appendChild(stage);
    var nav = el('div','bottom-nav');
    var retry = el('button','nav-btn ghost','再玩一次');
    retry.onclick = function(){
      haptic();
      state.seals = [];
      goScene('intro');
    };
    nav.appendChild(retry);
    root.appendChild(nav);
    return root;
  }

  /* ============================================
     主渲染分发
     ============================================ */
  var SCENE_RENDERERS = {
    intro: renderIntro,
    letter: renderLetter,
    trial1: renderTrial1,
    trial2: renderTrial2,
    trial3: renderTrial3,
    trial4: renderTrial4,
    trial5: renderTrial5,
    ending: renderEnding,
  };

  function render(){
    app.innerHTML = '';
    var renderer = SCENE_RENDERERS[state.scene] || renderIntro;
    app.appendChild(renderer());
  }

  render();
})();
