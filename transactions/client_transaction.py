

class ClientTransaction():
    """
    Manage the client transactions in the blockchain.

    """

    def __init__(self, client, dest_location, qty, distributor, transaction_type, timestamp):
        self.transaction_type = transaction_type    # Type of transaction : client/distributor
        self.client = client    # Name of client node
        self.dest_location = dest_location  # Destination location for the requested shipment
        self.qty = qty  # Quantity of vaccines in requested shipment
        self.distributor = distributor  # Name of distributor of requested vaccine shipment
        self.timestamp = timestamp  # Timestamp of the transaction

    # Display the transaction nicely when printed.
    def __str__(self):
        transaction_string = f"""
                {{"client": "{self.client}", "dest_location": "{self.dest_location}", "qty": {self.qty}, "distributor": "{self.distributor}",
                  "transaction_type": "{self.transaction_type}", "timestamp": "{self.timestamp}"}},"""
        return transaction_string

    def get_transaction_type(self):
        return self.transaction_type

    def get_requested_distributor(self):
        return self.distributor

    def get_requesting_client(self):
        return self.client

    def get_qty(self):
        return self.qty
