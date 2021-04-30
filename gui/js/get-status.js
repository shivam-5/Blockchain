/**
 * Periodically check the status of the node every 10 seconds.
 * Show red icon and appropriate information if the node is offline. Green if all okay.
 * Adapts the UI based on whether the node is a Client or Distributor.
 */
let statusCheck = window.setInterval(
  (function getStatus() {
    $.ajax({
      type: "GET",
      url: "http://localhost:" + window.apiPort + "/get-node-info",
      success: function (response) {
        $("#status-indicator").attr("style", "color: green !important");
        $(".node-status-block").removeClass("d-none");
        $("#node-status-error").addClass("d-none");
        $("#node-id").html(response.node_id);
        $("#distributor-client").html("<strong>" + (response.node_type == "CLIENT" ? "Client: " : "Distributor: ") + "</strong>" + response.distributor_client);
        $("#distributor-client-index").html((response.node_type == "CLIENT" ? "Client: " : "Distributor: ") + response.distributor_client);
        $("#node-id-index").html(response.node_id);
        $("#node-type").html(response.node_type);
        $("#node-type-index").html(response.node_type);
        $("#node-status-index-error").addClass("d-none");
        $("#node-status-index").removeClass("d-none");
        if (response.node_type == "CLIENT") {
          $(".client-nav").removeClass("d-none");
          $(".distributor-nav").addClass("d-none");
        } else {
          $(".client-nav").addClass("d-none");
          $(".distributor-nav").removeClass("d-none");
        }
      },
      error: function () {
        $("#status-indicator").attr("style", "color: red !important");
        $(".node-status-block").addClass("d-none");
        $("#node-status-error").removeClass("d-none");
        $("#node-id").html("");
        $("#node-status-index").addClass("d-none");
        $("#node-status-index-error").removeClass("d-none");
      },
    });
  })(),
  10000
);
