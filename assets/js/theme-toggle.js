/*
 * Make the theme switch flip light/dark on every click.
 *
 * LoveIt cycles cfg-theme through auto -> light -> dark. When the OS is in dark mode,
 * "auto" looks the same as "dark", so going dark -> auto changes only the icon and the
 * reader has to click again. Here every click targets the opposite of what is shown;
 * if that matches the OS preference it is stored as "auto" (keep following the system),
 * otherwise as an explicit "light" / "dark".
 *
 * The theme's own click handler still does the work (body attributes, localStorage,
 * switch-theme events for comments, charts, mermaid). This capture-phase listener runs
 * first and only rewrites cfg-theme so that the theme's "next state" is our target.
 */
(function () {
  'use strict';

  var CYCLE = ['auto', 'light', 'dark'];
  var media = window.matchMedia ? window.matchMedia('(prefers-color-scheme: dark)') : null;

  document.addEventListener('click', function (event) {
    if (!event.target.closest || !event.target.closest('.theme-switch')) return;
    var body = document.body;
    var wantDark = body.getAttribute('theme') !== 'dark';
    var systemDark = !!(media && media.matches);
    var target = wantDark === systemDark ? 'auto' : (wantDark ? 'dark' : 'light');
    var previous = CYCLE[(CYCLE.indexOf(target) + CYCLE.length - 1) % CYCLE.length];
    body.setAttribute('cfg-theme', previous);
  }, true);
})();
