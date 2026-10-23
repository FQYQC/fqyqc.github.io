/*
 * Keep in-page anchor targets in place while lazy images load.
 *
 * Post images are lazy-loaded by lazysizes and have no reserved size: each
 * one is a 60px placeholder until its photo arrives. After a TOC click or a
 * page load with a #hash, photos above the target finish loading and push the
 * heading down. Browsers without scroll anchoring (Safari) then leave the
 * reader somewhere else, and even with anchoring a shift during the smooth
 * scroll makes it land short.
 *
 * While a target is "pinned", this script re-aligns it to its scroll-margin-top
 * whenever the page height changes or a scroll comes to rest. Pinning stops as
 * soon as the reader scrolls, touches, clicks or presses a key, or after
 * PIN_MS. See docs/architecture.md ("目录跳转与图片懒加载").
 */
(function () {
  'use strict';

  if (!('ResizeObserver' in window)) return;

  var PIN_MS = 20000;
  var SCROLL_IDLE_MS = 150;

  var target = null;
  var deadline = 0;
  var settled = false; // aligned at least once since pinning
  var dirty = false; // layout changed while a scroll was in progress
  var alignedY = 0; // scroll position right after the last alignment
  var lastScrollAt = 0;
  var idleTimer = null;
  var bodyHeight = -1;

  function elementForHash(hash) {
    if (!hash || hash.length < 2) return null;
    var id = hash.slice(1);
    try {
      id = decodeURIComponent(id);
    } catch (e) {
      /* keep the raw id */
    }
    return document.getElementById(id);
  }

  function pin(el) {
    target = el;
    deadline = Date.now() + PIN_MS;
    settled = false;
    dirty = false;
  }

  function unpin() {
    target = null;
  }

  function jumpTo(y) {
    // Bypass the theme's `scroll-behavior: smooth` so the correction lands in
    // the same frame as the layout change instead of animating.
    var root = document.documentElement;
    var previous = root.style.scrollBehavior;
    root.style.scrollBehavior = 'auto';
    window.scrollTo(window.pageXOffset, y);
    root.style.scrollBehavior = previous;
  }

  // Distance between the target and where the browser puts an anchor target
  // (its scroll-margin-top, i.e. just below the fixed header).
  function offset() {
    var margin = parseFloat(getComputedStyle(target).scrollMarginTop) || 0;
    return target.getBoundingClientRect().top - margin;
  }

  function realign() {
    if (!target) return;
    if (Date.now() > deadline || !target.isConnected) {
      unpin();
      return;
    }
    var delta = offset();
    if (Math.abs(delta) >= 1) jumpTo(window.pageYOffset + delta);
    settled = true;
    dirty = false;
    alignedY = window.pageYOffset;
  }

  function onScrollIdle() {
    idleTimer = null;
    if (!target) return;
    // A scroll that moved away from the aligned position without any layout
    // change came from the reader (e.g. dragging the scrollbar): let go.
    if (settled && !dirty && Math.abs(window.pageYOffset - alignedY) > 2) {
      unpin();
      return;
    }
    realign();
  }

  window.addEventListener('scroll', function () {
    if (!target) return;
    // Arriving at the target (end of the smooth scroll, our own corrections,
    // scroll anchoring) is not "scrolling"; anything else is, until it rests.
    if (Math.abs(offset()) < 1) {
      settled = true;
      alignedY = window.pageYOffset;
    } else if (!settled || Math.abs(window.pageYOffset - alignedY) >= 1) {
      lastScrollAt = Date.now();
    }
    if (idleTimer) window.clearTimeout(idleTimer);
    idleTimer = window.setTimeout(onScrollIdle, SCROLL_IDLE_MS);
  }, { passive: true });

  // Image loads change the page height. ResizeObserver callbacks run after
  // layout and before paint, so an idle correction is not visible as a jump.
  new ResizeObserver(function () {
    var height = document.body.getBoundingClientRect().height;
    if (height === bodyHeight) return;
    bodyHeight = height;
    if (!target) return;
    if (Date.now() - lastScrollAt < SCROLL_IDLE_MS) {
      dirty = true; // wait for the smooth scroll to finish (onScrollIdle)
    } else {
      realign();
    }
  }).observe(document.body);

  // Any direct input means the reader has taken over.
  ['wheel', 'touchstart', 'pointerdown', 'mousedown', 'keydown'].forEach(function (type) {
    window.addEventListener(type, unpin, { capture: true, passive: true });
  });

  // Same-page anchor clicks (TOC, heading links, footnotes). The browser
  // still performs the scroll itself; this only pins the destination.
  document.addEventListener('click', function (event) {
    if (event.defaultPrevented || event.button !== 0) return;
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    var link = event.target.closest && event.target.closest('a[href*="#"]');
    if (!link || link.origin !== location.origin || link.pathname !== location.pathname) return;
    var el = elementForHash(link.hash);
    if (el) pin(el);
  });

  // Opening a URL with a #hash. Skip reloads and back/forward, where the
  // browser restores the reader's previous scroll position instead.
  var navigation = performance.getEntriesByType && performance.getEntriesByType('navigation')[0];
  if (!navigation || navigation.type === 'navigate') {
    var initial = elementForHash(location.hash);
    if (initial) {
      pin(initial);
      window.requestAnimationFrame(realign);
    }
  }
})();
