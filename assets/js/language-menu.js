/*
 * Desktop language picker in the site's own style.
 *
 * LoveIt renders a transparent native <select> over the globe icon, which opens an
 * OS-styled dropdown. On desktop the select ignores clicks (see _custom.scss) and this
 * script shows a small menu built from the select's options instead: the current
 * language is marked, the other one links to the translation of this page. If the page
 * has no translation, the other language links to its home page. Click outside or press
 * Esc to close. The mobile menu keeps the native picker.
 */
(function () {
  'use strict';

  // Home page and label of each language; keep in sync with hugo.toml.
  var LANGS = [
    { code: 'en', home: '/', name: 'English' },
    { code: 'zh-cn', home: '/zh-cn/', name: '简体中文' }
  ];

  function currentCode() {
    return location.pathname.indexOf('/zh-cn/') === 0 ? 'zh-cn' : 'en';
  }

  function entries(select) {
    var list = Array.prototype.map.call(select.options, function (option) {
      return { name: option.text.trim(), url: option.value, current: option.selected };
    });
    if (list.length > 1) return list;
    // No translation of this page: offer the other languages' home pages.
    var here = currentCode();
    return LANGS.map(function (lang) {
      return { name: lang.name, url: lang.code === here ? location.pathname : lang.home, current: lang.code === here };
    });
  }

  function init() {
    var item = document.querySelector('#header-desktop .menu-item.language');
    var select = document.getElementById('language-select-desktop');
    if (!item || !select) return;

    var menu = document.createElement('div');
    menu.className = 'language-menu';
    menu.setAttribute('role', 'menu');
    menu.hidden = true;
    entries(select).forEach(function (entry) {
      var link = document.createElement('a');
      link.className = 'language-menu-item' + (entry.current ? ' is-current' : '');
      link.href = entry.url;
      link.textContent = entry.name;
      link.setAttribute('role', 'menuitem');
      if (entry.current) link.setAttribute('aria-current', 'true');
      menu.appendChild(link);
    });
    document.body.appendChild(menu);

    item.setAttribute('aria-haspopup', 'menu');
    item.setAttribute('aria-expanded', 'false');

    function place() {
      var rect = item.getBoundingClientRect();
      var header = document.getElementById('header-desktop');
      var bottom = header ? header.getBoundingClientRect().bottom : rect.bottom;
      menu.style.top = Math.round(bottom + 6) + 'px';
      menu.style.right = Math.round(document.documentElement.clientWidth - rect.right) + 'px';
    }

    function open() {
      place();
      menu.hidden = false;
      item.setAttribute('aria-expanded', 'true');
    }

    function close() {
      menu.hidden = true;
      item.setAttribute('aria-expanded', 'false');
    }

    item.addEventListener('click', function (event) {
      event.preventDefault();
      if (menu.hidden) open(); else close();
    });
    document.addEventListener('click', function (event) {
      if (!menu.hidden && !menu.contains(event.target) && !item.contains(event.target)) close();
    });
    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape') close();
    });
    window.addEventListener('resize', close);
    window.addEventListener('scroll', close, { passive: true });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
