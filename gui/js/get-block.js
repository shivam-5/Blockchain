window.blockIndex = 0; //0 - most recent, -1 = current block -1, -2 = current block -2, etc...

/**
 * Render the current block on page load.
 */
$(document).ready(function () {
  getBlock();
});

/**
 * Fetches a block, all of its information, and transactions from the blockchain.
 * Executed on page load, or on the press of the "Next" and "Prev" buttons.
 * Renders the transactions and block information on the screen if in valid range.
 */
function getBlock() {
  $.ajax({
    type: "GET",
    data: { blockIndex: window.blockIndex },
    dataType: "json",
    url: "http://localhost:" + window.apiPort + "/get-block",
    success: function (response) {
      if (response.status_code == 404) {
        console.log("You're at the genesis block!");
        window.blockIndex += 1;
      } else {
        block = JSON.parse(response.block.replaceAll(/},( |\n)*\]/gi, "}]"));
        $("#explorer-block-number").html(block.block_number);
        $("#explorer-block-id").html(block.id);
        $("#explorer-block-previous-digest").html(block.previous_digest);
        block_timestamp = new Date(Math.trunc(block.timestamp) * 1000);
        $("#explorer-block-date-time").html(
          `${block_timestamp.getDate()}/${
            block_timestamp.getMonth() + 1
          }/${block_timestamp.getFullYear()} ${block_timestamp.getHours()}:${block_timestamp.getMinutes()}:${block_timestamp.getSeconds()}`
        );
        if (window.blockIndex == 0) {
          $("#explorer-block-number").append(" (Latest)");
        }

        console.log(block);
        transactions = block.transactions;
        console.log(transactions);
        $("#block-explorer-table-body").html("");

        for (transaction in transactions) {
          transaction = transactions[transaction];
          timestamp = new Date(Math.trunc(transaction.timestamp) * 1000);

          if (transaction.transaction_type == "DISTRIBUTOR") {
            midway = Math.round(transaction.origin_node.length / 2);
            origin_node = transaction.origin_node.substr(0, midway) + "<wbr>" + transaction.origin_node.substr(midway + 1, transaction.origin_node.length);
          }
          $("#block-explorer-table-body").append(`
              <tr>
                <th scope="row">${transaction.transaction_type == "DISTRIBUTOR" ? transaction.shipment_id : "N/A"}</th>
                <td>${transaction.transaction_type == "DISTRIBUTOR" ? origin_node : transaction.client}</td>
                <td>${transaction.transaction_type == "DISTRIBUTOR" ? transaction.src_location : "N/A"}</td>
                <td>${transaction.dest_location}</td>
                <td>${transaction.qty}</td>
                <td>${transaction.distributor}</td>
                <td>${transaction.transaction_type}</td>
                <td>${timestamp.getDate()}/${timestamp.getMonth() + 1}/${timestamp.getFullYear()} ${timestamp.getHours()}:${timestamp.getMinutes()}:${timestamp.getSeconds()}</td>
              </tr>
            `);
        }
        if (transactions.length == 0) {
          $("#block-explorer-table").addClass("d-none");
          //$("#no-pending-transactions").removeClass("d-none");
        } else {
          $("#block-explorer-table").removeClass("d-none");
          // $("#no-pending-transactions").addClass("d-none");
        }
      }
    },
    error: function () {
      console.log("Request failed. Check that the node is online and try again.");
    },
  });
}

$("#explorer-prev-btn").click(function () {
  window.blockIndex -= 1;
  getBlock();
});

$("#explorer-next-btn").click(function () {
  if (window.blockIndex < 0) {
    window.blockIndex += 1;
    getBlock();
  }
});
