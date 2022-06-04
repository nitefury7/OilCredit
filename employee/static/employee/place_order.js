"use strict";
let delete_input_group;

const GET_CUSTOMERS_ENDPOINT = "/employee/get_customers";
const GET_ITEMS_ENDPOINT = "/employee/get_items";
const GET_CSRF_TOKEN_ENDPOINT = "/get_csrf_token";

// Get customer list
$(document).ready(async () => {
  let users = await (async () => {
    let response = await fetch(GET_CUSTOMERS_ENDPOINT);
    return await response.json();
  })();

  let user_select_options_html = "";
  for (let user of users) {
    user_select_options_html += `<option value='${user.id}'>${user.username}</option>`;
  }
  $("#customer_select").html(user_select_options_html);
  $("#customer_select").select2({
    theme: "bootstrap-5",
    width: "80%",
  });

  // On change customer
  const onChangeCustomer = async () => {
    let id = $("#customer_select").val();
    let response = await fetch(`get_customer_profile/${id}`);
    let user_info = await response.json();

    let html = `
        <tbody>
            <tr> <th>Username</th> <td>${user_info.username}</td> </tr>
            <tr> <th>Account Number</th> <td>${user_info.id}</td> </tr>
            <tr> <th>First Name</th> <td>${user_info.first_name}</td> </tr>
            <tr> <th>Last Name</th> <td>${user_info.last_name}</td> </tr>
            <tr> <th>Contact</th> <td>${user_info.contact}</td> </tr>
            <tr> <th>Email</th> <td>${user_info.email}</td> </tr>
        </tbody>
      `;
    $("#customer_profile").html(html);
    $("#customer_profile_card").removeClass("d-none");
  };
  $("#customer_select").on("change", onChangeCustomer);
  onChangeCustomer();
});

// Get Items
$(document).ready(async () => {
  const items = await (async () => {
    let response = await fetch(GET_ITEMS_ENDPOINT);
    return await response.json();
  })();

  let item_select_options_html = "";
  for (let item of items) {
    item_select_options_html += `<option value='${item.id}'>${item.name}</option>`;
  }
  $(".order-item-select").html(item_select_options_html);

  const construct_table_rows = () => {
    let total_cost = 0.0;
    let receipt_table_html = "";
    const items_map = new Map();
    for (let item of items) {
      items_map.set(item.id, item);
    }
    for (let input_group of Array.from($("#orders_list").children())) {
      const item_id = +input_group.children[0].value;
      const input_volume = +input_group.children[1].value;
      const item = items_map.get(item_id);
      const cost = item.rate * input_volume;
      total_cost += cost;
      receipt_table_html += `
        <tr class='fw-bold'>
          <td>${item.name}</td>
          <td>${item.rate.toFixed(4)}</td>
          <td>${input_volume}</td>
          <td>${cost.toFixed(4)}</td>
        </tr>`;
    }
    receipt_table_html += `
      <tr class='fw-bold text-danger'>
        <td colspan="3" class='text-end'>Total</td>
        <td>${total_cost.toFixed(4)}</td>
      </tr>`;

    $("#receipt_table").html(receipt_table_html);
  };
  construct_table_rows();
  delete_input_group = (group) => {
    group.parentNode.remove();
    construct_table_rows();
  };

  const add_new = () => {
    const input_group = `
      <div class="input-group my-2">
        <select class="order-item-select form-select mx-2" aria-label="Item name">
         ${item_select_options_html}
        </select>
        <input type="number" min='0' class="volume-input form-control mx-2" placeholder="Volume" aria-label="Volume"/>
        <button onclick='delete_input_group(this)' class='mx-2 btn btn-outline-danger rounded-pill'><i class="fas fa-trash"></i></button>
      </div>`;
    $("#orders_list").append(input_group);
    $(".order-item-select").on("change", () => construct_table_rows());
    $(".volume-input").on("input", () => construct_table_rows());
    construct_table_rows();
  };
  add_new();

  // On add item
  $("#add_new").click(add_new);
});

async function onSubmit() {
  const csrf_token = await (async () => {
    let response = await fetch(GET_CSRF_TOKEN_ENDPOINT);
    return await response.json();
  })();

  const purchases = [];
  for (let input_group of Array.from($("#orders_list").children())) {
    let item_id = +input_group.children[0].value;
    let input_volume = +input_group.children[1].value;
    purchases.push({ item: item_id, volume: input_volume });
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
