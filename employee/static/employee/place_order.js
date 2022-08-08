"use strict";
let delete_input_group = () => {};

const GET_CUSTOMERS_ENDPOINT = "/employee/get_customers";
const GET_ITEMS_ENDPOINT = "/employee/get_items";
const GET_CSRF_TOKEN_ENDPOINT = "/get_csrf_token";

function initialize_user_select(users) {
  const user_select_options_html = Array.from(users)
    .map((user) => `<option value='${user.id}'>${user.username}</option>`)
    .join("");

  $("#customer_select").html(user_select_options_html);
  $("#customer_select").select2({ theme: "bootstrap-5", width: "80%" });

  // On change customer
  const onChangeCustomer = async () => {
    const id = $("#customer_select").val();

    const user_info = await (async () => {
      const response = await fetch(`get_customer_profile/${id}`);
      return await response.json();
    })();

    let html = `
        <tbody>
            <tr> <th>Username</th> <td>${user_info.username}</td> </tr>
            <tr> <th>Account Number</th> <td>${user_info.id}</td> </tr>
            <tr> <th>First Name</th> <td>${user_info.first_name}</td> </tr>
            <tr> <th>Last Name</th> <td>${user_info.last_name}</td> </tr>
            <tr> <th>Contact</th> <td>${user_info.contact}</td> </tr>
            <tr> <th>Email</th> <td>${user_info.email}</td> </tr>
            <tr> <th>Available Credit</th> <td>${user_info.credit}</td> </tr>
        </tbody>
      `;
    $("#customer_profile").html(html);
    $("#customer_profile_card").removeClass("d-none");
  };
  $("#customer_select").on("change", onChangeCustomer);
  onChangeCustomer();
}

// Get customer list
$(document).ready(async () => {
  const users = await (async () => {
    let response = await fetch(GET_CUSTOMERS_ENDPOINT);
    return await response.json();
  })();
  initialize_user_select(users);
});

function initialize_items_form(items) {
  const items_map = new Map();
  for (let item of items) {
    items_map.set(item.id, item);
  }

  const construct_table_rows = () => {
    let total_cost = 0.0;
    let receipt_table_html = "";
    for (let input_group of Array.from($("#orders_list").children())) {
      const item_id = +input_group.children[0].value;
      const input_volume = +input_group.children[1].value;
      const input_total = +input_group.children[2].value;
      const item = items_map.get(item_id);
      total_cost += input_total;
      receipt_table_html += `
        <tr class='fw-bold'>
          <td>${item.name}</td>
          <td>${input_volume}</td>
          <td>${input_total}</td>
        </tr>`;
    }
    receipt_table_html += `
      <tr class='fw-bold text-danger'>
        <td colspan="3" class='text-end'>Total</td>
        <td>${total_cost.toFixed(4)}</td>
      </tr>`;

    $("#receipt_table").html(receipt_table_html);
  };

  delete_input_group = (group) => {
    group.parentNode.remove();
    construct_table_rows();
  };

  const item_select_options_html = Array.from(items)
    .map((item) => `<option value='${item.id}'>${item.name}</option>`)
    .join("");
  $(".order-item-select").html(item_select_options_html);

  const add_new = () => {
    const input_group = `
      <div class="input-group my-2">
        <select class="order-item-select form-select mx-2" aria-label="Item name">
         ${item_select_options_html}
        </select>
        <input value="" type="number" min='0' class="volume-input form-control mx-2" placeholder="Volume" aria-label="Volume"/>
        <input value="" type="number" min='0' class="total-input form-control mx-2" placeholder="Total" aria-label="Total"/>
        <button onclick='delete_input_group(this)' class='mx-2 btn btn-outline-danger rounded-pill'><i class="fas fa-trash"></i></button>
      </div>`;
    $("#orders_list").append(input_group);
    $(".order-item-select").change((_) => {
      construct_table_rows();
    });
    $(".volume-input").on("input", () => construct_table_rows());
    $(".total-input").on("input", () => construct_table_rows());
    construct_table_rows();
  };
  add_new();

  // On add item
  $("#add_new").click(add_new);
}

// Get Items
$(document).ready(async () => {
  const items = await (async () => {
    let response = await fetch(GET_ITEMS_ENDPOINT);
    return await response.json();
  })();
  initialize_items_form(items);
});

function onSetCreditConfirm() {
  const credit= +$("#input_credit").val();
  document.querySelector("#confirm-set-credit .modal-body").innerHTML = `
    Do you want to set the credit to <span class="fs-5 fw-bold text-danger"> ${credit} </span>
  `;
  new bootstrap.Modal(document.getElementById("confirm-set-credit")).toggle();
}

async function onSetCredit() {
  const csrf_token = await (async () => {
    const response = await fetch(GET_CSRF_TOKEN_ENDPOINT);
    return await response.json();
  })();

  const form = {
    customer: +$("#customer_select").val(),
    credit: +$("#input_credit").val(),
  };

  console.log(window.location.href);
  await fetch("set_credit/", {
    credentials: "same-origin",
    method: "post",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrf_token,
    },
    body: JSON.stringify(form),
  });
  window.location.reload();
}

async function onInvoiceSubmit() {
  const csrf_token = await (async () => {
    const response = await fetch(GET_CSRF_TOKEN_ENDPOINT);
    return await response.json();
  })();

  const purchases = [];
  for (let input_group of Array.from($("#orders_list").children())) {
    const item_id = +input_group.children[0].value;
    const input_volume = +input_group.children[1].value;
    const input_total = +input_group.children[2].value;
    purchases.push({ item: item_id, volume: input_volume, total: input_total });
  }
  const form = {
    customer: +$("#customer_select").val(),
    purchases: purchases,
  };

  await fetch(window.location.href, {
    credentials: "same-origin",
    method: "post",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrf_token,
    },
    body: JSON.stringify(form),
  });
  window.location.reload();
}
