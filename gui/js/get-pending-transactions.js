/**
 * Triggered when the user loads the "Pending Transactions" page (Distributor)
 *
 * Retrieves transactions from the appropriate endpoint.
 * Adds all of the transactions to the pending transactions table.
 */
$.ajax({
  type: "GET",
  url: "http://localhost:" + window.apiPort + "/get-pending-transactions",
  success: function (response) {
    pending_transactions = response.pending_transactions;
    for (transaction in pending_transactions) {
      console.log(pending_transactions[transaction]);
      transaction = JSON.parse(pending_transactions[transaction]);
      timestamp = new Date(Math.trunc(transaction.timestamp) * 1000);

      if (transaction.transaction_type == "DISTRIBUTOR") {
        midway = Math.round(transaction.origin_node.length / 2);
        origin_node = transaction.origin_node.substr(0, midway) + "<wbr>" + transaction.origin_node.substr(midway + 1, transaction.origin_node.length);
      }
      $("#pending-transactions-table-body").append(`
          <tr>
            <th scope="row">${transaction.transaction_type == "DISTRIBUTOR" ? transaction.shipment_id : "N/A"}</th>
            <td>${transaction.transaction_type == "DISTRIBUTOR" ? origin_node : transaction.client}</td>
            <td>${transaction.transaction_type == "DISTRIBUTOR" ? transaction.src_location : "N/A"}</td>
            <td>${transaction.dest_location}</td>
            <td>${transaction.qty}</td>
            <td>${transaction.distributor}</td>
            <td>${timestamp.getDate()}/${timestamp.getMonth() + 1}/${timestamp.getFullYear()} ${timestamp.getHours()}:${timestamp.getMinutes()}:${timestamp.getSeconds()}</td>
          </tr>
        `);
    }
    if (pending_transactions.length == 0) {
      $("#pending-transactions-table").addClass("d-none");
      $("#no-pending-transactions").removeClass("d-none");
    } else {
      $("#pending-transactions-table").removeClass("d-none");
      $("#no-pending-transactions").addClass("d-none");
    }
  },
  error: function () {
    console.log("Request failed. Check that the node is online and try again.");
  },
});
