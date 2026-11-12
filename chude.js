/* BKOJ - Lọc theo tab và tìm kiếm cho các trang dạng thẻ.
   Hoạt động với component filter_bar (data-bk-filter), card_section (data-bk-group),
   topic_card (data-bk-item) và empty_state (data-bk-empty). */
(function () {
  /* ---- Chế độ tối: đo màu nền thật phía sau trang, nền tối thì thêm lớp bk-dark ---- */
  var page = document.querySelector(".bk-page");
  function backgroundOf(el) {
    while (el) {
      var c = getComputedStyle(el).backgroundColor;
      if (c && c !== "transparent" && !/rgba\(\s*0,\s*0,\s*0,\s*0\s*\)/.test(c)) return c;
      el = el.parentElement;
    }
    return "rgb(255, 255, 255)";
  }
  function updateTheme() {
    if (!page) return;
    var m = backgroundOf(page.parentElement).match(/[\d.]+/g) || [255, 255, 255];
    page.classList.toggle("bk-dark", 0.299 * m[0] + 0.587 * m[1] + 0.114 * m[2] < 110);
  }
  updateTheme();
  window.addEventListener("load", updateTheme);
  var watch = new MutationObserver(function () { setTimeout(updateTheme, 50); });
  [document.documentElement, document.body].forEach(function (el) {
    watch.observe(el, { attributes: true, attributeFilter: ["class", "style", "data-theme"] });
  });
  watch.observe(document.head, { childList: true });
  document.addEventListener("click", function (e) {
    if (e.target.closest && e.target.closest("#nav-darkmode-icon")) setTimeout(updateTheme, 300);
  });

  var bar = document.querySelector("[data-bk-filter]");
  if (!bar) return;
  var tabs = bar.querySelectorAll(".bk-tab");
  var search = bar.querySelector("[data-bk-search]");
  var groups = document.querySelectorAll("[data-bk-group]");
  var empty = document.querySelector("[data-bk-empty]");
  var current = tabs.length ? tabs[0].dataset.filter : "all";

  function norm(s) {
    return (s || "").toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/đ/g, "d");
  }

  function apply() {
    var q = norm(search ? search.value.trim() : ""), shown = 0;
    groups.forEach(function (group) {
      var inTab = current === "all" || group.dataset.bkGroup === current, visible = 0;
      group.querySelectorAll("[data-bk-item]").forEach(function (item) {
        var ok = inTab && norm(item.dataset.text).indexOf(q) !== -1;
        item.style.display = ok ? "" : "none";
        if (ok) visible++;
      });
      group.style.display = visible ? "" : "none";
      shown += visible;
    });
    if (empty) empty.hidden = shown > 0;
  }

  tabs.forEach(function (tab) {
    tab.addEventListener("click", function () {
      tabs.forEach(function (t) { t.classList.remove("is-active"); });
      tab.classList.add("is-active");
      current = tab.dataset.filter;
      apply();
    });
  });
  if (search) search.addEventListener("input", apply);
})();
