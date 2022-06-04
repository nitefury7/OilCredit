"use strict";
const LATEST_SPENDINGS_ENDPOINT = "/customer/latest_spendings";
const SPENDINGS_BY_PRODUCT = "/customer/spendings_by_product";

$(document).ready(() => {
  $("#order_history").DataTable();
});

String.prototype.hashCode = function () {
  // fnv1a implementation
  let FNV1_32A_INIT = 0x811c9dc5;
  let hval = FNV1_32A_INIT;
  for (let i = 0; i < this.length; ++i) {
    hval ^= this.charCodeAt(i);
    hval +=
      (hval << 1) + (hval << 4) + (hval << 7) + (hval << 8) + (hval << 24);
  }
  return hval >>> 0;
};

function getColor(label, opacity = "ff") {
  return (
    "#" + Math.abs(label.hashCode()).toString(16).substring(0, 6) + opacity
  );
}

$(document).ready(async () => {
  const ctx = document.getElementById("spendings_by_product").getContext("2d");
  const response = await fetch(SPENDINGS_BY_PRODUCT);
  const json = await response.json();
  new Chart(ctx, {
    type: "bar",
    data: {
      labels: Object.keys(json),
      datasets: [
        {
          label: "Spendings by product",
          data: Object.values(json),
          backgroundColor: Object.keys(json).map((x) => getColor(x, "50")),
          borderColor: ["#FF0000FF"],
          borderWidth: 1,
        },
      ],
    },
    options: { scales: { y: { beginAtZero: true } } },
  });
});

$(document).ready(async () => {
  const ctx = document.getElementById("latest_spendings").getContext("2d");
  const response = await fetch(LATEST_SPENDINGS_ENDPOINT);
  const json = await response.json();
  const data = {
    labels: ["9", "8", "7", "6", "5", "4", "3", "2", "1", "Today"],
    datasets: [
      {
        label: "Recent Purchases",
        data: json,
        fill: true,
        borderColor: "#f87",
        tension: 0.1,
      },
    ],
  };
  new Chart(ctx, {
    type: "line",
    data: data,
    options: { maintainAspectRatio: true, aspectRatio: 1 },
    plugins: {
      title: { display: true, text: "Spendings during the last ten days." },
    },
  });
});
