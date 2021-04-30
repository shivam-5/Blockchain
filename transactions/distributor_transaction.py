class DistributorTransaction:
    """
    Manage the distributor transactions in the blockchain.

    """

    def __init__(self, shipment_id, origin_node, src_location, dest_location, qty, distributor, transaction_type,
                 timestamp):
        self.transaction_type = transaction_type    # Type of transaction : client/distributor
        self.shipment_id = shipment_id  # Id of the shipment
        self.origin_node = origin_node  # Starting node that created the shipment
        self.src_location = src_location    # Source location for the shipment
        self.dest_location = dest_location  # Destination location for the shipment
        self.qty = qty  # Quantity of vaccines in shipment
        self.distributor = distributor  # Name of distributor
        self.timestamp = timestamp  # Timestamp of the transaction

    # Display the transaction nicely when printed.
    def __str__(self):
        transaction_string = f"""
                {{"shipment_id": "{self.shipment_id}", "origin_node": "{self.origin_node}",
                 "src_location": "{self.src_location}", "dest_location": "{self.dest_location}",
                  "qty": {self.qty}, "distributor": "{self.distributor}", 
                  "transaction_type": "{self.transaction_type}", "timestamp": "{self.timestamp}"}},"""
        return transaction_string

    def get_transaction_type(self):
        return self.transaction_type

    def get_origin_node(self):
        return self.origin_node

    def get_distributor(self):
        return self.distributor

    def get_qty(self):
        return self.qty
