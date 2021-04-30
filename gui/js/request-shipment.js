/**
 * Triggered on submission of the "Request Shipment" form (Client Nodes)
 *
 * Submits the information to the relevant API endpoint.
 */
$("#request-shipment-form").submit(function (event) {
  event.preventDefault();

  $.ajax({
    type: "POST",
    url: "http://localhost:" + window.apiPort + "/request-shipment",
    dataType: "json",
    data: $("#request-shipment-form").serialize(),
    success: function () {
      $("#request-shipment-success").removeClass("d-none");
      $("#request-shipment-failed").addClass("d-none");
      console.log("Request successful!");
    },
    error: function () {
      $("#request-shipment-failed").removeClass("d-none");
      $("#request-shipment-success").addClass("d-none");
      console.log("Request failed. Check that the node is online and try again.");
    },
  });
});
