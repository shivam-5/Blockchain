/**
 * Triggered on submission of the "Add Shipment" form (Distributor Nodes)
 *
 * Submits the information to the relevant API endpoint.
 */
$("#add-shipment-form").submit(function (event) {
  event.preventDefault();

  $.ajax({
    type: "POST",
    url: "http://localhost:" + window.apiPort + "/add-shipment",
    dataType: "json",
    data: $("#add-shipment-form").serialize(),
    success: function () {
      $("#add-shipment-success").removeClass("d-none");
      $("#add-shipment-failed").addClass("d-none");
      console.log("Request successful!");
    },
    error: function () {
      $("#add-shipment-failed").removeClass("d-none");
      $("#add-shipment-success").addClass("d-none");
      console.log("Request failed. Check that the node is online and try again.");
    },
  });
});
