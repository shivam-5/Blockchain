from blockchain import Blockchain


class Consensus:
    """
    Singleton class - Can only be one instance of the consensus protocol per node.
    Evaluates and stores the consensus power of every node on the network.

    """

    single_instance = None

    def __init__(self, node_name):
        print("Initialising consensus mechanism...\n")
        self.node_name = node_name
        self.consensus_power = {}
        self.aggregate_consensus_power()

    # STATIC - Fetch and return the single instance of the consensus, or if it doesn't already exist, instantiate it.
    @staticmethod
    def instance(node_name):
        if Consensus.single_instance == None:
            Consensus.single_instance = Consensus(node_name)
        return Consensus.single_instance

    # Collects the qty each node has in circulation and stores it in a dictionary.
    def aggregate_consensus_power(self):
        blockchain = Blockchain.instance().get_blockchain()
        for block in blockchain:
            for transaction in block.get_transactions():
                if transaction.get_transaction_type() == 'DISTRIBUTOR':
                    distributor = transaction.get_distributor().upper()
                    qty = transaction.get_qty()
                    if distributor not in self.consensus_power:
                        self.consensus_power[distributor] = 0
                    self.consensus_power[distributor] = qty
                else:
                    distributor = transaction.get_requested_distributor().upper()
                    client = transaction.get_requesting_client().upper()
                    qty = transaction.get_qty()
                    if distributor == self.node_name.upper():
                        self.consensus_power[client] = qty

    # Fetch and return the consensus power of all nodes.
    def get_consensus_power(self):
        return self.consensus_power

