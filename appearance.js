/* An optional reading appearance; independent of holdings, language and game state. */
(function (win, doc) {
  'use strict';
  const KEY = '13f-site-appearance';
  const normalize = value => value === 'almanac' ? 'almanac' : 'current';
  function read(key) { try { return win.localStorage.getItem(key); } catch (_) { return null; } }
  let theme = normalize(read(KEY));

  function refresh() {
    const en = read('lang') === 'en', active = theme === 'almanac';
    doc.querySelectorAll('[data-appearance-toggle]').forEach(button => {
      button.setAttribute('aria-checked', String(active));
      button.setAttribute('aria-label', en ? 'Almanac appearance' : '年鉴主题');
      button.title = en ? 'Switch between current and illustrated almanac styles' : '在当前样式与插图年鉴样式之间切换';
      const label = button.querySelector('[data-appearance-label]');
      if (label) label.textContent = en ? 'Book' : '年鉴';
    });
  }
  function send(frame) {
    try { frame.contentWindow?.postMessage({type:'13f:appearance', theme}, win.location.origin); } catch (_) { /* Frame may still be loading. */ }
  }
  function set(value, persist = true) {
    theme = normalize(value);
    doc.documentElement.setAttribute('data-appearance', theme);
    if (persist) { try { win.localStorage.setItem(KEY, theme); } catch (_) { /* Still usable when storage is blocked. */ } }
    refresh();
    win.InvestorBookplates?.refresh();
    doc.querySelectorAll('iframe').forEach(send);
    return theme;
  }
  // Run in the head, before styles paint, so a saved choice never flashes the other theme.
  set(theme, false);
  doc.addEventListener('DOMContentLoaded', refresh);
  doc.addEventListener('click', event => {
    if (event.target.closest?.('[data-appearance-toggle]')) set(theme === 'almanac' ? 'current' : 'almanac');
    else if (event.target.closest?.('#langBtn')) refresh();
  });
  doc.addEventListener('load', event => { if (event.target.tagName === 'IFRAME') send(event.target); }, true);
  win.addEventListener('storage', event => { if (event.key === KEY || event.key === null) set(read(KEY), false); });
  win.addEventListener('message', event => {
    if (win.parent !== win && event.source === win.parent && event.origin === win.location.origin &&
        event.data?.type === '13f:appearance') set(event.data.theme, false);
  });
  win.SiteAppearance = {set, refresh, current: () => theme};
})(window, document);
