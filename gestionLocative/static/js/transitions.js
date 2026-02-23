/**
 * Solulocate — Transitions fluides (fade-in) au chargement
 * Ajoute la classe .page-ready sur body et .visible sur les éléments .fade-in / .fade-in-up / .section-fade
 */
(function () {
  'use strict';

  function ready(fn) {
    if (document.readyState !== 'loading') {
      fn();
    } else {
      document.addEventListener('DOMContentLoaded', fn);
    }
  }

  function triggerPageReady() {
    document.body.classList.add('page-ready');
  }

  function revealFadeElements() {
    var selectors = ['.fade-in', '.fade-in-up', '.section-fade', '.main-container', '.hero-accueil'];
    selectors.forEach(function (sel) {
      var nodes = document.querySelectorAll(sel);
      nodes.forEach(function (el, i) {
        (function (element, index) {
          setTimeout(function () {
            element.classList.add('visible');
          }, index * 50);
        })(el, i);
      });
    });
  }

  function observeFadeElements() {
    var fadeEls = document.querySelectorAll('.fade-in, .fade-in-up, .section-fade');
    if (!fadeEls.length) return;

    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
          }
        });
      },
      { rootMargin: '0px 0px -40px 0px', threshold: 0.1 }
    );

    fadeEls.forEach(function (el) {
      observer.observe(el);
    });
  }

  ready(function () {
    triggerPageReady();
    revealFadeElements();
    observeFadeElements();
  });
})();
