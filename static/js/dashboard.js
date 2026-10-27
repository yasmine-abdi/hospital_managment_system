/* ============================================================
   School Management System — Dashboard JS
   Minimal, dependency-free
   ============================================================ */

(function () {
  "use strict";

  // ── Mobile sidebar toggle ──────────────────────────────────
  const sidebar        = document.getElementById("sidebar");
  const overlay        = document.getElementById("sidebarOverlay");
  const mobileMenuBtn  = document.getElementById("mobileMenuBtn");

  function openSidebar() {
    sidebar.classList.add("open");
    overlay.classList.add("open");
    document.body.style.overflow = "hidden";
  }

  function closeSidebar() {
    sidebar.classList.remove("open");
    overlay.classList.remove("open");
    document.body.style.overflow = "";
  }

  if (mobileMenuBtn) {
    mobileMenuBtn.addEventListener("click", openSidebar);
  }
  if (overlay) {
    overlay.addEventListener("click", closeSidebar);
  }

  // Close sidebar on escape
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") closeSidebar();
  });

  // ── Auto-dismiss Django messages ───────────────────────────
  const messages = document.querySelectorAll(".message");
  messages.forEach(function (msg) {
    setTimeout(function () {
      msg.style.transition = "opacity .4s ease, transform .4s ease";
      msg.style.opacity    = "0";
      msg.style.transform  = "translateX(20px)";
      setTimeout(function () { msg.remove(); }, 400);
    }, 5000);
  });

  // ── Active nav link (highlight current section) ───────────
  // Already handled via Django template blocks, but this adds
  // a fallback for any links that match the current path.
  const currentPath = window.location.pathname;
  document.querySelectorAll(".sidebar-link").forEach(function (link) {
    if (link.getAttribute("href") === currentPath && !link.classList.contains("active")) {
      link.classList.add("active");
    }
  });

  // ── Global search (placeholder — wire up to Django view) ──
  const searchInput = document.querySelector(".topbar-search input");
  if (searchInput) {
    let timeout;
    searchInput.addEventListener("input", function () {
      clearTimeout(timeout);
      const q = this.value.trim();
      if (q.length < 2) return;
      timeout = setTimeout(function () {
        // Example: window.location.href = `/search/?q=${encodeURIComponent(q)}`;
        // Wire up to your Django search URL here.
        console.log("Search query:", q);
      }, 400);
    });
  }

})();
