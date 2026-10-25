/* Original decorative identities, drawn from the reviewed investor profiles. */
(function (win, doc) {
  'use strict';
  const entries = [
    ['lilu','#31594d','#e3e7d6','map','山高水长','Mountains & compounding'],
    ['pabrai','#8a4c28','#f0dfc4','coins','正面与反面','Asymmetric odds'],
    ['duan','#4c6244','#e6e7d5','seal','本分与生意','Business & discipline'],
    ['tepper','#344f68','#e0e6e6','tides','风浪里的灯塔','A light through the storm'],
    ['webb','#285e68','#e2ebdf','ledger','让阳光照进来','Let the sunlight in'],
    ['buffett','#425a38','#e5e6cb','botanical','给好生意以时间','Give good businesses time'],
    ['akre','#75442e','#ecdfcd','joinery','三条腿的凳子','The three-legged stool'],
    ['greenberg','#4d4a6f','#e5dfeb','pruning','少而精的枝叶','A carefully pruned garden'],
    ['klarman','#7d3547','#eadcdb','margin','为判断留出余地','Leave room for error'],
    ['ackman','#3a4c79','#dfe4ee','blueprint','研究之后，行动','From research to action'],
    ['abrams','#655344','#e9e2d5','study','安静处，做研究','A quiet place to study'],
    ['berkowitz','#7c4b28','#ead7c2','copper','跟着现金走','Follow the cash'],
    ['hawkins','#575b30','#e7e4cc','survey','把企业放上天平','Weigh the whole business'],
    ['vinall','#286359','#dce8dc','partner','与经营者同坐一桌','At the same table'],
    ['marks','#65471f','#e9dfbd','pendulum','给钟摆留一把尺','A ruler for the pendulum'],
    ['greenblatt','#566028','#e9e6cc','two-rulers','两把尺，一起量','Two measures, one judgment'],
    ['mclemore','#743e55','#eddee1','hourglass','让时间成为同伴','Make time an ally']
  ];
  const designs = Object.freeze(Object.fromEntries(entries.map(([id,ink,wash,finish,zh,en]) =>
    [id,Object.freeze({ink,wash,finish,label:Object.freeze([zh,en])})])));
  let selected = null, english = false;
  function refresh() {
    const figure = doc.querySelector('.almanac-vignette');
    if (!figure) return;
    // Hidden <img> elements still download. Keep the default appearance asset-free.
    if (!selected || doc.documentElement.getAttribute('data-appearance') !== 'almanac') {
      figure.replaceChildren(); return;
    }
    const source = 'assets/almanac/bookplates/' + selected + '.svg';
    let image = figure.querySelector('img');
    if (!image || image.getAttribute('src') !== source) {
      image = doc.createElement('img');
      image.setAttribute('src',source);
    }
    image.alt = ''; image.width = 220; image.height = 190; image.decoding = 'async';
    const caption = figure.querySelector('figcaption') || doc.createElement('figcaption');
    caption.textContent = designs[selected].label[english ? 1 : 0];
    figure.replaceChildren(image,caption);
  }
  function select(id, en = false) {
    selected = Object.prototype.hasOwnProperty.call(designs,id) ? id : null;
    english = !!en;
    const root = doc.documentElement, design = designs[selected];
    if (design) {
      root.setAttribute('data-investor',selected);
      root.setAttribute('data-bookplate-finish',design.finish);
      root.style.setProperty('--identity-ink',design.ink);
      root.style.setProperty('--identity-wash',design.wash);
    } else {
      root.removeAttribute('data-investor'); root.removeAttribute('data-bookplate-finish');
      root.style.removeProperty('--identity-ink'); root.style.removeProperty('--identity-wash');
    }
    refresh();
  }
  win.InvestorBookplates = {select,refresh,designs};
})(window,document);
