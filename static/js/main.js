/**
 * AskSanatan - Main JavaScript
 */

document.addEventListener("DOMContentLoaded", function () {
  initFlashToasts();

  document.querySelectorAll(".alert-dismissible").forEach(function (alert) {
    setTimeout(function () {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) bsAlert.close();
    }, 5000);
  });

  document.querySelectorAll("[data-confirm]").forEach(function (el) {
    el.addEventListener("click", function (e) {
      if (!confirm(el.getAttribute("data-confirm"))) {
        e.preventDefault();
      }
    });
  });

  document.querySelectorAll(".qty-input").forEach(function (input) {
    input.addEventListener("change", function () {
      const min = parseInt(input.getAttribute("min")) || 1;
      const max = parseInt(input.getAttribute("max")) || 999;
      let val = parseInt(input.value) || min;
      if (val < min) val = min;
      if (val > max) val = max;
      input.value = val;
    });
  });
});

function initFlashToasts() {
  const container = document.getElementById("toast-container");
  if (!container) return;

  container.querySelectorAll(".flash-toast").forEach(function (flash, index) {
    const type = flash.dataset.type || "info";
    const message = flash.dataset.message || "";
    let bgClass = "bg-info";
    if (type === "success") bgClass = "bg-success";
    else if (type === "danger") bgClass = "bg-danger";
    else if (type === "warning") bgClass = "bg-warning text-dark";

    const toastEl = document.createElement("div");
    toastEl.className = "toast align-items-center text-white " + bgClass + " border-0 mb-2";
    toastEl.setAttribute("role", "alert");
    toastEl.innerHTML =
      '<div class="d-flex">' +
      '<div class="toast-body">' + message + "</div>" +
      '<button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>' +
      "</div>";

    container.appendChild(toastEl);
    const added = toastEl;
    const toast = new bootstrap.Toast(added, { delay: 5000 });
    setTimeout(function () {
      toast.show();
    }, index * 200);
    flash.remove();
  });
}

function initAdminCharts(analytics) {
  if (typeof Chart === "undefined" || !analytics) return;

  const salesCtx = document.getElementById("salesChart");
  if (salesCtx) {
    new Chart(salesCtx, {
      type: "line",
      data: {
        labels: analytics.months,
        datasets: [
          {
            label: "Sales (₹)",
            data: analytics.sales,
            borderColor: "#ff9933",
            backgroundColor: "rgba(255, 153, 51, 0.2)",
            fill: true,
            tension: 0.4,
          },
        ],
      },
      options: { responsive: true, scales: { y: { beginAtZero: true } } },
    });
  }

  const statusCtx = document.getElementById("statusChart");
  if (statusCtx) {
    new Chart(statusCtx, {
      type: "doughnut",
      data: {
        labels: analytics.status_labels,
        datasets: [
          {
            data: analytics.status_counts,
            backgroundColor: ["#ffc107", "#17a2b8", "#6f42c1", "#28a745", "#dc3545"],
          },
        ],
      },
      options: { responsive: true },
    });
  }

  const catCtx = document.getElementById("categoryChart");
  if (catCtx) {
    new Chart(catCtx, {
      type: "bar",
      data: {
        labels: analytics.cat_labels,
        datasets: [{ label: "Revenue (₹)", data: analytics.cat_values, backgroundColor: "#d4af37" }],
      },
      options: { responsive: true, scales: { y: { beginAtZero: true } } },
    });
  }
}
